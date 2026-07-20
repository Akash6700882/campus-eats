import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.cart import CartItem
    from app.models.category import Category
    from app.models.inventory import InventoryItem
    from app.models.order import OrderItem
    from app.models.review import Review, WishlistItem


class Food(Base, TimestampMixin):
    __tablename__ = "foods"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("categories.id"), nullable=False
    )

    name: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    slug: Mapped[str] = mapped_column(String(140), unique=True, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text)
    image_url: Mapped[str | None] = mapped_column(String(500))

    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    discount_percent: Mapped[float] = mapped_column(Numeric(5, 2), default=0)

    is_veg: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    prep_time_minutes: Mapped[int] = mapped_column(Integer, default=10)

    rating_avg: Mapped[float] = mapped_column(Numeric(3, 2), default=0)
    rating_count: Mapped[int] = mapped_column(Integer, default=0)

    is_available: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_popular: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_special_today: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    category: Mapped["Category"] = relationship(back_populates="foods")
    order_items: Mapped[list["OrderItem"]] = relationship(back_populates="food")
    cart_items: Mapped[list["CartItem"]] = relationship(back_populates="food", cascade="all, delete-orphan")
    reviews: Mapped[list["Review"]] = relationship(back_populates="food", cascade="all, delete-orphan")
    wishlist_items: Mapped[list["WishlistItem"]] = relationship(
        back_populates="food", cascade="all, delete-orphan"
    )
    inventory: Mapped["InventoryItem | None"] = relationship(
        back_populates="food", cascade="all, delete-orphan"
    )

    @property
    def discounted_price(self) -> float:
        return round(float(self.price) * (1 - float(self.discount_percent) / 100), 2)
