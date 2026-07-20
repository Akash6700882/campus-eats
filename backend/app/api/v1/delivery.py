import uuid

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.deps import CurrentUser, DbSession, DeliveryPartnerSvc, NotificationSvc, OrderRepo, OrderSvc, require_role
from app.models.enums import RoleName
from app.schemas.delivery import (
    DeliverOrderRequest,
    DeliveryLocationUpdateRequest,
    DeliveryPartnerResponse,
)
from app.schemas.order import OrderResponse
from app.services.delivery_service import DeliveryError
from app.services.order_service import DELIVERY_ACTIVE_STATUSES, OrderError
from app.ws.events import broadcast_order_event

router = APIRouter(prefix="/delivery", tags=["delivery"])

RequireDelivery = Depends(require_role(RoleName.DELIVERY.value))


async def _reload(order_id: uuid.UUID, order_repo: OrderRepo) -> OrderResponse:
    order = await order_repo.get_with_details(order_id)
    return OrderResponse.from_order(order, reveal_otp=False)


@router.get("/me", response_model=DeliveryPartnerResponse, dependencies=[RequireDelivery])
async def get_my_profile(current_user: CurrentUser, delivery_service: DeliveryPartnerSvc) -> DeliveryPartnerResponse:
    try:
        partner = await delivery_service.get_self(current_user.id)
    except DeliveryError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc
    return DeliveryPartnerResponse.from_partner(partner)


@router.patch("/me/location", response_model=DeliveryPartnerResponse, dependencies=[RequireDelivery])
async def update_my_location(
    payload: DeliveryLocationUpdateRequest,
    current_user: CurrentUser,
    db: DbSession,
    delivery_service: DeliveryPartnerSvc,
) -> DeliveryPartnerResponse:
    try:
        partner = await delivery_service.update_self(
            current_user.id, payload.latitude, payload.longitude, payload.is_available
        )
        await db.commit()
    except DeliveryError as exc:
        await db.rollback()
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc
    return DeliveryPartnerResponse.from_partner(partner)


@router.get("/orders", response_model=list[OrderResponse], dependencies=[RequireDelivery])
async def list_my_orders(
    current_user: CurrentUser, order_repo: OrderRepo, delivery_service: DeliveryPartnerSvc
) -> list[OrderResponse]:
    try:
        partner = await delivery_service.get_self(current_user.id)
    except DeliveryError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc
    orders = await order_repo.list_for_delivery_partner(partner.id, DELIVERY_ACTIVE_STATUSES)
    return [OrderResponse.from_order(o, reveal_otp=False) for o in orders]


async def _my_partner_id(current_user: CurrentUser, delivery_service: DeliveryPartnerSvc) -> uuid.UUID:
    try:
        partner = await delivery_service.get_self(current_user.id)
    except DeliveryError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc
    return partner.id


@router.post("/orders/{order_id}/pickup", response_model=OrderResponse, dependencies=[RequireDelivery])
async def pickup_order(
    order_id: uuid.UUID,
    current_user: CurrentUser,
    db: DbSession,
    order_service: OrderSvc,
    order_repo: OrderRepo,
    delivery_service: DeliveryPartnerSvc,
    notification_service: NotificationSvc,
) -> OrderResponse:
    partner_id = await _my_partner_id(current_user, delivery_service)
    try:
        order = await order_service.delivery_pickup(order_id, partner_id)
        await notification_service.notify_order_status(order.user_id, order.order_number, order.status)
        await db.commit()
    except OrderError as exc:
        await db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, str(exc)) from exc
    await broadcast_order_event(order, "order.picked_up")
    return await _reload(order_id, order_repo)


@router.post("/orders/{order_id}/on-the-way", response_model=OrderResponse, dependencies=[RequireDelivery])
async def start_transit(
    order_id: uuid.UUID,
    current_user: CurrentUser,
    db: DbSession,
    order_service: OrderSvc,
    order_repo: OrderRepo,
    delivery_service: DeliveryPartnerSvc,
    notification_service: NotificationSvc,
) -> OrderResponse:
    partner_id = await _my_partner_id(current_user, delivery_service)
    try:
        order = await order_service.delivery_start_transit(order_id, partner_id)
        await notification_service.notify_order_status(order.user_id, order.order_number, order.status)
        await db.commit()
    except OrderError as exc:
        await db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, str(exc)) from exc
    await broadcast_order_event(order, "order.on_the_way")
    return await _reload(order_id, order_repo)


@router.post("/orders/{order_id}/deliver", response_model=OrderResponse, dependencies=[RequireDelivery])
async def deliver_order(
    order_id: uuid.UUID,
    payload: DeliverOrderRequest,
    current_user: CurrentUser,
    db: DbSession,
    order_service: OrderSvc,
    order_repo: OrderRepo,
    delivery_service: DeliveryPartnerSvc,
    notification_service: NotificationSvc,
) -> OrderResponse:
    partner_id = await _my_partner_id(current_user, delivery_service)
    try:
        order = await order_service.delivery_complete(order_id, partner_id, payload.otp)
        await notification_service.notify_order_status(order.user_id, order.order_number, order.status)
        await db.commit()
    except OrderError as exc:
        await db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, str(exc)) from exc
    await broadcast_order_event(order, "order.delivered")
    return await _reload(order_id, order_repo)
