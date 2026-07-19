from sqlalchemy import select

from app.models.coupon import Coupon
from app.repositories.base import BaseRepository


class CouponRepository(BaseRepository[Coupon]):
    model = Coupon

    async def get_by_code(self, code: str) -> Coupon | None:
        result = await self.session.execute(select(Coupon).where(Coupon.code == code.upper()))
        return result.scalar_one_or_none()
