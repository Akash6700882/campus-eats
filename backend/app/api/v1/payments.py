import json
import uuid

from fastapi import APIRouter, HTTPException, Request, Response, status

from app.core.deps import CurrentUser, DbSession, NotificationSvc, OrderRepo, OrderSvc, PaymentSvc
from app.models.enums import PaymentStatus
from app.schemas.order import OrderResponse
from app.schemas.payment import PaymentInitiateResponse, PaymentResponse, PaymentVerifyRequest
from app.services.invoice_service import generate_invoice_pdf
from app.services.order_service import OrderError
from app.services.payment_service import PaymentError
from app.ws.events import broadcast_order_event

router = APIRouter(tags=["payments"])


async def _auto_confirm_and_notify(order_id: uuid.UUID, order_service: OrderSvc, notification_service: NotificationSvc):
    """Shared by the client-side verify path and the webhook: advances a
    freshly-paid order straight past kitchen confirmation and records the
    customer notification. Caller commits, then broadcasts the returned
    event over the order's WebSocket — same order as every other router."""
    order = await order_service.auto_confirm_after_payment(order_id)
    await notification_service.notify_order_status(order.user_id, order.order_number, order.status)
    event = "order.assigned" if order.delivery_partner_id else "order.ready"
    return order, event


@router.post(
    "/orders/{order_id}/payment/initiate",
    response_model=PaymentInitiateResponse,
    status_code=status.HTTP_201_CREATED,
)
async def initiate_payment(
    order_id: uuid.UUID, current_user: CurrentUser, db: DbSession, payment_service: PaymentSvc
) -> PaymentInitiateResponse:
    try:
        payment, razorpay_order = await payment_service.initiate_payment(order_id, current_user.id)
        await db.commit()
    except PaymentError as exc:
        await db.rollback()
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, str(exc)) from exc
    return PaymentInitiateResponse.build(payment.id, razorpay_order, float(payment.amount))


@router.post("/orders/{order_id}/payment/verify", response_model=PaymentResponse)
async def verify_payment(
    order_id: uuid.UUID,
    payload: PaymentVerifyRequest,
    current_user: CurrentUser,
    db: DbSession,
    payment_service: PaymentSvc,
    order_service: OrderSvc,
    notification_service: NotificationSvc,
) -> PaymentResponse:
    try:
        payment = await payment_service.verify_payment(
            order_id,
            current_user.id,
            payload.razorpay_order_id,
            payload.razorpay_payment_id,
            payload.razorpay_signature,
        )
        order, event = await _auto_confirm_and_notify(order_id, order_service, notification_service)
        await db.commit()
    except (PaymentError, OrderError) as exc:
        await db.rollback()
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc
    await broadcast_order_event(order, event)
    return PaymentResponse.model_validate(payment)


@router.post("/orders/{order_id}/payment/cancel", response_model=OrderResponse)
async def cancel_unpaid_order(
    order_id: uuid.UUID,
    current_user: CurrentUser,
    db: DbSession,
    payment_service: PaymentSvc,
    order_repo: OrderRepo,
) -> OrderResponse:
    try:
        await payment_service.cancel_unpaid_order(order_id, current_user.id)
        await db.commit()
    except PaymentError as exc:
        await db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, str(exc)) from exc

    full_order = await order_repo.get_for_user(order_id, current_user.id)
    return OrderResponse.from_order(full_order)


@router.post("/payments/webhook")
async def razorpay_webhook(
    request: Request,
    db: DbSession,
    payment_service: PaymentSvc,
    order_service: OrderSvc,
    notification_service: NotificationSvc,
) -> dict[str, str]:
    """Server-side fallback for payment confirmation — configure this URL in
    the Razorpay dashboard's webhook settings, subscribed to at least
    `payment.captured` (or `order.paid`) and `payment.failed`."""
    body = await request.body()
    signature = request.headers.get("X-Razorpay-Signature", "")

    try:
        valid = payment_service.verify_webhook_signature(body, signature)
    except PaymentError as exc:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, str(exc)) from exc
    if not valid:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "invalid webhook signature")

    raw_event = json.loads(body)
    payment_entity = raw_event.get("payload", {}).get("payment", {}).get("entity", {})
    payment = await payment_service.handle_webhook_event(raw_event.get("event", ""), payment_entity)

    order, event = None, None
    if payment is not None and payment.status == PaymentStatus.PAID:
        try:
            order, event = await _auto_confirm_and_notify(payment.order_id, order_service, notification_service)
        except OrderError:
            pass  # payment reconciliation above still succeeded; Razorpay will retry this event regardless
    await db.commit()
    if order is not None:
        await broadcast_order_event(order, event)
    return {"status": "ok"}


@router.get("/orders/{order_id}/invoice")
async def get_invoice(order_id: uuid.UUID, current_user: CurrentUser, order_repo: OrderRepo) -> Response:
    order = await order_repo.get_for_user(order_id, current_user.id)
    if order is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Order not found")

    pdf_bytes = generate_invoice_pdf(order)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{order.order_number}.pdf"'},
    )
