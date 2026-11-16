from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict


class ReservationCreate(BaseModel):
    vehicle_id: int
    start_date: date
    end_date: date


class ReservationStatusUpdate(BaseModel):
    status: Literal["confirmed", "active", "returned"]


class ReservationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    vehicle_id: int
    start_date: date
    end_date: date
    total_price: Decimal
    status: str
    created_at: datetime