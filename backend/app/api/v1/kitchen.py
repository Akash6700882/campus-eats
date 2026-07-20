import uuid

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.deps import DbSession, NotificationSvc, OrderRepo, OrderSvc, require_role
from app.models.enums import RoleName
from app.schemas.delivery import KitchenRejectRequest
from app.schemas.order import OrderResponse
from app.services.order_service import KITCHEN_QUEUE_STATUSES, OrderError
from app.ws.events import broadcast_order_event

router = APIRouter(prefix="/kitchen", tags=["kitchen"])

RequireKitchen = Depends(require_role(RoleName.KITCHEN.value, RoleName.ADMIN.value))


async def _reload(order_id: uuid.UUID, order_repo: OrderRepo) -> OrderResponse:
    order = await order_repo.get_with_details(order_id)
    return OrderResponse.from_order(order, reveal_otp=False)


@router.get("/orders", response_model=list[OrderResponse], dependencies=[RequireKitchen])
async def list_kitchen_orders(order_repo: OrderRepo) -> list[OrderResponse]:
    orders = await order_repo.list_by_statuses(KITCHEN_QUEUE_STATUSES)
    return [OrderResponse.from_order(o, reveal_otp=False) for o in orders]


@router.post("/orders/{order_id}/accept", response_model=OrderResponse, dependencies=[RequireKitchen])
async def accept_order(
    order_id: uuid.UUID, db: DbSession, order_service: OrderSvc, order_repo: OrderRepo, notification_service: NotificationSvc
) -> OrderResponse:
    try:
        order = await order_service.kitchen_accept(order_id)
        await notification_service.notify_order_status(order.user_id, order.order_number, order.status)
        await db.commit()
    except OrderError as exc:
        await db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, str(exc)) from exc
    await broadcast_order_event(order, "order.accepted")
    return await _reload(order_id, order_repo)


@router.post("/orders/{order_id}/reject", response_model=OrderResponse, dependencies=[RequireKitchen])
async def reject_order(
    order_id: uuid.UUID,
    payload: KitchenRejectRequest,
    db: DbSession,
    order_service: OrderSvc,
    order_repo: OrderRepo,
    notification_service: NotificationSvc,
) -> OrderResponse:
    try:
        order = await order_service.kitchen_reject(order_id, payload.reason)
        await notification_service.notify_order_status(order.user_id, order.order_number, order.status)
        await db.commit()
    except OrderError as exc:
        await db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, str(exc)) from exc
    await broadcast_order_event(order, "order.rejected")
    return await _reload(order_id, order_repo)


@router.post(
    "/orders/{order_id}/start-preparing", response_model=OrderResponse, dependencies=[RequireKitchen]
)
async def start_preparing(
    order_id: uuid.UUID, db: DbSession, order_service: OrderSvc, order_repo: OrderRepo, notification_service: NotificationSvc
) -> OrderResponse:
    try:
        order = await order_service.kitchen_start_preparing(order_id)
        await notification_service.notify_order_status(order.user_id, order.order_number, order.status)
        await db.commit()
    except OrderError as exc:
        await db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, str(exc)) from exc
    await broadcast_order_event(order, "order.preparing")
    return await _reload(order_id, order_repo)


@router.post("/orders/{order_id}/ready", response_model=OrderResponse, dependencies=[RequireKitchen])
async def mark_ready(
    order_id: uuid.UUID, db: DbSession, order_service: OrderSvc, order_repo: OrderRepo, notification_service: NotificationSvc
) -> OrderResponse:
    try:
        order = await order_service.kitchen_mark_ready(order_id)
        await notification_service.notify_order_status(order.user_id, order.order_number, order.status)
        await db.commit()
    except OrderError as exc:
        await db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, str(exc)) from exc
    event = "order.assigned" if order.delivery_partner_id else "order.ready"
    await broadcast_order_event(order, event)
    return await _reload(order_id, order_repo)
