import uuid

from sqlalchemy import select

from app.models.address import Address
from app.repositories.base import BaseRepository


class AddressRepository(BaseRepository[Address]):
    model = Address

    async def list_for_user(self, user_id: uuid.UUID) -> list[Address]:
        result = await self.session.execute(
            select(Address).where(Address.user_id == user_id).order_by(Address.is_default.desc())
        )
        return list(result.scalars().all())

    async def get_for_user(self, address_id: uuid.UUID, user_id: uuid.UUID) -> Address | None:
        result = await self.session.execute(
            select(Address).where(Address.id == address_id, Address.user_id == user_id)
        )
        return result.scalar_one_or_none()
