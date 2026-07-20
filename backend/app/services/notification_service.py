import uuid

from app.models.enums import NotificationType, OrderStatus
from app.models.notification import Notification
from app.repositories.notification_repository import NotificationRepository

_ORDER_STATUS_MESSAGES: dict[OrderStatus, tuple[str, str]] = {
    OrderStatus.ACCEPTED: ("Order accepted", "The kitchen has accepted your order and will start preparing it soon."),
    OrderStatus.PREPARING: ("Order is being prepared", "Your order is now being prepared in the kitchen."),
    OrderStatus.READY: ("Order ready", "Your order is ready and waiting for a delivery partner."),
    OrderStatus.ASSIGNED: ("Delivery partner assigned", "A delivery partner has been assigned to your order."),
    OrderStatus.PICKED_UP: ("Order picked up", "Your order has been picked up and is on its way to you."),
    OrderStatus.ON_THE_WAY: ("Order on the way", "Your delivery partner is on the way with your order."),
    OrderStatus.DELIVERED: ("Order delivered", "Enjoy your meal! Your order has been delivered."),
    OrderStatus.CANCELLED: ("Order cancelled", "Your order has been cancelled."),
    OrderStatus.REFUNDED: ("Order refunded", "Your order has been refunded."),
}


class NotificationService:
    def __init__(self, notification_repo: NotificationRepository):
        self.notification_repo = notification_repo

    async def notify(
        self, user_id: uuid.UUID, title: str, message: str, notification_type: NotificationType = NotificationType.SYSTEM
    ) -> Notification:
        notification = Notification(
            id=uuid.uuid4(), user_id=user_id, title=title, message=message, type=notification_type
        )
        return await self.notification_repo.create(notification)

    async def notify_order_status(self, user_id: uuid.UUID, order_number: str, status: OrderStatus) -> Notification | None:
        entry = _ORDER_STATUS_MESSAGES.get(status)
        if entry is None:
            return None
        title, message = entry
        return await self.notify(
            user_id, title, f"{message} (Order {order_number})", NotificationType.ORDER_UPDATE
        )
