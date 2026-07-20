import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class ReviewCreateRequest(BaseModel):
    rating: int = Field(ge=1, le=5)
    comment: str | None = Field(default=None, max_length=1000)
    image_url: str | None = None
    order_id: uuid.UUID | None = None


class ReviewResponse(BaseModel):
    id: uuid.UUID
    food_id: uuid.UUID
    user_id: uuid.UUID
    user_name: str
    rating: int
    comment: str | None
    image_url: str | None
    likes_count: int
    created_at: datetime

    @staticmethod
    def from_review(review) -> "ReviewResponse":
        return ReviewResponse(
            id=review.id,
            food_id=review.food_id,
            user_id=review.user_id,
            user_name=review.user.full_name,
            rating=review.rating,
            comment=review.comment,
            image_url=review.image_url,
            likes_count=review.likes_count,
            created_at=review.created_at,
        )


class ReviewLikeResponse(BaseModel):
    review_id: uuid.UUID
    liked: bool
    likes_count: int
