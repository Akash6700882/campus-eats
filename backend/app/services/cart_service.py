import uuid

from app.models.cart import CartItem
from app.repositories.cart_repository import CartRepository
from app.repositories.food_repository import FoodRepository
from app.schemas.cart import CartItemResponse, CartSummaryResponse
from app.services.app_settings_service import AppSettingsService
from app.services.coupon_service import CouponError, CouponService


class CartError(Exception):
    pass


class CartService:
    def __init__(
        self,
        cart_repo: CartRepository,
        food_repo: FoodRepository,
        coupon_service: CouponService,
        app_settings_service: AppSettingsService,
    ):
        self.cart_repo = cart_repo
        self.food_repo = food_repo
        self.coupon_service = coupon_service
        self.app_settings_service = app_settings_service

    async def add_item(self, user_id: uuid.UUID, food_id: uuid.UUID, quantity: int) -> CartItem:
        food = await self.food_repo.get(food_id)
        if food is None or not food.is_available:
            raise CartError("food not found or unavailable")

        existing = await self.cart_repo.get_for_user(user_id, food_id)
        if existing is not None:
            existing.quantity += quantity
            existing.food = food
            return existing

        item = CartItem(id=uuid.uuid4(), user_id=user_id, food_id=food_id, quantity=quantity)
        await self.cart_repo.create(item)
        item.food = food
        return item

    async def update_quantity(self, user_id: uuid.UUID, food_id: uuid.UUID, quantity: int) -> CartItem:
        item = await self.cart_repo.get_for_user(user_id, food_id)
        if item is None:
            raise CartError("item not in cart")
        item.quantity = quantity
        return item

    async def remove_item(self, user_id: uuid.UUID, food_id: uuid.UUID) -> None:
        item = await self.cart_repo.get_for_user(user_id, food_id)
        if item is None:
            raise CartError("item not in cart")
        await self.cart_repo.delete(item)

    async def get_summary(self, user_id: uuid.UUID, coupon_code: str | None = None) -> CartSummaryResponse:
        app_settings = await self.app_settings_service.get()
        cart_items = await self.cart_repo.list_for_user(user_id)

        item_responses = [
            CartItemResponse(
                id=ci.id,
                food_id=ci.food_id,
                food_name=ci.food.name,
                unit_price=ci.food.discounted_price,
                quantity=ci.quantity,
                subtotal=round(ci.food.discounted_price * ci.quantity, 2),
                image_url=ci.food.image_url,
                is_available=ci.food.is_available,
            )
            for ci in cart_items
        ]
        item_total = round(sum(r.subtotal for r in item_responses), 2)

        discount_amount = 0.0
        coupon_error = None
        applied_code = None
        if coupon_code:
            try:
                coupon, discount_amount = await self.coupon_service.validate_and_price(
                    coupon_code, user_id, item_total
                )
                applied_code = coupon.code
            except CouponError as exc:
                coupon_error = str(exc)

        taxable = item_total - discount_amount
        gst_amount = round(taxable * float(app_settings.gst_percent) / 100, 2)
        delivery_charge = float(app_settings.delivery_charge) if item_responses else 0.0
        packing_charge = float(app_settings.packing_charge) if item_responses else 0.0
        grand_total = round(taxable + delivery_charge + packing_charge + gst_amount, 2)

        return CartSummaryResponse(
            items=item_responses,
            item_total=item_total,
            discount_amount=discount_amount,
            delivery_charge=delivery_charge,
            packing_charge=packing_charge,
            gst_amount=gst_amount,
            grand_total=grand_total,
            estimated_delivery_minutes=(
                max((ci.food.prep_time_minutes for ci in cart_items), default=10) + 15
            ),
            coupon_code=applied_code,
            coupon_error=coupon_error,
        )
