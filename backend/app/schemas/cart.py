import uuid

from pydantic import BaseModel, Field


class CartAddItemRequest(BaseModel):
    food_id: uuid.UUID
    quantity: int = Field(default=1, ge=1, le=50)


class CartUpdateQuantityRequest(BaseModel):
    quantity: int = Field(ge=1, le=50)


class CartItemResponse(BaseModel):
    id: uuid.UUID
    food_id: uuid.UUID
    food_name: str
    unit_price: float
    quantity: int
    subtotal: float
    image_url: str | None
    is_available: bool


class CartSummaryResponse(BaseModel):
    items: list[CartItemResponse]
    item_total: float
    discount_amount: float
    delivery_charge: float
    packing_charge: float
    gst_amount: float
    grand_total: float
    estimated_delivery_minutes: int
    coupon_code: str | None = None
    coupon_error: str | None = None
