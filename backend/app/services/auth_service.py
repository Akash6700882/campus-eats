import uuid

from app.core.jwt import InvalidTokenError, TokenType, create_reset_token, decode_token
from app.core.security import hash_password, verify_password
from app.models.enums import RoleName
from app.models.user import User
from app.repositories.role_repository import RoleRepository
from app.repositories.user_repository import UserRepository
from app.services.email_service import EmailService
from app.services.otp_service import OtpService


class AuthError(Exception):
    pass


class AuthService:
    def __init__(
        self,
        user_repo: UserRepository,
        role_repo: RoleRepository,
        otp_service: OtpService,
        email_service: EmailService,
    ):
        self.user_repo = user_repo
        self.role_repo = role_repo
        self.otp_service = otp_service
        self.email_service = email_service

    async def signup(self, full_name: str, email: str, phone: str, password: str) -> User:
        if await self.user_repo.get_by_email(email):
            raise AuthError("email already registered")
        if await self.user_repo.get_by_phone(phone):
            raise AuthError("phone already registered")

        customer_role = await self.role_repo.get_by_name(RoleName.CUSTOMER.value)
        if customer_role is None:
            raise AuthError("customer role is not seeded — run scripts/seed.py")

        user = User(
            id=uuid.uuid4(),
            full_name=full_name,
            email=email,
            phone=phone,
            hashed_password=hash_password(password),
            role_id=customer_role.id,
            is_active=True,
            is_verified=False,
        )
        await self.user_repo.create(user)
        user.role = customer_role
        return user

    async def login(self, email: str, password: str) -> User:
        user = await self.user_repo.get_by_email(email)
        if user is None or not verify_password(password, user.hashed_password):
            raise AuthError("invalid email or password")
        if not user.is_active:
            raise AuthError("account is disabled")
        return user

    async def request_otp(self, phone: str) -> None:
        await self.otp_service.request_otp(phone)

    async def verify_otp_login(self, phone: str, code: str) -> User:
        if not await self.otp_service.verify_otp(phone, code):
            raise AuthError("invalid or expired OTP")
        user = await self.user_repo.get_by_phone(phone)
        if user is None:
            raise AuthError("no account registered with this phone number")
        if not user.is_active:
            raise AuthError("account is disabled")
        return user

    async def forgot_password(self, email: str) -> None:
        user = await self.user_repo.get_by_email(email)
        if user is None:
            return  # don't leak account existence
        token = create_reset_token(user.id, user.role.name)
        reset_link = f"/reset-password?token={token}"
        self.email_service.send(
            user.email, "Reset your Campus Eats password", f"Use this link to reset your password: {reset_link}"
        )

    async def reset_password(self, token: str, new_password: str) -> None:
        try:
            payload = decode_token(token, TokenType.RESET)
        except InvalidTokenError as exc:
            raise AuthError("invalid or expired reset token") from exc

        user = await self.user_repo.get(uuid.UUID(payload["sub"]))
        if user is None:
            raise AuthError("user not found")
        user.hashed_password = hash_password(new_password)

    async def get_user_for_refresh(self, user_id: uuid.UUID) -> User:
        user = await self.user_repo.get_with_role(user_id)
        if user is None or not user.is_active:
            raise AuthError("user not found or inactive")
        return user
