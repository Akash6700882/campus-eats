from app.models.enums import OrderStatus

ALLOWED_TRANSITIONS: dict[OrderStatus, set[OrderStatus]] = {
    OrderStatus.PENDING: {OrderStatus.ACCEPTED, OrderStatus.CANCELLED},
    OrderStatus.ACCEPTED: {OrderStatus.PREPARING, OrderStatus.CANCELLED},
    OrderStatus.PREPARING: {OrderStatus.READY, OrderStatus.CANCELLED},
    OrderStatus.READY: {OrderStatus.ASSIGNED},
    OrderStatus.ASSIGNED: {OrderStatus.PICKED_UP},
    OrderStatus.PICKED_UP: {OrderStatus.ON_THE_WAY},
    OrderStatus.ON_THE_WAY: {OrderStatus.DELIVERED},
    OrderStatus.DELIVERED: {OrderStatus.REFUNDED},
    OrderStatus.CANCELLED: set(),
    OrderStatus.REFUNDED: set(),
}

# Statuses at which a customer may still self-cancel — once the kitchen has
# marked an order "ready" for pickup, cancellation requires staff/admin
# intervention instead (food may already be prepared).
CUSTOMER_CANCELLABLE_STATUSES = {OrderStatus.PENDING, OrderStatus.ACCEPTED, OrderStatus.PREPARING}


class InvalidTransitionError(Exception):
    pass


def assert_transition_allowed(current: OrderStatus, new: OrderStatus) -> None:
    if new not in ALLOWED_TRANSITIONS.get(current, set()):
        raise InvalidTransitionError(f"cannot transition order from '{current.value}' to '{new.value}'")
