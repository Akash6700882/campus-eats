import uuid

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.review import Review, ReviewLike
from app.repositories.base import BaseRepository


class ReviewRepository(BaseRepository[Review]):
    model = Review

    def _base_query(self):
        return select(Review).options(selectinload(Review.user))

    async def list_for_food(self, food_id: uuid.UUID, limit: int = 50, offset: int = 0) -> list[Review]:
        result = await self.session.execute(
            self._base_query()
            .where(Review.food_id == food_id)
            .order_by(Review.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def get_with_user(self, review_id: uuid.UUID) -> Review | None:
        result = await self.session.execute(self._base_query().where(Review.id == review_id))
        return result.scalar_one_or_none()

    async def get_by_user_and_food(self, user_id: uuid.UUID, food_id: uuid.UUID) -> Review | None:
        result = await self.session.execute(
            select(Review).where(Review.user_id == user_id, Review.food_id == food_id)
        )
        return result.scalar_one_or_none()

    async def get_like(self, review_id: uuid.UUID, user_id: uuid.UUID) -> ReviewLike | None:
        result = await self.session.execute(
            select(ReviewLike).where(ReviewLike.review_id == review_id, ReviewLike.user_id == user_id)
        )
        return result.scalar_one_or_none()
