import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.core.deps import CategoryRepo, DbSession, FoodRepo, ImageSvc, MenuSvc, require_role
from app.models.enums import RoleName
from app.schemas.menu import (
    CategoryCreateRequest,
    CategoryResponse,
    CategoryUpdateRequest,
    FoodCreateRequest,
    FoodResponse,
    FoodUpdateRequest,
    ImageUploadResponse,
)
from app.services.image_service import ImageUploadError
from app.services.menu_service import MenuConflictError, MenuNotFoundError

router = APIRouter(tags=["menu"])

RequireAdmin = Depends(require_role(RoleName.ADMIN.value))


# --- Public browse/search ---------------------------------------------------


@router.get("/categories", response_model=list[CategoryResponse])
async def list_categories(category_repo: CategoryRepo) -> list[CategoryResponse]:
    categories = await category_repo.list_active()
    return [CategoryResponse.model_validate(c) for c in categories]


@router.get("/foods", response_model=list[FoodResponse])
async def search_foods(
    food_repo: FoodRepo,
    q: str | None = None,
    category_id: uuid.UUID | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    min_rating: float | None = None,
    is_veg: bool | None = None,
    is_popular: bool | None = None,
    is_special_today: bool | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[FoodResponse]:
    foods = await food_repo.search(
        query=q,
        category_id=category_id,
        min_price=min_price,
        max_price=max_price,
        min_rating=min_rating,
        is_veg=is_veg,
        is_popular=is_popular,
        is_special_today=is_special_today,
        limit=limit,
        offset=offset,
    )
    return [FoodResponse.from_food(f) for f in foods]


@router.get("/foods/{slug}", response_model=FoodResponse)
async def get_food(slug: str, food_repo: FoodRepo) -> FoodResponse:
    food = await food_repo.get_by_slug(slug)
    if food is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Food not found")
    return FoodResponse.from_food(food)


# --- Admin: categories --------------------------------------------------------


@router.post(
    "/admin/categories", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED,
    dependencies=[RequireAdmin],
)
async def create_category(payload: CategoryCreateRequest, db: DbSession, menu_service: MenuSvc) -> CategoryResponse:
    try:
        category = await menu_service.create_category(payload)
        await db.commit()
    except MenuConflictError as exc:
        await db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, str(exc)) from exc
    return CategoryResponse.model_validate(category)


@router.patch("/admin/categories/{category_id}", response_model=CategoryResponse, dependencies=[RequireAdmin])
async def update_category(
    category_id: uuid.UUID, payload: CategoryUpdateRequest, db: DbSession, menu_service: MenuSvc
) -> CategoryResponse:
    try:
        category = await menu_service.update_category(category_id, payload)
        await db.commit()
    except MenuNotFoundError as exc:
        await db.rollback()
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc
    return CategoryResponse.model_validate(category)


@router.delete("/admin/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[RequireAdmin])
async def delete_category(category_id: uuid.UUID, db: DbSession, menu_service: MenuSvc) -> None:
    try:
        await menu_service.delete_category(category_id)
        await db.commit()
    except MenuNotFoundError as exc:
        await db.rollback()
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc


# --- Admin: foods --------------------------------------------------------------


@router.post(
    "/admin/foods", response_model=FoodResponse, status_code=status.HTTP_201_CREATED, dependencies=[RequireAdmin]
)
async def create_food(payload: FoodCreateRequest, db: DbSession, menu_service: MenuSvc) -> FoodResponse:
    try:
        food = await menu_service.create_food(payload)
        await db.commit()
    except MenuNotFoundError as exc:
        await db.rollback()
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc
    except MenuConflictError as exc:
        await db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, str(exc)) from exc
    return FoodResponse.from_food(food)


@router.patch("/admin/foods/{food_id}", response_model=FoodResponse, dependencies=[RequireAdmin])
async def update_food(
    food_id: uuid.UUID, payload: FoodUpdateRequest, db: DbSession, menu_service: MenuSvc
) -> FoodResponse:
    try:
        food = await menu_service.update_food(food_id, payload)
        await db.commit()
    except MenuNotFoundError as exc:
        await db.rollback()
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc
    return FoodResponse.from_food(food)


@router.delete("/admin/foods/{food_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[RequireAdmin])
async def delete_food(food_id: uuid.UUID, db: DbSession, menu_service: MenuSvc) -> None:
    try:
        await menu_service.delete_food(food_id)
        await db.commit()
    except MenuNotFoundError as exc:
        await db.rollback()
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc


@router.post("/admin/foods/{food_id}/image", response_model=ImageUploadResponse, dependencies=[RequireAdmin])
async def upload_food_image(
    food_id: uuid.UUID, db: DbSession, food_repo: FoodRepo, image_service: ImageSvc, file: UploadFile = File(...)
) -> ImageUploadResponse:
    food = await food_repo.get(food_id)
    if food is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Food not found")

    try:
        image_url = image_service.upload(await file.read(), folder="campus-eats/foods")
    except ImageUploadError as exc:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, str(exc)) from exc

    food.image_url = image_url
    await db.commit()
    return ImageUploadResponse(image_url=image_url)
