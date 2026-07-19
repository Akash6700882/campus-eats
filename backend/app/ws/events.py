from datetime import datetime, timezone

from app.models.order import Order
from app.ws.manager import manager


async def broadcast_order_event(order: Order, event: str) -> None:
    payload = {
        "event": event,
        "order_id": str(order.id),
        "order_number": order.order_number,
        "status": order.status.value,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    await manager.broadcast(f"order:{order.id}", payload)
    await manager.broadcast("kitchen", payload)
    if order.delivery_partner_id:
        await manager.broadcast(f"delivery:{order.delivery_partner_id}", payload)
