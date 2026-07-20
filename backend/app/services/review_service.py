import uuid

from app.models.review import Review, ReviewLike
from app.repositories.food_repository import FoodRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.review_repository import ReviewRepository


class ReviewError(Exception):
    pass


class ReviewService:
    def __init__(self, review_repo: ReviewRepository, food_repo: FoodRepository, order_repo: OrderRepository):
        self.review_repo = review_repo
        self.food_repo = food_repo
        self.order_repo = order_repo

    async def create_review(
        self,
        user_id: uuid.UUID,
        food_id: uuid.UUID,
        rating: int,
        comment: str | None,
        image_url: str | None,
        order_id: uuid.UUID | None,
    ) -> Review:
        food = await self.food_repo.get(food_id)
        if food is None:
            raise ReviewError("food not found")

        if await self.review_repo.get_by_user_and_food(user_id, food_id):
            raise ReviewError("you've already reviewed this item")

        if not await self.order_repo.has_delivered_order_with_food(user_id, food_id):
            raise ReviewError("you can only review food from a delivered order")

        review = Review(
            id=uuid.uuid4(),
            user_id=user_id,
            food_id=food_id,
            order_id=order_id,
            rating=rating,
            comment=comment,
            image_url=image_url,
        )
        await self.review_repo.create(review)

        new_count = food.rating_count + 1
        food.rating_avg = round((float(food.rating_avg) * food.rating_count + rating) / new_count, 2)
        food.rating_count = new_count
        return review

    async def delete_review(self, review_id: uuid.UUID, user_id: uuid.UUID) -> None:
        review = await self.review_repo.get(review_id)
        if review is None or review.user_id != user_id:
            raise ReviewError("review not found")

        food = await self.food_repo.get(review.food_id)
        if food is not None and food.rating_count > 0:
            new_count = food.rating_count - 1
            food.rating_avg = round(
                ((float(food.rating_avg) * food.rating_count) - review.rating) / new_count, 2
            ) if new_count > 0 else 0
            food.rating_count = new_count

        await self.review_repo.delete(review)

    async def toggle_like(self, review_id: uuid.UUID, user_id: uuid.UUID) -> tuple[Review, bool]:
        review = await self.review_repo.get(review_id)
        if review is None:
            raise ReviewError("review not found")

        existing = await self.review_repo.get_like(review_id, user_id)
        if existing is not None:
            await self.review_repo.session.delete(existing)
            review.likes_count = max(0, review.likes_count - 1)
            liked = False
        else:
            self.review_repo.session.add(ReviewLike(id=uuid.uuid4(), review_id=review_id, user_id=user_id))
            review.likes_count += 1
            liked = True

        await self.review_repo.session.flush()
        return review, liked
