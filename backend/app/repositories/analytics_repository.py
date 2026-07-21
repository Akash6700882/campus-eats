from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import OrderStatus
from app.models.order import Order, OrderItem


class AnalyticsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def order_counts_by_status(self) -> dict[str, int]:
        result = await self.session.execute(select(Order.status, func.count()).group_by(Order.status))
        return {status.value: count for status, count in result.all()}

    async def total_revenue(self) -> float:
        result = await self.session.execute(
            select(func.coalesce(func.sum(Order.grand_total), 0)).where(Order.status == OrderStatus.DELIVERED)
        )
        return float(result.scalar_one())

    async def revenue_by_day(self, days: int = 7) -> list[tuple[str, float, int]]:
        since = datetime.now(timezone.utc) - timedelta(days=days - 1)
        day = func.date(Order.delivered_at)
        result = await self.session.execute(
            select(day, func.sum(Order.grand_total), func.count())
            .where(Order.status == OrderStatus.DELIVERED, Order.delivered_at >= since)
            .group_by(day)
            .order_by(day)
        )
        return [(str(d), float(revenue), count) for d, revenue, count in result.all()]

    async def best_selling_foods(self, limit: int = 5) -> list[tuple[str, int, float]]:
        result = await self.session.execute(
            select(
                OrderItem.food_name_snapshot,
                func.sum(OrderItem.quantity),
                func.sum(OrderItem.subtotal),
            )
            .join(Order, Order.id == OrderItem.order_id)
            .where(Order.status == OrderStatus.DELIVERED)
            .group_by(OrderItem.food_name_snapshot)
            .order_by(func.sum(OrderItem.quantity).desc())
            .limit(limit)
        )
        return [(name, int(qty), float(revenue)) for name, qty, revenue in result.all()]

    # --- Date-range report queries ------------------------------------------
    # Unlike the dashboard-summary methods above (all-time / trailing-7-days),
    # these take an explicit [start, end) window for the "Reports" admin tab.
    # Order counts/status breakdown use placed_at (business activity in the
    # period); revenue stays DELIVERED-only (real money), matching
    # total_revenue()'s definition above.

    async def order_counts_by_status_in_range(self, start: datetime, end: datetime) -> dict[str, int]:
        result = await self.session.execute(
            select(Order.status, func.count())
            .where(Order.placed_at >= start, Order.placed_at < end)
            .group_by(Order.status)
        )
        return {status.value: count for status, count in result.all()}

    async def total_revenue_in_range(self, start: datetime, end: datetime) -> float:
        result = await self.session.execute(
            select(func.coalesce(func.sum(Order.grand_total), 0)).where(
                Order.status == OrderStatus.DELIVERED, Order.placed_at >= start, Order.placed_at < end
            )
        )
        return float(result.scalar_one())

    async def revenue_by_day_in_range(self, start: datetime, end: datetime) -> list[tuple[str, float, int]]:
        day = func.date(Order.placed_at)
        result = await self.session.execute(
            select(day, func.sum(Order.grand_total), func.count())
            .where(Order.status == OrderStatus.DELIVERED, Order.placed_at >= start, Order.placed_at < end)
            .group_by(day)
            .order_by(day)
        )
        return [(str(d), float(revenue), count) for d, revenue, count in result.all()]

    async def best_selling_foods_in_range(
        self, start: datetime, end: datetime, limit: int = 5
    ) -> list[tuple[str, int, float]]:
        result = await self.session.execute(
            select(
                OrderItem.food_name_snapshot,
                func.sum(OrderItem.quantity),
                func.sum(OrderItem.subtotal),
            )
            .join(Order, Order.id == OrderItem.order_id)
            .where(Order.status == OrderStatus.DELIVERED, Order.placed_at >= start, Order.placed_at < end)
            .group_by(OrderItem.food_name_snapshot)
            .order_by(func.sum(OrderItem.quantity).desc())
            .limit(limit)
        )
        return [(name, int(qty), float(revenue)) for name, qty, revenue in result.all()]
