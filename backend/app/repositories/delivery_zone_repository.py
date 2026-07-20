from sqlalchemy import select

from app.models.delivery import DeliveryZone
from app.repositories.base import BaseRepository


class DeliveryZoneRepository(BaseRepository[DeliveryZone]):
    model = DeliveryZone

    async def list_active(self) -> list[DeliveryZone]:
        result = await self.session.execute(select(DeliveryZone).where(DeliveryZone.is_active.is_(True)))
        return list(result.scalars().all())

    async def get_first_active(self) -> DeliveryZone | None:
        result = await self.session.execute(
            select(DeliveryZone).where(DeliveryZone.is_active.is_(True)).order_by(DeliveryZone.created_at).limit(1)
        )
        return result.scalar_one_or_none()
