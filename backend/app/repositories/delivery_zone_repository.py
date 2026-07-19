from sqlalchemy import select

from app.models.delivery import DeliveryZone
from app.repositories.base import BaseRepository


class DeliveryZoneRepository(BaseRepository[DeliveryZone]):
    model = DeliveryZone

    async def list_active(self) -> list[DeliveryZone]:
        result = await self.session.execute(select(DeliveryZone).where(DeliveryZone.is_active.is_(True)))
        return list(result.scalars().all())
