import uuid
from datetime import datetime, timezone

from app.models.cart import CartItem
from app.models.enums import OrderStatus, PaymentStatus
from app.models.order import Order
from app.models.payment import Payment
from app.repositories.cart_repository import CartRepository
from app.repositories.food_repository import FoodRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.payment_repository import PaymentRepository
from app.services.payment_gateway import PaymentError as GatewayError
from app.services.payment_gateway import PaymentGateway

# Razorpay webhook events that indicate a payment succeeded — either can
# arrive depending on the event subscribed to in the dashboard.
_WEBHOOK_PAID_EVENTS = {"payment.captured", "order.paid"}


class PaymentError(Exception):
    pass


class PaymentService:
    def __init__(
        self,
        order_repo: OrderRepository,
        cart_repo: CartRepository,
        food_repo: FoodRepository,
        payment_repo: PaymentRepository,
        gateway: PaymentGateway,
    ):
        self.order_repo = order_repo
        self.cart_repo = cart_repo
        self.food_repo = food_repo
        self.payment_repo = payment_repo
        self.gateway = gateway

    async def initiate_payment(self, order_id: uuid.UUID, user_id: uuid.UUID) -> tuple[Payment, dict]:
        order = await self._get_payable_order(order_id, user_id)

        try:
            razorpay_order = self.gateway.create_order(float(order.grand_total), receipt=order.order_number)
        except GatewayError as exc:
            raise PaymentError(str(exc)) from exc

        payment = Payment(
            id=uuid.uuid4(),
            order_id=order.id,
            provider="razorpay",
            provider_order_id=razorpay_order["id"],
            amount=order.grand_total,
            currency="INR",
            status=PaymentStatus.CREATED,
        )
        order.payments.append(payment)
        await self.order_repo.session.flush()
        return payment, razorpay_order

    async def verify_payment(
        self,
        order_id: uuid.UUID,
        user_id: uuid.UUID,
        razorpay_order_id: str,
        razorpay_payment_id: str,
        razorpay_signature: str,
    ) -> Payment:
        order = await self.order_repo.get_for_user(order_id, user_id)
        if order is None:
            raise PaymentError("order not found")

        payment = next((p for p in order.payments if p.provider_order_id == razorpay_order_id), None)
        if payment is None:
            raise PaymentError("no matching payment attempt found for this order")
        if payment.status == PaymentStatus.PAID:
            return payment

        try:
            verified = self.gateway.verify_signature(razorpay_order_id, razorpay_payment_id, razorpay_signature)
        except GatewayError as exc:
            raise PaymentError(str(exc)) from exc

        if not verified:
            payment.status = PaymentStatus.FAILED
            payment.failure_reason = "signature verification failed"
            raise PaymentError("payment verification failed")

        payment.status = PaymentStatus.PAID
        payment.provider_payment_id = razorpay_payment_id
        payment.provider_signature = razorpay_signature
        return payment

    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        return self.gateway.verify_webhook_signature(payload, signature)

    async def handle_webhook_event(self, event_type: str, payment_entity: dict) -> Payment | None:
        """Reconciles payment status from a Razorpay webhook — the server-side
        fallback for when the client-side verify-signature call never lands
        (closed tab, dropped connection mid-payment). Idempotent: a payment
        already marked PAID is left untouched, since the client-side path
        commonly wins the race against the webhook."""
        provider_order_id = payment_entity.get("order_id")
        if not provider_order_id:
            return None

        payment = await self.payment_repo.get_by_provider_order_id(provider_order_id)
        if payment is None or payment.status == PaymentStatus.PAID:
            return payment

        if event_type in _WEBHOOK_PAID_EVENTS:
            payment.status = PaymentStatus.PAID
            payment.provider_payment_id = payment_entity.get("id")
        elif event_type == "payment.failed":
            payment.status = PaymentStatus.FAILED
            payment.failure_reason = payment_entity.get("error_description") or "payment failed"
        return payment

    async def cancel_unpaid_order(self, order_id: uuid.UUID, user_id: uuid.UUID) -> Order:
        order = await self.order_repo.get_for_user(order_id, user_id)
        if order is None:
            raise PaymentError("order not found")
        if order.status != OrderStatus.PENDING:
            raise PaymentError("order cannot be cancelled at this stage")
        if any(p.status == PaymentStatus.PAID for p in order.payments):
            raise PaymentError("order is already paid")

        order.status = OrderStatus.CANCELLED
        order.cancelled_at = datetime.now(timezone.utc)

        for item in order.items:
            food = await self.food_repo.get(item.food_id)
            if food is None or not food.is_available:
                continue
            existing = await self.cart_repo.get_for_user(user_id, item.food_id)
            if existing is not None:
                existing.quantity += item.quantity
            else:
                self.cart_repo.session.add(
                    CartItem(id=uuid.uuid4(), user_id=user_id, food_id=item.food_id, quantity=item.quantity)
                )

        return order

    async def _get_payable_order(self, order_id: uuid.UUID, user_id: uuid.UUID) -> Order:
        order = await self.order_repo.get_for_user(order_id, user_id)
        if order is None:
            raise PaymentError("order not found")
        if order.status != OrderStatus.PENDING:
            raise PaymentError("order is not awaiting payment")
        if any(p.status == PaymentStatus.PAID for p in order.payments):
            raise PaymentError("order is already paid")
        return order
