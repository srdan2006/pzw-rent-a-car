from sqlalchemy import exists, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Vehicle, VehicleCategory


async def list_categories(
    session: AsyncSession, limit: int, offset: int
) -> tuple[list[VehicleCategory], int]:
    total = await session.scalar(select(func.count()).select_from(VehicleCategory))
    result = await session.scalars(
        select(VehicleCategory).order_by(VehicleCategory.id).limit(limit).offset(offset)
    )
    return list(result), total or 0


async def get_by_id(session: AsyncSession, category_id: int) -> VehicleCategory | None:
    return await session.get(VehicleCategory, category_id)


async def get_by_name(session: AsyncSession, name: str) -> VehicleCategory | None:
    return await session.scalar(
        select(VehicleCategory).where(VehicleCategory.name == name)
    )


async def add(session: AsyncSession, category: VehicleCategory) -> VehicleCategory:
    session.add(category)
    await session.flush()
    return category


async def delete(session: AsyncSession, category: VehicleCategory) -> None:
    await session.delete(category)


async def has_vehicles(session: AsyncSession, category_id: int) -> bool:
    return bool(
        await session.scalar(select(exists().where(Vehicle.category_id == category_id)))
    )