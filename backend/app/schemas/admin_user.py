import uuid
from datetime import datetime

from pydantic import BaseModel


class AdminCustomerResponse(BaseModel):
    id: uuid.UUID
    full_name: str
    email: str
    phone: str
    is_active: bool
    total_orders: int
    total_spend: float
    last_order_at: datetime | None

    @staticmethod
    def from_row(user, total_orders: int, total_spend: float, last_order_at: datetime | None) -> "AdminCustomerResponse":
        return AdminCustomerResponse(
            id=user.id,
            full_name=user.full_name,
            email=user.email,
            phone=user.phone,
            is_active=user.is_active,
            total_orders=total_orders,
            total_spend=total_spend,
            last_order_at=last_order_at,
        )
