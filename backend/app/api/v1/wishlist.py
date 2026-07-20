import uuid

from fastapi import APIRouter, HTTPException, status

from app.core.deps import CurrentUser, DbSession, FoodRepo, WishlistRepo
from app.models.review import WishlistItem
from app.schemas.wishlist import WishlistItemResponse

router = APIRouter(prefix="/wishlist", tags=["wishlist"])


@router.get("", response_model=list[WishlistItemResponse])
async def list_wishlist(current_user: CurrentUser, wishlist_repo: WishlistRepo) -> list[WishlistItemResponse]:
    items = await wishlist_repo.list_for_user(current_user.id)
    return [WishlistItemResponse.from_item(i) for i in items]


@router.post("/{food_id}", response_model=WishlistItemResponse, status_code=status.HTTP_201_CREATED)
async def add_to_wishlist(
    food_id: uuid.UUID, current_user: CurrentUser, db: DbSession, wishlist_repo: WishlistRepo, food_repo: FoodRepo
) -> WishlistItemResponse:
    food = await food_repo.get_with_category(food_id)
    if food is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "food not found")

    existing = await wishlist_repo.get_for_user_and_food(current_user.id, food_id)
    if existing is not None:
        existing.food = food
        return WishlistItemResponse.from_item(existing)

    item = WishlistItem(id=uuid.uuid4(), user_id=current_user.id, food_id=food_id)
    await wishlist_repo.create(item)
    await db.commit()
    item.food = food
    return WishlistItemResponse.from_item(item)


@router.delete("/{food_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_from_wishlist(
    food_id: uuid.UUID, current_user: CurrentUser, db: DbSession, wishlist_repo: WishlistRepo
) -> None:
    existing = await wishlist_repo.get_for_user_and_food(current_user.id, food_id)
    if existing is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "not in wishlist")
    await wishlist_repo.delete(existing)
    await db.commit()
