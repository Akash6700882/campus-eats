import uuid

from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService


class AdminUserError(Exception):
    pass


class AdminUserService:
    def __init__(self, user_repo: UserRepository, auth_service: AuthService):
        self.user_repo = user_repo
        self.auth_service = auth_service

    async def _get_target(self, user_id: uuid.UUID) -> User:
        user = await self.user_repo.get_with_role(user_id)
        if user is None:
            raise AdminUserError("user not found")
        return user

    async def set_active(self, actor_id: uuid.UUID, user_id: uuid.UUID, is_active: bool) -> User:
        if actor_id == user_id:
            raise AdminUserError("you cannot block or unblock your own account")
        user = await self._get_target(user_id)
        user.is_active = is_active
        return user

    async def reset_password(self, user_id: uuid.UUID) -> None:
        user = await self._get_target(user_id)
        await self.auth_service.forgot_password(user.email)

    async def delete_user(self, actor_id: uuid.UUID, user_id: uuid.UUID) -> User:
        """Soft-deletes: the account is deactivated and personally-identifying
        fields are anonymized, but the row itself is kept. Orders, payments,
        and reviews reference it via a non-nullable foreign key — a real
        DELETE would either cascade-destroy that order/financial history
        (User.orders cascades "all, delete-orphan") or fail outright, so
        this is the only way to honor "delete this account" without losing
        records a food business needs to keep."""
        if actor_id == user_id:
            raise AdminUserError("you cannot delete your own account")
        user = await self._get_target(user_id)
        anon_suffix = uuid.uuid4().hex[:12]
        user.full_name = "Deleted User"
        user.email = f"deleted-{anon_suffix}@campuseats.invalid"
        user.phone = f"0000{anon_suffix[:6]}"
        user.is_active = False
        return user
