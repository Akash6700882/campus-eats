import uuid
from datetime import datetime

from pydantic import BaseModel

from app.schemas.menu import FoodResponse


class WishlistItemResponse(BaseModel):
    id: uuid.UUID
    food: FoodResponse
    created_at: datetime

    @staticmethod
    def from_item(item) -> "WishlistItemResponse":
        return WishlistItemResponse(
            id=item.id, food=FoodResponse.from_food(item.food), created_at=item.created_at
        )
