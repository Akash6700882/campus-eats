import uuid
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.jwt import InvalidTokenError, TokenType, decode_token
from app.core.redis_client import get_redis
from app.models.user import User
from app.repositories.address_repository import AddressRepository
from app.repositories.cart_repository import CartRepository
from app.repositories.category_repository import CategoryRepository
from app.repositories.coupon_repository import CouponRepository
from app.repositories.delivery_partner_repository import DeliveryPartnerRepository
from app.repositories.delivery_zone_repository import DeliveryZoneRepository
from app.repositories.food_repository import FoodRepository
from app.repositories.notification_repository import NotificationRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.review_repository import ReviewRepository
from app.repositories.role_repository import RoleRepository
from app.repositories.user_repository import UserRepository
from app.repositories.wishlist_repository import WishlistRepository
from app.services.address_service import AddressService
from app.services.auth_service import AuthService
from app.services.cart_service import CartService
from app.services.coupon_service import CouponService
from app.services.delivery_service import DeliveryPartnerService
from app.services.delivery_zone_service import DeliveryZoneService
from app.services.email_service import EmailService
from app.services.image_service import ImageService
from app.services.menu_service import MenuService
from app.services.notification_provider import get_sms_provider
from app.services.notification_service import NotificationService
from app.services.order_service import OrderService
from app.services.otp_service import OtpService
from app.services.payment_gateway import PaymentGateway, RazorpayGateway
from app.services.payment_service import PaymentService
from app.services.review_service import ReviewService

DbSession = Annotated[AsyncSession, Depends(get_db)]

_bearer_scheme = HTTPBearer(auto_error=False)


def get_user_repository(session: DbSession) -> UserRepository:
    return UserRepository(session)


def get_role_repository(session: DbSession) -> RoleRepository:
    return RoleRepository(session)


def get_otp_service() -> OtpService:
    return OtpService(redis=get_redis(), sms_provider=get_sms_provider())


def get_email_service() -> EmailService:
    return EmailService()


def get_category_repository(session: DbSession) -> CategoryRepository:
    return CategoryRepository(session)


def get_food_repository(session: DbSession) -> FoodRepository:
    return FoodRepository(session)


def get_image_service() -> ImageService:
    return ImageService()


def get_address_repository(session: DbSession) -> AddressRepository:
    return AddressRepository(session)


def get_cart_repository(session: DbSession) -> CartRepository:
    return CartRepository(session)


def get_coupon_repository(session: DbSession) -> CouponRepository:
    return CouponRepository(session)


def get_delivery_zone_repository(session: DbSession) -> DeliveryZoneRepository:
    return DeliveryZoneRepository(session)


def get_order_repository(session: DbSession) -> OrderRepository:
    return OrderRepository(session)


def get_delivery_partner_repository(session: DbSession) -> DeliveryPartnerRepository:
    return DeliveryPartnerRepository(session)


def get_review_repository(session: DbSession) -> ReviewRepository:
    return ReviewRepository(session)


def get_wishlist_repository(session: DbSession) -> WishlistRepository:
    return WishlistRepository(session)


def get_notification_repository(session: DbSession) -> NotificationRepository:
    return NotificationRepository(session)


UserRepo = Annotated[UserRepository, Depends(get_user_repository)]
RoleRepo = Annotated[RoleRepository, Depends(get_role_repository)]
OtpSvc = Annotated[OtpService, Depends(get_otp_service)]
EmailSvc = Annotated[EmailService, Depends(get_email_service)]
CategoryRepo = Annotated[CategoryRepository, Depends(get_category_repository)]
FoodRepo = Annotated[FoodRepository, Depends(get_food_repository)]
ImageSvc = Annotated[ImageService, Depends(get_image_service)]
AddressRepo = Annotated[AddressRepository, Depends(get_address_repository)]
CartRepo = Annotated[CartRepository, Depends(get_cart_repository)]
CouponRepo = Annotated[CouponRepository, Depends(get_coupon_repository)]
DeliveryZoneRepo = Annotated[DeliveryZoneRepository, Depends(get_delivery_zone_repository)]
OrderRepo = Annotated[OrderRepository, Depends(get_order_repository)]
DeliveryPartnerRepo = Annotated[DeliveryPartnerRepository, Depends(get_delivery_partner_repository)]
ReviewRepo = Annotated[ReviewRepository, Depends(get_review_repository)]
WishlistRepo = Annotated[WishlistRepository, Depends(get_wishlist_repository)]
NotificationRepo = Annotated[NotificationRepository, Depends(get_notification_repository)]


