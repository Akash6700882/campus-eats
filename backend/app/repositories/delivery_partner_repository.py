import uuid

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.delivery import DeliveryPartner
from app.repositories.base import BaseRepository


class DeliveryPartnerRepository(BaseRepository[DeliveryPartner]):
    model = DeliveryPartner

    def _base_query(self):
        return select(DeliveryPartner).options(selectinload(DeliveryPartner.user))

    async def get_with_user(self, id: uuid.UUID) -> DeliveryPartner | None:
        result = await self.session.execute(self._base_query().where(DeliveryPartner.id == id))
        return result.scalar_one_or_none()

    async def get_by_user_id(self, user_id: uuid.UUID) -> DeliveryPartner | None:
        result = await self.session.execute(self._base_query().where(DeliveryPartner.user_id == user_id))
        return result.scalar_one_or_none()

    async def list_available(self) -> list[DeliveryPartner]:
        result = await self.session.execute(
            self._base_query().where(
                DeliveryPartner.is_available.is_(True),
                DeliveryPartner.current_latitude.is_not(None),
                DeliveryPartner.current_longitude.is_not(None),
            )
        )
        return list(result.scalars().all())

    async def list_all(self) -> list[DeliveryPartner]:
        result = await self.session.execute(self._base_query().order_by(DeliveryPartner.created_at.desc()))
        return list(result.scalars().all())
