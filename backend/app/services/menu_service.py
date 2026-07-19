import uuid

from app.core.utils import slugify
from app.models.category import Category
from app.models.food import Food
from app.repositories.category_repository import CategoryRepository
from app.repositories.food_repository import FoodRepository
from app.schemas.menu import CategoryCreateRequest, CategoryUpdateRequest, FoodCreateRequest, FoodUpdateRequest


class MenuError(Exception):
    pass


class MenuNotFoundError(MenuError):
    pass


class MenuConflictError(MenuError):
    pass


class MenuService:
    def __init__(self, category_repo: CategoryRepository, food_repo: FoodRepository):
        self.category_repo = category_repo
        self.food_repo = food_repo

    async def create_category(self, payload: CategoryCreateRequest) -> Category:
        slug = slugify(payload.name)
        if await self.category_repo.get_by_slug(slug):
            raise MenuConflictError(f"category '{payload.name}' already exists")
        category = Category(
            id=uuid.uuid4(),
            name=payload.name,
            slug=slug,
            description=payload.description,
            image_url=payload.image_url,
            sort_order=payload.sort_order,
        )
        return await self.category_repo.create(category)

    async def update_category(self, category_id: uuid.UUID, payload: CategoryUpdateRequest) -> Category:
        category = await self.category_repo.get(category_id)
        if category is None:
            raise MenuNotFoundError("category not found")

        data = payload.model_dump(exclude_unset=True)
        if "name" in data:
            category.name = data["name"]
            category.slug = slugify(data["name"])
        for field in ("description", "image_url", "sort_order", "is_active"):
            if field in data:
                setattr(category, field, data[field])
        return category

    async def delete_category(self, category_id: uuid.UUID) -> None:
        category = await self.category_repo.get(category_id)
        if category is None:
            raise MenuNotFoundError("category not found")
        await self.category_repo.delete(category)

    async def create_food(self, payload: FoodCreateRequest) -> Food:
        category = await self.category_repo.get(payload.category_id)
        if category is None:
            raise MenuNotFoundError("category not found")

        slug = slugify(payload.name)
        if await self.food_repo.get_by_slug(slug):
            raise MenuConflictError(f"food '{payload.name}' already exists")

        food = Food(
            id=uuid.uuid4(),
            category_id=payload.category_id,
            name=payload.name,
            slug=slug,
            description=payload.description,
            image_url=payload.image_url,
            price=payload.price,
            discount_percent=payload.discount_percent,
            is_veg=payload.is_veg,
            prep_time_minutes=payload.prep_time_minutes,
            is_available=payload.is_available,
            is_popular=payload.is_popular,
            is_special_today=payload.is_special_today,
        )
        await self.food_repo.create(food)
        food.category = category
        return food

    async def update_food(self, food_id: uuid.UUID, payload: FoodUpdateRequest) -> Food:
        food = await self.food_repo.get_with_category(food_id)
        if food is None:
            raise MenuNotFoundError("food not found")

        data = payload.model_dump(exclude_unset=True)
        if "category_id" in data:
            category = await self.category_repo.get(data["category_id"])
            if category is None:
                raise MenuNotFoundError("category not found")
            food.category = category
        if "name" in data:
            food.name = data["name"]
            food.slug = slugify(data["name"])
        for field in (
            "description", "image_url", "price", "discount_percent", "is_veg",
            "prep_time_minutes", "is_available", "is_popular", "is_special_today",
        ):
            if field in data:
                setattr(food, field, data[field])
        return food

    async def delete_food(self, food_id: uuid.UUID) -> None:
        food = await self.food_repo.get(food_id)
        if food is None:
            raise MenuNotFoundError("food not found")
        await self.food_repo.delete(food)
