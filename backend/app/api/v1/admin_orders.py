import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.deps import (
    AdminUserSvc,
    AuditLogSvc,
    CurrentUser,
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
from app.schemas.admin_user import AdminCustomerResponse
from app.schemas.delivery import (
    AdminAssignPartnerRequest,
    AdminCancelRequest,
    AdminUserResponse,
    DeliveryPartnerCreateRequest,
    DeliveryPartnerResponse,
)
from app.schemas.order import OrderResponse
from app.services.admin_user_service import AdminUserError
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
    order_repo: OrderRepo,
    status_filter: OrderStatus | None = Query(default=None, alias="status"),
    user_id: uuid.UUID | None = Query(default=None),
) -> list[OrderResponse]:
    statuses = [status_filter] if status_filter else list(OrderStatus)
    orders = await order_repo.list_by_statuses(statuses, limit=200, user_id=user_id)
    return [OrderResponse.from_order(o) for o in orders]


@router.post("/admin/orders/{order_id}/cancel", response_model=OrderResponse, dependencies=[RequireAdmin])
async def force_cancel_order(
    order_id: uuid.UUID,
    payload: AdminCancelRequest,
    current_user: CurrentUser,
    db: DbSession,
    order_service: OrderSvc,
    order_repo: OrderRepo,
    notification_service: NotificationSvc,
    audit_log_service: AuditLogSvc,
) -> OrderResponse:
    try:
        order = await order_service.admin_force_cancel(order_id, payload.reason)
        await notification_service.notify_order_status(order.user_id, order.order_number, order.status)
        await audit_log_service.record(
            current_user, "order.force_cancel", "order", str(order_id), {"reason": payload.reason}
        )
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
    current_user: CurrentUser,
    db: DbSession,
    order_service: OrderSvc,
    order_repo: OrderRepo,
    notification_service: NotificationSvc,
    audit_log_service: AuditLogSvc,
) -> OrderResponse:
    try:
        order = await order_service.admin_assign_partner(order_id, payload.delivery_partner_id)
        await notification_service.notify_order_status(order.user_id, order.order_number, order.status)
        await audit_log_service.record(
            current_user,
            "order.assign_partner",
            "order",
            str(order_id),
            {"delivery_partner_id": str(payload.delivery_partner_id)},
        )
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
    payload: DeliveryPartnerCreateRequest,
    current_user: CurrentUser,
    db: DbSession,
    delivery_service: DeliveryPartnerSvc,
    audit_log_service: AuditLogSvc,
) -> DeliveryPartnerResponse:
    try:
        partner = await delivery_service.create_profile(payload.user_id, payload.vehicle_number)
        await audit_log_service.record(
            current_user, "delivery_partner.create", "delivery_partner", str(partner.id)
        )
        await db.commit()
    except DeliveryError as exc:
        await db.rollback()
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc
    return DeliveryPartnerResponse.from_partner(partner)


@router.get("/admin/customers", response_model=list[AdminCustomerResponse], dependencies=[RequireAdmin])
async def list_customers(user_repo: UserRepo) -> list[AdminCustomerResponse]:
    rows = await user_repo.list_customers_with_order_stats()
    return [AdminCustomerResponse.from_row(*row) for row in rows]


@router.post("/admin/users/{user_id}/block", response_model=AdminUserResponse, dependencies=[RequireAdmin])
async def block_user(
    user_id: uuid.UUID,
    current_user: CurrentUser,
    db: DbSession,
    admin_user_service: AdminUserSvc,
    audit_log_service: AuditLogSvc,
) -> AdminUserResponse:
    try:
        user = await admin_user_service.set_active(current_user.id, user_id, is_active=False)
        await audit_log_service.record(current_user, "user.block", "user", str(user_id))
        await db.commit()
    except AdminUserError as exc:
        await db.rollback()
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc
    return AdminUserResponse.from_user(user)


@router.post("/admin/users/{user_id}/unblock", response_model=AdminUserResponse, dependencies=[RequireAdmin])
async def unblock_user(
    user_id: uuid.UUID,
    current_user: CurrentUser,
    db: DbSession,
    admin_user_service: AdminUserSvc,
    audit_log_service: AuditLogSvc,
) -> AdminUserResponse:
    try:
        user = await admin_user_service.set_active(current_user.id, user_id, is_active=True)
        await audit_log_service.record(current_user, "user.unblock", "user", str(user_id))
        await db.commit()
    except AdminUserError as exc:
        await db.rollback()
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc
    return AdminUserResponse.from_user(user)


@router.post(
    "/admin/users/{user_id}/reset-password", status_code=status.HTTP_204_NO_CONTENT, dependencies=[RequireAdmin]
)
async def admin_reset_user_password(
    user_id: uuid.UUID, current_user: CurrentUser, db: DbSession, admin_user_service: AdminUserSvc, audit_log_service: AuditLogSvc
) -> None:
    try:
        await admin_user_service.reset_password(user_id)
        await audit_log_service.record(current_user, "user.reset_password", "user", str(user_id))
        await db.commit()
    except AdminUserError as exc:
        await db.rollback()
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc


@router.delete("/admin/users/{user_id}", response_model=AdminUserResponse, dependencies=[RequireAdmin])
async def delete_user(
    user_id: uuid.UUID,
    current_user: CurrentUser,
    db: DbSession,
    admin_user_service: AdminUserSvc,
    audit_log_service: AuditLogSvc,
) -> AdminUserResponse:
    try:
        user = await admin_user_service.delete_user(current_user.id, user_id)
        await audit_log_service.record(current_user, "user.delete", "user", str(user_id))
        await db.commit()
    except AdminUserError as exc:
        await db.rollback()
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc
    return AdminUserResponse.from_user(user)
