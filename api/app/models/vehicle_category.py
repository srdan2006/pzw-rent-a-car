from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.vehicle import Vehicle


class VehicleCategory(Base):
    __tablename__ = "vehicle_categories"
    __table_args__ = (
        CheckConstraint("daily_price > 0", name="daily_price_positive"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    daily_price: Mapped[Decimal] = mapped_column(Numeric(10, 2))

    vehicles: Mapped[list["Vehicle"]] = relationship(back_populates="category")