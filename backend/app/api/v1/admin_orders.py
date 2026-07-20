import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.deps import (
    DbSession,
    DeliveryPartnerRepo,
    DeliveryPartnerSvc,
    NotificationSvc,
    OrderRepo,
    OrderSvc,
    UserRepo,
    require_role,
)
from app.models.enums import OrderStatus, RoleName
from app.schemas.delivery import (
    AdminAssignPartnerRequest,
    AdminCancelRequest,
    AdminUserResponse,
    DeliveryPartnerCreateRequest,
    DeliveryPartnerResponse,
)
from app.schemas.order import OrderResponse
from app.services.delivery_service import DeliveryError
from app.services.order_service import OrderError
from app.ws.events import broadcast_order_event

router = APIRouter(tags=["admin"])

RequireAdmin = Depends(require_role(RoleName.ADMIN.value))


async def _reload(order_id: uuid.UUID, order_repo: OrderRepo) -> OrderResponse:
    order = await order_repo.get_with_details(order_id)
    return OrderResponse.from_order(order)


@router.get("/admin/orders", response_model=list[OrderResponse], dependencies=[RequireAdmin])
async def list_all_orders(
    order_repo: OrderRepo, status_filter: OrderStatus | None = Query(default=None, alias="status")
) -> list[OrderResponse]:
    statuses = [status_filter] if status_filter else list(OrderStatus)
    orders = await order_repo.list_by_statuses(statuses, limit=200)
    return [OrderResponse.from_order(o) for o in orders]


@router.post("/admin/orders/{order_id}/cancel", response_model=OrderResponse, dependencies=[RequireAdmin])
async def force_cancel_order(
    order_id: uuid.UUID,
    payload: AdminCancelRequest,
    db: DbSession,
    order_service: OrderSvc,
    order_repo: OrderRepo,
    notification_service: NotificationSvc,
) -> OrderResponse:
    try:
        order = await order_service.admin_force_cancel(order_id, payload.reason)
        await notification_service.notify_order_status(order.user_id, order.order_number, order.status)
        await db.commit()
    except OrderError as exc:
        await db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, str(exc)) from exc
    await broadcast_order_event(order, "order.cancelled")
    return await _reload(order_id, order_repo)


@router.post("/admin/orders/{order_id}/assign", response_model=OrderResponse, dependencies=[RequireAdmin])
async def assign_delivery_partner(
    order_id: uuid.UUID,
    payload: AdminAssignPartnerRequest,
    db: DbSession,
    order_service: OrderSvc,
    order_repo: OrderRepo,
    notification_service: NotificationSvc,
) -> OrderResponse:
    try:
        order = await order_service.admin_assign_partner(order_id, payload.delivery_partner_id)
        await notification_service.notify_order_status(order.user_id, order.order_number, order.status)
        await db.commit()
    except OrderError as exc:
        await db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, str(exc)) from exc
    await broadcast_order_event(order, "order.assigned")
    return await _reload(order_id, order_repo)


@router.get("/admin/users", response_model=list[AdminUserResponse], dependencies=[RequireAdmin])
async def list_users_by_role(user_repo: UserRepo, role: RoleName = Query()) -> list[AdminUserResponse]:
    users = await user_repo.list_by_role(role.value)
    return [AdminUserResponse.from_user(u) for u in users]


@router.get(
    "/admin/delivery-partners", response_model=list[DeliveryPartnerResponse], dependencies=[RequireAdmin]
)
async def list_delivery_partners(delivery_partner_repo: DeliveryPartnerRepo) -> list[DeliveryPartnerResponse]:
    partners = await delivery_partner_repo.list_all()
    return [DeliveryPartnerResponse.from_partner(p) for p in partners]


@router.post(
    "/admin/delivery-partners",
    response_model=DeliveryPartnerResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[RequireAdmin],
)
async def create_delivery_partner(
    payload: DeliveryPartnerCreateRequest, db: DbSession, delivery_service: DeliveryPartnerSvc
) -> DeliveryPartnerResponse:
    try:
        partner = await delivery_service.create_profile(payload.user_id, payload.vehicle_number)
        await db.commit()
    except DeliveryError as exc:
        await db.rollback()
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc
    return DeliveryPartnerResponse.from_partner(partner)
