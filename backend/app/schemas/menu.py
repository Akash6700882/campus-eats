import uuid

from pydantic import BaseModel, Field


class CategoryCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    description: str | None = Field(default=None, max_length=255)
    image_url: str | None = None
    sort_order: int = 0


class CategoryUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=80)
    description: str | None = Field(default=None, max_length=255)
    image_url: str | None = None
    sort_order: int | None = None
    is_active: bool | None = None


class CategoryResponse(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    description: str | None
    image_url: str | None
    sort_order: int
    is_active: bool

    model_config = {"from_attributes": True}


class FoodCreateRequest(BaseModel):
    category_id: uuid.UUID
    name: str = Field(min_length=1, max_length=120)
    description: str | None = None
    image_url: str | None = None
    price: float = Field(gt=0)
    discount_percent: float = Field(default=0, ge=0, le=100)
    is_veg: bool = True
    prep_time_minutes: int = Field(default=10, ge=0)
    is_available: bool = True
    is_popular: bool = False
    is_special_today: bool = False


class FoodUpdateRequest(BaseModel):
    category_id: uuid.UUID | None = None
    name: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = None
    image_url: str | None = None
    price: float | None = Field(default=None, gt=0)
    discount_percent: float | None = Field(default=None, ge=0, le=100)
    is_veg: bool | None = None
    prep_time_minutes: int | None = Field(default=None, ge=0)
    is_available: bool | None = None
    is_popular: bool | None = None
    is_special_today: bool | None = None


class FoodResponse(BaseModel):
    id: uuid.UUID
    category_id: uuid.UUID
    category_name: str
    name: str
    slug: str
    description: str | None
    image_url: str | None
    price: float
    discount_percent: float
    discounted_price: float
    is_veg: bool
    prep_time_minutes: int
    rating_avg: float
    rating_count: int
    is_available: bool
    is_popular: bool
    is_special_today: bool

    @staticmethod
    def from_food(food) -> "FoodResponse":
        return FoodResponse(
            id=food.id,
            category_id=food.category_id,
            category_name=food.category.name,
            name=food.name,
            slug=food.slug,
            description=food.description,
            image_url=food.image_url,
            price=float(food.price),
            discount_percent=float(food.discount_percent),
            discounted_price=food.discounted_price,
            is_veg=food.is_veg,
            prep_time_minutes=food.prep_time_minutes,
            rating_avg=float(food.rating_avg),
            rating_count=food.rating_count,
            is_available=food.is_available,
            is_popular=food.is_popular,
            is_special_today=food.is_special_today,
        )


class ImageUploadResponse(BaseModel):
    image_url: str
