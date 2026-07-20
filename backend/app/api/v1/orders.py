import uuid

from fastapi import APIRouter, HTTPException, status

from app.core.deps import CurrentUser, DbSession, NotificationSvc, OrderRepo, OrderSvc
from app.schemas.order import CheckoutRequest, OrderResponse
from app.services.order_service import OrderError
from app.ws.events import broadcast_order_event

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def checkout(
    payload: CheckoutRequest, current_user: CurrentUser, db: DbSession, order_service: OrderSvc, order_repo: OrderRepo
) -> OrderResponse:
    try:
        order = await order_service.checkout(current_user.id, payload)
        await db.commit()
    except OrderError as exc:
        await db.rollback()
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, str(exc)) from exc

    full_order = await order_repo.get_with_details(order.id)
    return OrderResponse.from_order(full_order)


@router.get("", response_model=list[OrderResponse])
async def list_orders(current_user: CurrentUser, order_repo: OrderRepo) -> list[OrderResponse]:
    orders = await order_repo.list_for_user(current_user.id)
    return [OrderResponse.from_order(o) for o in orders]


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(order_id: uuid.UUID, current_user: CurrentUser, order_repo: OrderRepo) -> OrderResponse:
    order = await order_repo.get_for_user(order_id, current_user.id)
    if order is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Order not found")
    return OrderResponse.from_order(order)


@router.post("/{order_id}/cancel", response_model=OrderResponse)
async def cancel_order(
    order_id: uuid.UUID,
    current_user: CurrentUser,
    db: DbSession,
    order_service: OrderSvc,
    order_repo: OrderRepo,
    notification_service: NotificationSvc,
) -> OrderResponse:
    try:
        order = await order_service.cancel_order(order_id, current_user.id)
        await notification_service.notify_order_status(current_user.id, order.order_number, order.status)
        await db.commit()
    except OrderError as exc:
        await db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, str(exc)) from exc

    await broadcast_order_event(order, "order.cancelled")
    full_order = await order_repo.get_for_user(order_id, current_user.id)
    return OrderResponse.from_order(full_order)
