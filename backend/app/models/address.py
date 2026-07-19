import uuid

from sqlalchemy import Boolean, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.models.mixins import TimestampMixin


class Address(Base, TimestampMixin):
    __tablename__ = "addresses"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    label: Mapped[str] = mapped_column(String(50), default="Hostel")
    building: Mapped[str | None] = mapped_column(String(120))
    hostel: Mapped[str | None] = mapped_column(String(120))
    block: Mapped[str | None] = mapped_column(String(50))
    room_number: Mapped[str | None] = mapped_column(String(20))
    department: Mapped[str | None] = mapped_column(String(120))
    notes: Mapped[str | None] = mapped_column(String(255))

    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)

    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    user: Mapped["User"] = relationship(back_populates="addresses")
