from fastapi import APIRouter, Depends

from app.core.deps import DbSession, DeliveryPartnerRepo, UserRepo, require_role
from app.models.enums import RoleName
from app.repositories.analytics_repository import AnalyticsRepository
from app.schemas.analytics import (
    AnalyticsSummaryResponse,
    BestSellingFood,
    DailyRevenue,
    OrderStatusCount,
)

router = APIRouter(tags=["analytics"])

RequireAdmin = Depends(require_role(RoleName.ADMIN.value))


@router.get("/admin/analytics/summary", response_model=AnalyticsSummaryResponse, dependencies=[RequireAdmin])
async def analytics_summary(
    db: DbSession, user_repo: UserRepo, delivery_partner_repo: DeliveryPartnerRepo
) -> AnalyticsSummaryResponse:
    analytics_repo = AnalyticsRepository(db)

    status_counts = await analytics_repo.order_counts_by_status()
    total_orders = sum(status_counts.values())
    total_revenue = await analytics_repo.total_revenue()
    revenue_by_day = await analytics_repo.revenue_by_day()
    best_selling = await analytics_repo.best_selling_foods()
    total_customers = await user_repo.count_by_role(RoleName.CUSTOMER.value)
    delivery_partners = await delivery_partner_repo.list_all()

    return AnalyticsSummaryResponse(
        total_orders=total_orders,
        total_revenue=total_revenue,
        total_customers=total_customers,
        total_delivery_partners=len(delivery_partners),
        orders_by_status=[OrderStatusCount(status=s, count=c) for s, c in status_counts.items()],
        revenue_last_7_days=[
            DailyRevenue(date=d, revenue=r, order_count=c) for d, r, c in revenue_by_day
        ],
        best_selling_foods=[
            BestSellingFood(name=n, quantity_sold=q, revenue=r) for n, q, r in best_selling
        ],
    )
