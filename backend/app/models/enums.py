import enum


class RoleName(str, enum.Enum):
    CUSTOMER = "customer"
    ADMIN = "admin"
    KITCHEN = "kitchen"
    DELIVERY = "delivery"


class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    PREPARING = "preparing"
    READY = "ready"
    ASSIGNED = "assigned"
    PICKED_UP = "picked_up"
    ON_THE_WAY = "on_the_way"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class PaymentStatus(str, enum.Enum):
    CREATED = "created"
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"


class PaymentMethod(str, enum.Enum):
    UPI = "upi"
    CARD = "card"
    NETBANKING = "netbanking"
    WALLET = "wallet"
    COD = "cod"


class DiscountType(str, enum.Enum):
    PERCENT = "percent"
    FLAT = "flat"


class CouponType(str, enum.Enum):
    GENERAL = "general"
    FESTIVAL = "festival"
    REFERRAL = "referral"
    MIN_ORDER = "min_order"


class NotificationType(str, enum.Enum):
    ORDER_UPDATE = "order_update"
    PROMOTION = "promotion"
    SYSTEM = "system"