def get_auth_service(
    user_repo: UserRepo, role_repo: RoleRepo, otp_service: OtpSvc, email_service: EmailSvc
) -> AuthService:
    return AuthService(user_repo, role_repo, otp_service, email_service)


def get_menu_service(category_repo: CategoryRepo, food_repo: FoodRepo) -> MenuService:
    return MenuService(category_repo, food_repo)


def get_coupon_service(coupon_repo: CouponRepo, order_repo: OrderRepo) -> CouponService:
    return CouponService(coupon_repo, order_repo)


def get_address_service(address_repo: AddressRepo) -> AddressService:
    return AddressService(address_repo)


AuthSvc = Annotated[AuthService, Depends(get_auth_service)]
MenuSvc = Annotated[MenuService, Depends(get_menu_service)]
CouponSvc = Annotated[CouponService, Depends(get_coupon_service)]
AddressSvc = Annotated[AddressService, Depends(get_address_service)]


def get_cart_service(cart_repo: CartRepo, food_repo: FoodRepo, coupon_service: CouponSvc) -> CartService:
    return CartService(cart_repo, food_repo, coupon_service)


def get_order_service(
    cart_repo: CartRepo,
    address_repo: AddressRepo,
    order_repo: OrderRepo,
    delivery_zone_repo: DeliveryZoneRepo,
    coupon_service: CouponSvc,
    delivery_partner_repo: DeliveryPartnerRepo,
) -> OrderService:
    return OrderService(
        cart_repo, address_repo, order_repo, delivery_zone_repo, coupon_service, delivery_partner_repo
    )


def get_delivery_partner_service(
    delivery_partner_repo: DeliveryPartnerRepo, user_repo: UserRepo
) -> DeliveryPartnerService:
    return DeliveryPartnerService(delivery_partner_repo, user_repo)


def get_review_service(review_repo: ReviewRepo, food_repo: FoodRepo, order_repo: OrderRepo) -> ReviewService:
    return ReviewService(review_repo, food_repo, order_repo)


def get_delivery_zone_service(delivery_zone_repo: DeliveryZoneRepo) -> DeliveryZoneService:
    return DeliveryZoneService(delivery_zone_repo)


DeliveryZoneSvc = Annotated[DeliveryZoneService, Depends(get_delivery_zone_service)]


def get_notification_service(notification_repo: NotificationRepo) -> NotificationService:
    return NotificationService(notification_repo)


CartSvc = Annotated[CartService, Depends(get_cart_service)]
OrderSvc = Annotated[OrderService, Depends(get_order_service)]
DeliveryPartnerSvc = Annotated[DeliveryPartnerService, Depends(get_delivery_partner_service)]
ReviewSvc = Annotated[ReviewService, Depends(get_review_service)]
NotificationSvc = Annotated[NotificationService, Depends(get_notification_service)]


def get_payment_gateway() -> PaymentGateway:
    return RazorpayGateway()


PaymentGw = Annotated[PaymentGateway, Depends(get_payment_gateway)]


def get_payment_service(
    order_repo: OrderRepo, cart_repo: CartRepo, food_repo: FoodRepo, gateway: PaymentGw
) -> PaymentService:
    return PaymentService(order_repo, cart_repo, food_repo, gateway)


PaymentSvc = Annotated[PaymentService, Depends(get_payment_service)]


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer_scheme)],
    user_repo: UserRepo,
) -> User:
    if credentials is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Missing bearer token")

    try:
        payload = decode_token(credentials.credentials, TokenType.ACCESS)
    except InvalidTokenError as exc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired token") from exc

    user = await user_repo.get_with_role(uuid.UUID(payload["sub"]))
    if user is None or not user.is_active:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User not found or inactive")

    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_role(*allowed_roles: str):
    async def dependency(user: CurrentUser) -> User:
        if user.role.name not in allowed_roles:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Insufficient permissions for this action")
        return user

    return dependency
