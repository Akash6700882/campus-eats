import uuid

from sqlalchemy import Boolean, Float, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.models.mixins import TimestampMixin


class DeliveryZone(Base, TimestampMixin):
    """Campus geofence. `polygon_geojson` stores a GeoJSON Polygon
    (list of [lng, lat] pairs) used for point-in-polygon delivery checks —
    see app/services/geofence.py (added in Phase 4)."""

    __tablename__ = "delivery_zones"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    polygon_geojson: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class DeliveryPartner(Base, TimestampMixin):
    __tablename__ = "delivery_partners"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False
    )
    vehicle_number: Mapped[str | None] = mapped_column(String(20))

    is_available: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    current_latitude: Mapped[float | None] = mapped_column(Float)
    current_longitude: Mapped[float | None] = mapped_column(Float)

    rating_avg: Mapped[float] = mapped_column(Numeric(3, 2), default=0)
    total_deliveries: Mapped[int] = mapped_column(Integer, default=0)
    today_earnings: Mapped[float] = mapped_column(Numeric(10, 2), default=0)

    user: Mapped["User"] = relationship(back_populates="delivery_partner_profile")
    orders: Mapped[list["Order"]] = relationship(back_populates="delivery_partner")
