import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base
from app.models.enums import CouponType, DiscountType
from app.models.mixins import TimestampMixin


class Coupon(Base, TimestampMixin):
    __tablename__ = "coupons"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(String(30), unique=True, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(String(255))

    coupon_type: Mapped[CouponType] = mapped_column(
        Enum(CouponType, name="coupon_type"), default=CouponType.GENERAL
    )
    discount_type: Mapped[DiscountType] = mapped_column(Enum(DiscountType, name="discount_type"))
    discount_value: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    max_discount_amount: Mapped[float | None] = mapped_column(Numeric(10, 2))
    min_order_amount: Mapped[float] = mapped_column(Numeric(10, 2), default=0)

    valid_from: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    valid_to: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    usage_limit: Mapped[int | None] = mapped_column(Integer)
    per_user_limit: Mapped[int] = mapped_column(Integer, default=1)
    times_used: Mapped[int] = mapped_column(Integer, default=0)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
