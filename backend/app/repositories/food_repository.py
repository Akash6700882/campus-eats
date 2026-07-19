import uuid

from sqlalchemy import Select, select
from sqlalchemy.orm import selectinload

from app.models.food import Food
from app.repositories.base import BaseRepository


class FoodRepository(BaseRepository[Food]):
    model = Food

    def _base_query(self) -> Select:
        return select(Food).options(selectinload(Food.category))

    async def get_by_slug(self, slug: str) -> Food | None:
        result = await self.session.execute(self._base_query().where(Food.slug == slug))
        return result.scalar_one_or_none()

    async def get_with_category(self, id: uuid.UUID) -> Food | None:
        result = await self.session.execute(self._base_query().where(Food.id == id))
        return result.scalar_one_or_none()

    async def search(
        self,
        *,
        query: str | None = None,
        category_id: uuid.UUID | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
        min_rating: float | None = None,
        is_veg: bool | None = None,
        is_available: bool | None = True,
        is_popular: bool | None = None,
        is_special_today: bool | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Food]:
        stmt = self._base_query()

        if query:
            stmt = stmt.where(Food.name.ilike(f"%{query}%"))
        if category_id is not None:
            stmt = stmt.where(Food.category_id == category_id)
        if min_price is not None:
            stmt = stmt.where(Food.price >= min_price)
        if max_price is not None:
            stmt = stmt.where(Food.price <= max_price)
        if min_rating is not None:
            stmt = stmt.where(Food.rating_avg >= min_rating)
        if is_veg is not None:
            stmt = stmt.where(Food.is_veg == is_veg)
        if is_available is not None:
            stmt = stmt.where(Food.is_available == is_available)
        if is_popular is not None:
            stmt = stmt.where(Food.is_popular == is_popular)
        if is_special_today is not None:
            stmt = stmt.where(Food.is_special_today == is_special_today)

        stmt = stmt.order_by(Food.name).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
