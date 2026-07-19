import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import CouponType, DiscountType


class CouponCreateRequest(BaseModel):
    code: str = Field(min_length=3, max_length=30)
    description: str | None = None
    coupon_type: CouponType = CouponType.GENERAL
    discount_type: DiscountType
    discount_value: float = Field(gt=0)
    max_discount_amount: float | None = Field(default=None, gt=0)
    min_order_amount: float = Field(default=0, ge=0)
    valid_from: datetime
    valid_to: datetime
    usage_limit: int | None = Field(default=None, gt=0)
    per_user_limit: int = Field(default=1, gt=0)


class CouponUpdateRequest(BaseModel):
    description: str | None = None
    is_active: bool | None = None
    valid_to: datetime | None = None
    usage_limit: int | None = Field(default=None, gt=0)


class CouponResponse(BaseModel):
    id: uuid.UUID
    code: str
    description: str | None
    coupon_type: CouponType
    discount_type: DiscountType
    discount_value: float
    max_discount_amount: float | None
    min_order_amount: float
    valid_from: datetime
    valid_to: datetime
    usage_limit: int | None
    per_user_limit: int
    times_used: int
    is_active: bool

    model_config = {"from_attributes": True}
