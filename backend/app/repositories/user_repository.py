import uuid
from datetime import datetime

from sqlalchemy import case, func, select
from sqlalchemy.orm import selectinload

from app.models.enums import OrderStatus, RoleName
from app.models.order import Order
from app.models.role import Role
from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    model = User

    async def get_with_role(self, id: uuid.UUID) -> User | None:
        result = await self.session.execute(
            select(User).options(selectinload(User.role)).where(User.id == id)
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.execute(
            select(User).options(selectinload(User.role)).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def get_by_phone(self, phone: str) -> User | None:
        result = await self.session.execute(
            select(User).options(selectinload(User.role)).where(User.phone == phone)
        )
        return result.scalar_one_or_none()

    async def list_by_role(self, role_name: str) -> list[User]:
        result = await self.session.execute(
            select(User)
            .options(selectinload(User.role))
            .where(User.role.has(name=role_name))
            .order_by(User.full_name)
        )
        return list(result.scalars().all())

    async def count_by_role(self, role_name: str) -> int:
        result = await self.session.execute(
            select(func.count()).select_from(User).where(User.role.has(name=role_name))
        )
        return int(result.scalar_one())

    async def list_customers_with_order_stats(self) -> list[tuple[User, int, float, datetime | None]]:
        """Customer accounts with order-count/spend/last-order aggregates for
        the admin user-management view. Spend counts only DELIVERED orders,
        matching how AnalyticsRepository.total_revenue defines "real" revenue
        elsewhere in the app."""
        spend_case = case((Order.status == OrderStatus.DELIVERED, Order.grand_total), else_=0)
        result = await self.session.execute(
            select(
                User,
                func.count(Order.id),
                func.coalesce(func.sum(spend_case), 0),
                func.max(Order.placed_at),
            )
            .join(Role, User.role_id == Role.id)
            .outerjoin(Order, Order.user_id == User.id)
            .where(Role.name == RoleName.CUSTOMER.value)
            .group_by(User.id)
            .order_by(User.full_name)
        )
        return [(user, int(count), float(spend), last_order_at) for user, count, spend, last_order_at in result.all()]
