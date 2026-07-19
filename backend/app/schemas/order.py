import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.enums import OrderStatus
from app.schemas.address import AddressResponse
from app.schemas.delivery import DeliveryPartnerBrief


class CheckoutRequest(BaseModel):
    address_id: uuid.UUID
    coupon_code: str | None = None
    notes: str | None = None


class OrderItemResponse(BaseModel):
    food_id: uuid.UUID
    food_name: str
    unit_price: float
    quantity: int
    subtotal: float


class OrderResponse(BaseModel):
    id: uuid.UUID
    order_number: str
    status: OrderStatus
    items: list[OrderItemResponse]
    item_total: float
    discount_amount: float
    delivery_charge: float
    packing_charge: float
    gst_amount: float
    grand_total: float
    estimated_delivery_minutes: int
    notes: str | None
    delivery_otp: str | None
    placed_at: datetime | None
    delivered_at: datetime | None
    cancelled_at: datetime | None
    created_at: datetime
    customer_name: str
    customer_phone: str
    address: AddressResponse
    delivery_partner: DeliveryPartnerBrief | None

    @staticmethod
    def from_order(order, reveal_otp: bool = True) -> "OrderResponse":
        return OrderResponse(
            id=order.id,
            order_number=order.order_number,
            status=order.status,
            items=[
                OrderItemResponse(
                    food_id=item.food_id,
                    food_name=item.food_name_snapshot,
                    unit_price=float(item.unit_price_snapshot),
                    quantity=item.quantity,
                    subtotal=float(item.subtotal),
                )
                for item in order.items
            ],
            item_total=float(order.item_total),
            discount_amount=float(order.discount_amount),
            delivery_charge=float(order.delivery_charge),
            packing_charge=float(order.packing_charge),
            gst_amount=float(order.gst_amount),
            grand_total=float(order.grand_total),
            estimated_delivery_minutes=order.estimated_delivery_minutes,
            notes=order.notes,
            delivery_otp=order.delivery_otp if reveal_otp else None,
            placed_at=order.placed_at,
            delivered_at=order.delivered_at,
            cancelled_at=order.cancelled_at,
            created_at=order.created_at,
            customer_name=order.user.full_name,
            customer_phone=order.user.phone,
            address=AddressResponse.model_validate(order.address),
            delivery_partner=DeliveryPartnerBrief.from_partner(order.delivery_partner)
            if order.delivery_partner
            else None,
        )
