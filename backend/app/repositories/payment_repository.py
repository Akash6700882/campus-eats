from sqlalchemy import select

from app.models.payment import Payment
from app.repositories.base import BaseRepository


class PaymentRepository(BaseRepository[Payment]):
    model = Payment

    async def get_by_provider_order_id(self, provider_order_id: str) -> Payment | None:
        result = await self.session.execute(select(Payment).where(Payment.provider_order_id == provider_order_id))
        return result.scalar_one_or_none()
