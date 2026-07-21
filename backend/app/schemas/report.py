import enum

from pydantic import BaseModel

from app.schemas.analytics import BestSellingFood, DailyRevenue, OrderStatusCount


class ReportPeriod(str, enum.Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"


class ReportFormat(str, enum.Enum):
    JSON = "json"
    CSV = "csv"
    EXCEL = "excel"
    PDF = "pdf"


class ReportResponse(BaseModel):
    period: ReportPeriod
    start_date: str
    end_date: str
    total_orders: int
    total_revenue: float
    orders_by_status: list[OrderStatusCount]
    best_selling_foods: list[BestSellingFood]
    daily_breakdown: list[DailyRevenue]
