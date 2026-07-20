import uuid

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    model = User

    async def get_with_role(self, id: uuid.UUID) -> User | None:
        result = await self.session.execute(
            select(User).options(selectinload(User.role)).where(User.id == id)
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.execute(
            select(User).options(selectinload(User.role)).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def get_by_phone(self, phone: str) -> User | None:
        result = await self.session.execute(
            select(User).options(selectinload(User.role)).where(User.phone == phone)
        )
        return result.scalar_one_or_none()

    async def list_by_role(self, role_name: str) -> list[User]:
        result = await self.session.execute(
            select(User)
            .options(selectinload(User.role))
            .where(User.role.has(name=role_name))
            .order_by(User.full_name)
        )
        return list(result.scalars().all())
