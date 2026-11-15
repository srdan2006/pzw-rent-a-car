from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    daily_price: Decimal = Field(gt=0, max_digits=10, decimal_places=2)


class CategoryUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=50)
    daily_price: Decimal | None = Field(None, gt=0, max_digits=10, decimal_places=2)


class CategoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    daily_price: Decimal