from pydantic import BaseModel, ConfigDict, Field


class VehicleCreate(BaseModel):
    category_id: int
    brand: str = Field(min_length=1, max_length=50)
    model: str = Field(min_length=1, max_length=50)
    license_plate: str = Field(min_length=1, max_length=20)
    year: int = Field(ge=1990, le=2100)


class VehicleUpdate(BaseModel):
    category_id: int | None = None
    brand: str | None = Field(None, min_length=1, max_length=50)
    model: str | None = Field(None, min_length=1, max_length=50)
    license_plate: str | None = Field(None, min_length=1, max_length=20)
    year: int | None = Field(None, ge=1990, le=2100)
    is_active: bool | None = None


class VehicleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    category_id: int
    brand: str
    model: str
    license_plate: str
    year: int
    is_active: bool
