from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class ReservationCreate(BaseModel):
    vehicle_id: int
    start_date: date
    end_date: date


class ReservationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    vehicle_id: int
    start_date: date
    end_date: date
    total_price: Decimal
    created_at: datetime