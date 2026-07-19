import uuid

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.deps import CouponRepo, DbSession, require_role
from app.models.coupon import Coupon
from app.models.enums import RoleName
from app.schemas.coupon import CouponCreateRequest, CouponResponse, CouponUpdateRequest

router = APIRouter(prefix="/admin/coupons", tags=["coupons"])

RequireAdmin = Depends(require_role(RoleName.ADMIN.value))


@router.get("", response_model=list[CouponResponse], dependencies=[RequireAdmin])
async def list_coupons(coupon_repo: CouponRepo) -> list[CouponResponse]:
    coupons = await coupon_repo.list()
    return [CouponResponse.model_validate(c) for c in coupons]


@router.post("", response_model=CouponResponse, status_code=status.HTTP_201_CREATED, dependencies=[RequireAdmin])
async def create_coupon(payload: CouponCreateRequest, db: DbSession, coupon_repo: CouponRepo) -> CouponResponse:
    code = payload.code.upper()
    if await coupon_repo.get_by_code(code):
        raise HTTPException(status.HTTP_409_CONFLICT, f"coupon '{code}' already exists")

    coupon = Coupon(
        id=uuid.uuid4(),
        code=code,
        description=payload.description,
        coupon_type=payload.coupon_type,
        discount_type=payload.discount_type,
        discount_value=payload.discount_value,
        max_discount_amount=payload.max_discount_amount,
        min_order_amount=payload.min_order_amount,
        valid_from=payload.valid_from,
        valid_to=payload.valid_to,
        usage_limit=payload.usage_limit,
        per_user_limit=payload.per_user_limit,
    )
    await coupon_repo.create(coupon)
    await db.commit()
    return CouponResponse.model_validate(coupon)


@router.patch("/{coupon_id}", response_model=CouponResponse, dependencies=[RequireAdmin])
async def update_coupon(
    coupon_id: uuid.UUID, payload: CouponUpdateRequest, db: DbSession, coupon_repo: CouponRepo
) -> CouponResponse:
    coupon = await coupon_repo.get(coupon_id)
    if coupon is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "coupon not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(coupon, field, value)
    await db.commit()
    return CouponResponse.model_validate(coupon)
