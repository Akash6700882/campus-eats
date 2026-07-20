from pydantic import BaseModel


class OrderStatusCount(BaseModel):
    status: str
    count: int


class DailyRevenue(BaseModel):
    date: str
    revenue: float
    order_count: int


class BestSellingFood(BaseModel):
    name: str
    quantity_sold: int
    revenue: float


class AnalyticsSummaryResponse(BaseModel):
    total_orders: int
    total_revenue: float
    total_customers: int
    total_delivery_partners: int
    orders_by_status: list[OrderStatusCount]
    revenue_last_7_days: list[DailyRevenue]
    best_selling_foods: list[BestSellingFood]
