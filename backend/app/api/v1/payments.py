import uuid

from fastapi import APIRouter, HTTPException, Response, status

from app.core.deps import CurrentUser, DbSession, OrderRepo, PaymentSvc
from app.schemas.order import OrderResponse
from app.schemas.payment import PaymentInitiateResponse, PaymentResponse, PaymentVerifyRequest
from app.services.invoice_service import generate_invoice_pdf
from app.services.payment_service import PaymentError

router = APIRouter(tags=["payments"])


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
) -> PaymentResponse:
    try:
        payment = await payment_service.verify_payment(
            order_id,
            current_user.id,
            payload.razorpay_order_id,
            payload.razorpay_payment_id,
            payload.razorpay_signature,
        )
        await db.commit()
    except PaymentError as exc:
        await db.rollback()
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc
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
