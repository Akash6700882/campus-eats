import uuid
from datetime import datetime, timezone

from app.models.coupon import Coupon
from app.models.enums import DiscountType
from app.repositories.coupon_repository import CouponRepository
from app.repositories.order_repository import OrderRepository


class CouponError(Exception):
    pass


class CouponService:
    def __init__(self, coupon_repo: CouponRepository, order_repo: OrderRepository):
        self.coupon_repo = coupon_repo
        self.order_repo = order_repo

    async def validate_and_price(
        self, code: str, user_id: uuid.UUID, item_total: float
    ) -> tuple[Coupon, float]:
        coupon = await self.coupon_repo.get_by_code(code)
        if coupon is None or not coupon.is_active:
            raise CouponError("invalid coupon code")

        now = datetime.now(timezone.utc)
        if not (coupon.valid_from <= now <= coupon.valid_to):
            raise CouponError("this coupon is not currently valid")

        if item_total < float(coupon.min_order_amount):
            raise CouponError(f"minimum order amount for this coupon is {coupon.min_order_amount}")

        if coupon.usage_limit is not None and coupon.times_used >= coupon.usage_limit:
            raise CouponError("this coupon has reached its usage limit")

        user_usage_count = await self.order_repo.count_orders_for_user_and_coupon(user_id, coupon.id)
        if user_usage_count >= coupon.per_user_limit:
            raise CouponError("you have already used this coupon")

        if coupon.discount_type == DiscountType.PERCENT:
            discount = item_total * float(coupon.discount_value) / 100
        else:
            discount = float(coupon.discount_value)

        if coupon.max_discount_amount is not None:
            discount = min(discount, float(coupon.max_discount_amount))
        discount = min(discount, item_total)

        return coupon, round(discount, 2)
