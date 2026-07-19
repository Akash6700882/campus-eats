import uuid

import pytest

from app.models.enums import OrderStatus
from app.ws.events import broadcast_order_event
from app.ws.manager import ConnectionManager

pytestmark = pytest.mark.asyncio


class FakeWebSocket:
    def __init__(self, fail: bool = False):
        self.fail = fail
        self.accepted = False
        self.messages: list[dict] = []

    async def accept(self) -> None:
        self.accepted = True

    async def send_json(self, message: dict) -> None:
        if self.fail:
            raise RuntimeError("connection closed")
        self.messages.append(message)


async def test_connect_accepts_and_registers():
    manager = ConnectionManager()
    ws = FakeWebSocket()

    await manager.connect("order:1", ws)

    assert ws.accepted is True
    assert ws in manager._channels["order:1"]


async def test_broadcast_delivers_to_all_subscribers_on_channel():
    manager = ConnectionManager()
    ws1, ws2, other_channel_ws = FakeWebSocket(), FakeWebSocket(), FakeWebSocket()
    await manager.connect("kitchen", ws1)
    await manager.connect("kitchen", ws2)
    await manager.connect("order:1", other_channel_ws)

    await manager.broadcast("kitchen", {"event": "order.ready"})

    assert ws1.messages == [{"event": "order.ready"}]
    assert ws2.messages == [{"event": "order.ready"}]
    assert other_channel_ws.messages == []


async def test_disconnect_removes_subscriber_and_empty_channel():
    manager = ConnectionManager()
    ws = FakeWebSocket()
    await manager.connect("order:1", ws)

    manager.disconnect("order:1", ws)

    assert "order:1" not in manager._channels


async def test_broadcast_prunes_dead_connections():
    manager = ConnectionManager()
    dead, alive = FakeWebSocket(fail=True), FakeWebSocket()
    await manager.connect("kitchen", dead)
    await manager.connect("kitchen", alive)

    await manager.broadcast("kitchen", {"event": "order.ready"})

    assert dead not in manager._channels["kitchen"]
    assert alive.messages == [{"event": "order.ready"}]


class _FakeUser:
    def __init__(self, full_name: str, phone: str):
        self.full_name = full_name
        self.phone = phone


class _FakePartner:
    def __init__(self, id_: uuid.UUID):
        self.id = id_
        self.user = _FakeUser("Test Partner", "9000000001")


class _FakeOrder:
    def __init__(self, status: OrderStatus, delivery_partner_id: uuid.UUID | None = None):
        self.id = uuid.uuid4()
        self.order_number = "CETEST1234"
        self.status = status
        self.delivery_partner_id = delivery_partner_id


async def test_broadcast_order_event_reaches_order_and_kitchen_channels():
    from app.ws import manager as manager_module

    order = _FakeOrder(OrderStatus.ACCEPTED)
    order_ws, kitchen_ws = FakeWebSocket(), FakeWebSocket()
    await manager_module.manager.connect(f"order:{order.id}", order_ws)
    await manager_module.manager.connect("kitchen", kitchen_ws)

    try:
        await broadcast_order_event(order, "order.accepted")

        assert order_ws.messages[0]["event"] == "order.accepted"
        assert order_ws.messages[0]["status"] == "accepted"
        assert kitchen_ws.messages[0]["order_number"] == "CETEST1234"
    finally:
        manager_module.manager.disconnect(f"order:{order.id}", order_ws)
        manager_module.manager.disconnect("kitchen", kitchen_ws)


async def test_broadcast_order_event_reaches_assigned_delivery_partner_channel():
    from app.ws import manager as manager_module

    partner_id = uuid.uuid4()
    order = _FakeOrder(OrderStatus.ASSIGNED, delivery_partner_id=partner_id)
    delivery_ws = FakeWebSocket()
    await manager_module.manager.connect(f"delivery:{partner_id}", delivery_ws)

    try:
        await broadcast_order_event(order, "order.assigned")
        assert delivery_ws.messages[0]["event"] == "order.assigned"
    finally:
        manager_module.manager.disconnect(f"delivery:{partner_id}", delivery_ws)
