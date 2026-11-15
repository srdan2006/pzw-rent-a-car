from sqlalchemy import exists, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Reservation, Vehicle


async def list_vehicles(
    session: AsyncSession, limit: int, offset: int, category_id: int | None
) -> tuple[list[Vehicle], int]:
    query = select(Vehicle).where(Vehicle.is_active.is_(True))
    if category_id is not None:
        query = query.where(Vehicle.category_id == category_id)

    total = await session.scalar(select(func.count()).select_from(query.subquery()))
    result = await session.scalars(query.order_by(Vehicle.id).limit(limit).offset(offset))
    return list(result), total or 0


async def get_by_id(session: AsyncSession, vehicle_id: int) -> Vehicle | None:
    return await session.get(Vehicle, vehicle_id)


async def get_by_plate(session: AsyncSession, license_plate: str) -> Vehicle | None:
    return await session.scalar(
        select(Vehicle).where(Vehicle.license_plate == license_plate)
    )


async def add(session: AsyncSession, vehicle: Vehicle) -> Vehicle:
    session.add(vehicle)
    await session.flush()
    return vehicle


async def delete(session: AsyncSession, vehicle: Vehicle) -> None:
    await session.delete(vehicle)


async def has_reservations(session: AsyncSession, vehicle_id: int) -> bool:
    return bool(
        await session.scalar(
            select(exists().where(Reservation.vehicle_id == vehicle_id))
        )
    )