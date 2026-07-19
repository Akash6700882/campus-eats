import uuid

from sqlalchemy import Select, select
from sqlalchemy.orm import selectinload

from app.models.delivery import DeliveryPartner
from app.models.enums import OrderStatus
from app.models.order import Order
from app.repositories.base import BaseRepository


class OrderRepository(BaseRepository[Order]):
    model = Order

    def _base_query(self) -> Select:
        return select(Order).options(
            selectinload(Order.items),
            selectinload(Order.address),
            selectinload(Order.payments),
            selectinload(Order.user),
            selectinload(Order.delivery_partner).selectinload(DeliveryPartner.user),
        )

    async def get_with_details(self, id: uuid.UUID) -> Order | None:
        result = await self.session.execute(self._base_query().where(Order.id == id))
        return result.scalar_one_or_none()

    async def get_for_user(self, order_id: uuid.UUID, user_id: uuid.UUID) -> Order | None:
        result = await self.session.execute(
            self._base_query().where(Order.id == order_id, Order.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def list_for_user(self, user_id: uuid.UUID, limit: int = 50, offset: int = 0) -> list[Order]:
        result = await self.session.execute(
            self._base_query()
            .where(Order.user_id == user_id)
            .order_by(Order.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def count_orders_for_user_and_coupon(self, user_id: uuid.UUID, coupon_id: uuid.UUID) -> int:
        result = await self.session.execute(
            select(Order).where(Order.user_id == user_id, Order.coupon_id == coupon_id)
        )
        return len(result.scalars().all())

    async def list_by_statuses(
        self, statuses: list[OrderStatus], limit: int = 100, offset: int = 0
    ) -> list[Order]:
        result = await self.session.execute(
            self._base_query()
            .where(Order.status.in_(statuses))
            .order_by(Order.created_at.asc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def list_for_delivery_partner(
        self, delivery_partner_id: uuid.UUID, statuses: list[OrderStatus] | None = None
    ) -> list[Order]:
        query = self._base_query().where(Order.delivery_partner_id == delivery_partner_id)
        if statuses:
            query = query.where(Order.status.in_(statuses))
        result = await self.session.execute(query.order_by(Order.created_at.asc()))
        return list(result.scalars().all())
