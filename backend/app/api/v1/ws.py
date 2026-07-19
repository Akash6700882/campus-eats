import uuid

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.db import get_db
from app.core.jwt import InvalidTokenError, TokenType, decode_token
from app.models.enums import RoleName
from app.models.user import User
from app.repositories.delivery_partner_repository import DeliveryPartnerRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.user_repository import UserRepository
from app.ws.manager import manager

router = APIRouter(tags=["websockets"])


async def _authenticate(websocket: WebSocket) -> User | None:
    """Browsers can't set custom headers on a WebSocket handshake, so the
    access token is passed as a query param instead of an Authorization
    header."""
    token = websocket.query_params.get("token")
    if not token:
        return None
    try:
        payload = decode_token(token, TokenType.ACCESS)
    except InvalidTokenError:
        return None

    db_gen = get_db()
    session = await anext(db_gen)
    try:
        user = await UserRepository(session).get_with_role(uuid.UUID(payload["sub"]))
    finally:
        await db_gen.aclose()
    return user if user is not None and user.is_active else None


@router.websocket("/ws/orders/{order_id}")
async def order_updates(websocket: WebSocket, order_id: uuid.UUID) -> None:
    """Live status updates for a single order — the customer tracking a
    delivery, or staff who need to watch one order."""
    user = await _authenticate(websocket)
    if user is None:
        await websocket.close(code=4401)
        return

    db_gen = get_db()
    session = await anext(db_gen)
    try:
        if user.role.name in (RoleName.ADMIN.value, RoleName.KITCHEN.value, RoleName.DELIVERY.value):
            order = await OrderRepository(session).get(order_id)
        else:
            order = await OrderRepository(session).get_for_user(order_id, user.id)
    finally:
        await db_gen.aclose()
    if order is None:
        await websocket.close(code=4404)
        return

    channel = f"order:{order_id}"
    await manager.connect(channel, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(channel, websocket)


@router.websocket("/ws/kitchen")
async def kitchen_updates(websocket: WebSocket) -> None:
    """Broadcasts every order-lifecycle event to the kitchen dashboard."""
    user = await _authenticate(websocket)
    if user is None or user.role.name not in (RoleName.KITCHEN.value, RoleName.ADMIN.value):
        await websocket.close(code=4403)
        return

    await manager.connect("kitchen", websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect("kitchen", websocket)


@router.websocket("/ws/delivery")
async def delivery_updates(websocket: WebSocket) -> None:
    """Broadcasts order events relevant to the connected delivery partner."""
    user = await _authenticate(websocket)
    if user is None or user.role.name != RoleName.DELIVERY.value:
        await websocket.close(code=4403)
        return

    db_gen = get_db()
    session = await anext(db_gen)
    try:
        partner = await DeliveryPartnerRepository(session).get_by_user_id(user.id)
    finally:
        await db_gen.aclose()
    if partner is None:
        await websocket.close(code=4404)
        return

    channel = f"delivery:{partner.id}"
    await manager.connect(channel, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(channel, websocket)
