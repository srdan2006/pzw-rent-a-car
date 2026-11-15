from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.models import Vehicle
from app.repositories import vehicle_repository
from app.schemas.common import Page, PaginationParams
from app.schemas.vehicle import VehicleCreate, VehicleRead, VehicleUpdate
from app.services import category_service


async def list_vehicles(
    session: AsyncSession, pagination: PaginationParams, category_id: int | None
) -> Page[VehicleRead]:
    items, total = await vehicle_repository.list_vehicles(
        session, pagination.limit, pagination.offset, category_id
    )
    return Page[VehicleRead](
        items=[VehicleRead.model_validate(item) for item in items],
        total=total,
        limit=pagination.limit,
        offset=pagination.offset,
    )


async def get_vehicle(session: AsyncSession, vehicle_id: int) -> Vehicle:
    vehicle = await vehicle_repository.get_by_id(session, vehicle_id)
    if vehicle is None:
        raise AppError(404, "VEHICLE_NOT_FOUND", "Vozilo ne postoji.")
    return vehicle


async def _ensure_plate_free(session: AsyncSession, license_plate: str) -> None:
    if await vehicle_repository.get_by_plate(session, license_plate):
        raise AppError(
            409, "LICENSE_PLATE_TAKEN", "Vozilo s tom registracijom već postoji."
        )


async def create_vehicle(session: AsyncSession, data: VehicleCreate) -> Vehicle:
    await category_service.get_category(session, data.category_id)
    await _ensure_plate_free(session, data.license_plate)

    vehicle = await vehicle_repository.add(session, Vehicle(**data.model_dump()))
    await session.commit()
    return vehicle


async def update_vehicle(
    session: AsyncSession, vehicle_id: int, data: VehicleUpdate
) -> Vehicle:
    vehicle = await get_vehicle(session, vehicle_id)
    changes = data.model_dump(exclude_unset=True, exclude_none=True)

    if "category_id" in changes:
        await category_service.get_category(session, changes["category_id"])

    new_plate = changes.get("license_plate")
    if new_plate and new_plate != vehicle.license_plate:
        await _ensure_plate_free(session, new_plate)

    for field, value in changes.items():
        setattr(vehicle, field, value)

    await session.commit()
    return vehicle


async def delete_vehicle(session: AsyncSession, vehicle_id: int) -> None:
    vehicle = await get_vehicle(session, vehicle_id)

    if await vehicle_repository.has_reservations(session, vehicle.id):
        raise AppError(
            409,
            "VEHICLE_HAS_RESERVATIONS",
            "Vozilo ima rezervacije i ne može se obrisati. Deaktivirajte ga.",
        )

    await vehicle_repository.delete(session, vehicle)
    await session.commit()