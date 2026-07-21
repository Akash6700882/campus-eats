import secrets
import uuid
from datetime import datetime, timezone

from app.core.config import get_settings
from app.models.enums import OrderStatus
from app.models.order import Order, OrderItem
from app.repositories.address_repository import AddressRepository
from app.repositories.cart_repository import CartRepository
from app.repositories.delivery_partner_repository import DeliveryPartnerRepository
from app.repositories.delivery_zone_repository import DeliveryZoneRepository
from app.repositories.order_repository import OrderRepository
from app.schemas.order import CheckoutRequest
from app.services.coupon_service import CouponError, CouponService
from app.services.delivery_assignment import find_nearest_partner
from app.services.geofence import point_in_zone
from app.services.order_state_machine import (
    CUSTOMER_CANCELLABLE_STATUSES,
    InvalidTransitionError,
    assert_transition_allowed,
)

KITCHEN_QUEUE_STATUSES = [OrderStatus.PENDING, OrderStatus.ACCEPTED, OrderStatus.PREPARING, OrderStatus.READY]
DELIVERY_ACTIVE_STATUSES = [OrderStatus.ASSIGNED, OrderStatus.PICKED_UP, OrderStatus.ON_THE_WAY]
_ADMIN_CANCELLABLE_STATUSES = {
    s for s in OrderStatus if s not in (OrderStatus.DELIVERED, OrderStatus.CANCELLED, OrderStatus.REFUNDED)
}


class OrderError(Exception):
    pass


