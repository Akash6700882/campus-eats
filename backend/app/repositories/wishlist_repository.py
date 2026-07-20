import uuid

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.food import Food
from app.models.review import WishlistItem
from app.repositories.base import BaseRepository


class WishlistRepository(BaseRepository[WishlistItem]):
    model = WishlistItem

    async def list_for_user(self, user_id: uuid.UUID) -> list[WishlistItem]:
        result = await self.session.execute(
            select(WishlistItem)
            .options(selectinload(WishlistItem.food).selectinload(Food.category))
            .where(WishlistItem.user_id == user_id)
            .order_by(WishlistItem.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_for_user_and_food(self, user_id: uuid.UUID, food_id: uuid.UUID) -> WishlistItem | None:
        result = await self.session.execute(
            select(WishlistItem).where(WishlistItem.user_id == user_id, WishlistItem.food_id == food_id)
        )
        return result.scalar_one_or_none()
