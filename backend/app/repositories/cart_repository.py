import uuid

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.cart import CartItem
from app.repositories.base import BaseRepository


class CartRepository(BaseRepository[CartItem]):
    model = CartItem

    async def list_for_user(self, user_id: uuid.UUID) -> list[CartItem]:
        result = await self.session.execute(
            select(CartItem).options(selectinload(CartItem.food)).where(CartItem.user_id == user_id)
        )
        return list(result.scalars().all())

    async def get_for_user(self, user_id: uuid.UUID, food_id: uuid.UUID) -> CartItem | None:
        result = await self.session.execute(
            select(CartItem)
            .options(selectinload(CartItem.food))
            .where(CartItem.user_id == user_id, CartItem.food_id == food_id)
        )
        return result.scalar_one_or_none()

    async def clear_for_user(self, user_id: uuid.UUID) -> None:
        items = await self.list_for_user(user_id)
        for item in items:
            await self.session.delete(item)
        await self.session.flush()
