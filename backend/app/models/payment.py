import uuid

from sqlalchemy import Enum, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.models.enums import PaymentMethod, PaymentStatus
from app.models.mixins import TimestampMixin


class Payment(Base, TimestampMixin):
    __tablename__ = "payments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("orders.id"), nullable=False)

    provider: Mapped[str] = mapped_column(String(30), default="razorpay")
    provider_order_id: Mapped[str | None] = mapped_column(String(100), index=True)
    provider_payment_id: Mapped[str | None] = mapped_column(String(100), index=True)
    provider_signature: Mapped[str | None] = mapped_column(String(255))

    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(5), default="INR")
    method: Mapped[PaymentMethod | None] = mapped_column(Enum(PaymentMethod, name="payment_method"))
    status: Mapped[PaymentStatus] = mapped_column(
        Enum(PaymentStatus, name="payment_status"), default=PaymentStatus.CREATED, nullable=False
    )

    failure_reason: Mapped[str | None] = mapped_column(String(255))

    order: Mapped["Order"] = relationship(back_populates="payments")
