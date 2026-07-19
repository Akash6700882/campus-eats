import uuid

from fastapi import APIRouter, HTTPException, status

from app.core.deps import CartSvc, CurrentUser, DbSession
from app.schemas.cart import CartAddItemRequest, CartSummaryResponse, CartUpdateQuantityRequest
from app.services.cart_service import CartError

router = APIRouter(prefix="/cart", tags=["cart"])


@router.get("", response_model=CartSummaryResponse)
async def get_cart(current_user: CurrentUser, cart_service: CartSvc, coupon_code: str | None = None) -> CartSummaryResponse:
    return await cart_service.get_summary(current_user.id, coupon_code)


@router.post("/items", response_model=CartSummaryResponse, status_code=status.HTTP_201_CREATED)
async def add_item(
    payload: CartAddItemRequest, current_user: CurrentUser, db: DbSession, cart_service: CartSvc
) -> CartSummaryResponse:
    try:
        await cart_service.add_item(current_user.id, payload.food_id, payload.quantity)
        await db.commit()
    except CartError as exc:
        await db.rollback()
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc
    return await cart_service.get_summary(current_user.id)


@router.patch("/items/{food_id}", response_model=CartSummaryResponse)
async def update_item_quantity(
    food_id: uuid.UUID,
    payload: CartUpdateQuantityRequest,
    current_user: CurrentUser,
    db: DbSession,
    cart_service: CartSvc,
) -> CartSummaryResponse:
    try:
        await cart_service.update_quantity(current_user.id, food_id, payload.quantity)
        await db.commit()
    except CartError as exc:
        await db.rollback()
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc
    return await cart_service.get_summary(current_user.id)


@router.delete("/items/{food_id}", response_model=CartSummaryResponse)
async def remove_item(
    food_id: uuid.UUID, current_user: CurrentUser, db: DbSession, cart_service: CartSvc
) -> CartSummaryResponse:
    try:
        await cart_service.remove_item(current_user.id, food_id)
        await db.commit()
    except CartError as exc:
        await db.rollback()
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc
    return await cart_service.get_summary(current_user.id)
