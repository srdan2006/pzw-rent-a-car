from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, true
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.vehicle_category import VehicleCategory


class Vehicle(Base):
    __tablename__ = "vehicles"

    id: Mapped[int] = mapped_column(primary_key=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("vehicle_categories.id"))
    brand: Mapped[str] = mapped_column(String(50))
    model: Mapped[str] = mapped_column(String(50))
    license_plate: Mapped[str] = mapped_column(String(20), unique=True)
    year: Mapped[int]
    is_active: Mapped[bool] = mapped_column(server_default=true())

    category: Mapped["VehicleCategory"] = relationship(back_populates="vehicles")