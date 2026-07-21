import uuid

from sqlalchemy import Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base
from app.models.mixins import TimestampMixin


class AppSettings(Base, TimestampMixin):
    """Singleton row (there's only ever one, created lazily on first read)
    holding admin-editable business settings that used to be fixed .env
    values. gst_percent/delivery_charge/packing_charge are read live by both
    CartService (checkout preview) and OrderService (the actual charge), so
    an admin edit here takes effect immediately. business_hours_* are
    informational only — not yet enforced against checkout."""

    __tablename__ = "app_settings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    restaurant_name: Mapped[str] = mapped_column(String(120), default="Campus Eats", nullable=False)
    gst_percent: Mapped[float] = mapped_column(Numeric(5, 2), default=5.0, nullable=False)
    delivery_charge: Mapped[float] = mapped_column(Numeric(10, 2), default=15.0, nullable=False)
    packing_charge: Mapped[float] = mapped_column(Numeric(10, 2), default=5.0, nullable=False)
    business_hours_open: Mapped[str] = mapped_column(String(5), default="09:00", nullable=False)
    business_hours_close: Mapped[str] = mapped_column(String(5), default="22:00", nullable=False)