class OrderService:
    def __init__(
        self,
        cart_repo: CartRepository,
        address_repo: AddressRepository,
        order_repo: OrderRepository,
        delivery_zone_repo: DeliveryZoneRepository,
        coupon_service: CouponService,
        delivery_partner_repo: DeliveryPartnerRepository,
    ):
        self.cart_repo = cart_repo
        self.address_repo = address_repo
        self.order_repo = order_repo
        self.delivery_zone_repo = delivery_zone_repo
        self.coupon_service = coupon_service
        self.delivery_partner_repo = delivery_partner_repo

    @staticmethod
    def _generate_order_number() -> str:
        return f"CE{uuid.uuid4().hex[:10].upper()}"

    async def checkout(self, user_id: uuid.UUID, payload: CheckoutRequest) -> Order:
        cart_items = await self.cart_repo.list_for_user(user_id)
        if not cart_items:
            raise OrderError("cart is empty")

        unavailable = [ci.food.name for ci in cart_items if not ci.food.is_available]
        if unavailable:
            raise OrderError(f"these items are no longer available: {', '.join(unavailable)}")

        address = await self.address_repo.get_for_user(payload.address_id, user_id)
        if address is None:
            raise OrderError("address not found")

        zones = await self.delivery_zone_repo.list_active()
        if not zones:
            raise OrderError("no active delivery zones configured")
        in_campus = any(
            point_in_zone(address.latitude, address.longitude, zone.polygon_geojson) for zone in zones
        )
        if not in_campus:
            raise OrderError("delivery address is outside the campus delivery zone")

        item_total = round(sum(ci.food.discounted_price * ci.quantity for ci in cart_items), 2)

        coupon = None
        discount_amount = 0.0
        if payload.coupon_code:
            try:
                coupon, discount_amount = await self.coupon_service.validate_and_price(
                    payload.coupon_code, user_id, item_total
                )
            except CouponError as exc:
                raise OrderError(str(exc)) from exc

        settings = get_settings()
        delivery_charge = settings.delivery_charge
        packing_charge = settings.packing_charge
        taxable = item_total - discount_amount
        gst_amount = round(taxable * settings.gst_percent / 100, 2)
        grand_total = round(taxable + delivery_charge + packing_charge + gst_amount, 2)
        estimated_minutes = max((ci.food.prep_time_minutes for ci in cart_items), default=10) + 15

        order = Order(
            id=uuid.uuid4(),
            order_number=self._generate_order_number(),
            user_id=user_id,
            address_id=address.id,
            coupon_id=coupon.id if coupon else None,
            status=OrderStatus.PENDING,
            item_total=item_total,
            discount_amount=discount_amount,
            delivery_charge=delivery_charge,
            packing_charge=packing_charge,
            gst_amount=gst_amount,
            grand_total=grand_total,
            estimated_delivery_minutes=estimated_minutes,
            notes=payload.notes,
            placed_at=datetime.now(timezone.utc),
        )
        for ci in cart_items:
            order.items.append(
                OrderItem(
                    id=uuid.uuid4(),
                    food_id=ci.food_id,
                    food_name_snapshot=ci.food.name,
                    unit_price_snapshot=ci.food.discounted_price,
                    quantity=ci.quantity,
                    subtotal=round(ci.food.discounted_price * ci.quantity, 2),
                )
            )

        await self.order_repo.create(order)
        if coupon is not None:
            coupon.times_used += 1
        await self.cart_repo.clear_for_user(user_id)
        return order

    async def cancel_order(self, order_id: uuid.UUID, user_id: uuid.UUID) -> Order:
        order = await self.order_repo.get_for_user(order_id, user_id)
        if order is None:
            raise OrderError("order not found")
        if order.status not in CUSTOMER_CANCELLABLE_STATUSES:
            raise OrderError(f"order cannot be cancelled once it is '{order.status.value}'")

        assert_transition_allowed(order.status, OrderStatus.CANCELLED)
        order.status = OrderStatus.CANCELLED
        order.cancelled_at = datetime.now(timezone.utc)
        return order

    async def _transition(self, order_id: uuid.UUID, new_status: OrderStatus) -> Order:
        order = await self.order_repo.get_with_details(order_id)
        if order is None:
            raise OrderError("order not found")
        try:
            assert_transition_allowed(order.status, new_status)
        except InvalidTransitionError as exc:
            raise OrderError(str(exc)) from exc
        order.status = new_status
        return order

    # --- Kitchen -----------------------------------------------------------

    async def kitchen_accept(self, order_id: uuid.UUID) -> Order:
        return await self._transition(order_id, OrderStatus.ACCEPTED)

    async def kitchen_reject(self, order_id: uuid.UUID, reason: str | None = None) -> Order:
        order = await self._transition(order_id, OrderStatus.CANCELLED)
        order.cancelled_at = datetime.now(timezone.utc)
        if reason:
            order.notes = f"{order.notes + ' | ' if order.notes else ''}Rejected by kitchen: {reason}"
        return order

    async def kitchen_start_preparing(self, order_id: uuid.UUID) -> Order:
        return await self._transition(order_id, OrderStatus.PREPARING)

    async def _assign_delivery_partner_if_available(self, order: Order) -> None:
        """Generates the delivery OTP and tries to auto-assign the nearest
        available delivery partner (falls back to staying 'ready' and
        unassigned if none are free — an admin can assign manually)."""
        order.delivery_otp = f"{secrets.randbelow(1_000_000):06d}"

        partners = await self.delivery_partner_repo.list_available()
        partner = find_nearest_partner(partners, order.address.latitude, order.address.longitude)
        if partner is not None:
            order.status = OrderStatus.ASSIGNED
            order.delivery_partner = partner
            partner.is_available = False

    async def kitchen_mark_ready(self, order_id: uuid.UUID) -> Order:
        order = await self._transition(order_id, OrderStatus.READY)
        await self._assign_delivery_partner_if_available(order)
        return order

    async def auto_confirm_after_payment(self, order_id: uuid.UUID) -> Order:
        """Drives a freshly-paid order straight to 'ready' (and tries
        auto-assignment) without a human kitchen action — the live order
        flow doesn't route through kitchen confirmation. Idempotent: called
        from both the client-side verify-signature path and the webhook, so
        a non-pending order (already advanced by whichever path won the
        race) is left untouched rather than re-processed."""
        order = await self.order_repo.get_with_details(order_id)
        if order is None:
            raise OrderError("order not found")
        if order.status != OrderStatus.PENDING:
            return order

        assert_transition_allowed(order.status, OrderStatus.READY)
        order.status = OrderStatus.READY
        await self._assign_delivery_partner_if_available(order)
        return order

    # --- Delivery ------------------------------------------------------------

    async def _get_partner_order(self, order_id: uuid.UUID, partner_id: uuid.UUID) -> Order:
        order = await self.order_repo.get_with_details(order_id)
        if order is None or order.delivery_partner_id != partner_id:
            raise OrderError("order not found")
        return order

    async def delivery_pickup(self, order_id: uuid.UUID, partner_id: uuid.UUID) -> Order:
        order = await self._get_partner_order(order_id, partner_id)
        try:
            assert_transition_allowed(order.status, OrderStatus.PICKED_UP)
        except InvalidTransitionError as exc:
            raise OrderError(str(exc)) from exc
        order.status = OrderStatus.PICKED_UP
        return order

    async def delivery_start_transit(self, order_id: uuid.UUID, partner_id: uuid.UUID) -> Order:
        order = await self._get_partner_order(order_id, partner_id)
        try:
            assert_transition_allowed(order.status, OrderStatus.ON_THE_WAY)
        except InvalidTransitionError as exc:
            raise OrderError(str(exc)) from exc
        order.status = OrderStatus.ON_THE_WAY
        return order

    async def delivery_complete(self, order_id: uuid.UUID, partner_id: uuid.UUID, otp: str) -> Order:
        order = await self._get_partner_order(order_id, partner_id)
        try:
            assert_transition_allowed(order.status, OrderStatus.DELIVERED)
        except InvalidTransitionError as exc:
            raise OrderError(str(exc)) from exc
        if not order.delivery_otp or otp != order.delivery_otp:
            raise OrderError("invalid delivery OTP")

        order.status = OrderStatus.DELIVERED
        order.delivered_at = datetime.now(timezone.utc)

        partner = await self.delivery_partner_repo.get(partner_id)
        if partner is not None:
            partner.total_deliveries += 1
            partner.today_earnings = float(partner.today_earnings) + float(order.delivery_charge)
            partner.is_available = True
        return order

    # --- Admin ---------------------------------------------------------------

    async def admin_force_cancel(self, order_id: uuid.UUID, reason: str | None = None) -> Order:
        order = await self.order_repo.get_with_details(order_id)
        if order is None:
            raise OrderError("order not found")
        if order.status not in _ADMIN_CANCELLABLE_STATUSES:
            raise OrderError(f"order cannot be cancelled once it is '{order.status.value}'")

        if order.delivery_partner_id and order.status in DELIVERY_ACTIVE_STATUSES:
            partner = await self.delivery_partner_repo.get(order.delivery_partner_id)
            if partner is not None:
                partner.is_available = True

        order.status = OrderStatus.CANCELLED
        order.cancelled_at = datetime.now(timezone.utc)
        if reason:
            order.notes = f"{order.notes + ' | ' if order.notes else ''}Cancelled by admin: {reason}"
        return order

    async def admin_assign_partner(self, order_id: uuid.UUID, delivery_partner_id: uuid.UUID) -> Order:
        order = await self.order_repo.get_with_details(order_id)
        if order is None:
            raise OrderError("order not found")
        if order.status != OrderStatus.READY:
            raise OrderError("order must be 'ready' and unassigned to manually assign a delivery partner")

        partner = await self.delivery_partner_repo.get_with_user(delivery_partner_id)
        if partner is None:
            raise OrderError("delivery partner not found")
        if not partner.is_available:
            raise OrderError("delivery partner is not available")

        order.status = OrderStatus.ASSIGNED
        order.delivery_partner = partner
        partner.is_available = False
        return order
