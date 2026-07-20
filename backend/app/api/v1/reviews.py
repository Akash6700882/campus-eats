import uuid

from fastapi import APIRouter, HTTPException, status

from app.core.deps import CurrentUser, DbSession, ReviewRepo, ReviewSvc
from app.schemas.review import ReviewCreateRequest, ReviewLikeResponse, ReviewResponse
from app.services.review_service import ReviewError

router = APIRouter(tags=["reviews"])


@router.get("/foods/{food_id}/reviews", response_model=list[ReviewResponse])
async def list_reviews(food_id: uuid.UUID, review_repo: ReviewRepo) -> list[ReviewResponse]:
    reviews = await review_repo.list_for_food(food_id)
    return [ReviewResponse.from_review(r) for r in reviews]


@router.post(
    "/foods/{food_id}/reviews", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED
)
async def create_review(
    food_id: uuid.UUID,
    payload: ReviewCreateRequest,
    current_user: CurrentUser,
    db: DbSession,
    review_service: ReviewSvc,
    review_repo: ReviewRepo,
) -> ReviewResponse:
    try:
        review = await review_service.create_review(
            current_user.id, food_id, payload.rating, payload.comment, payload.image_url, payload.order_id
        )
        await db.commit()
    except ReviewError as exc:
        await db.rollback()
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc
    full = await review_repo.get_with_user(review.id)
    return ReviewResponse.from_review(full)


@router.delete("/reviews/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_review(
    review_id: uuid.UUID, current_user: CurrentUser, db: DbSession, review_service: ReviewSvc
) -> None:
    try:
        await review_service.delete_review(review_id, current_user.id)
        await db.commit()
    except ReviewError as exc:
        await db.rollback()
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc


@router.post("/reviews/{review_id}/like", response_model=ReviewLikeResponse)
async def like_review(
    review_id: uuid.UUID, current_user: CurrentUser, db: DbSession, review_service: ReviewSvc
) -> ReviewLikeResponse:
    try:
        review, liked = await review_service.toggle_like(review_id, current_user.id)
        await db.commit()
    except ReviewError as exc:
        await db.rollback()
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc
    return ReviewLikeResponse(review_id=review.id, liked=liked, likes_count=review.likes_count)
