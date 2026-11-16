from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.models import VehicleCategory
from app.repositories import category_repository
from app.schemas.category import CategoryCreate, CategoryRead, CategoryUpdate
from app.schemas.common import Page, PaginationParams


async def list_categories(
    session: AsyncSession, pagination: PaginationParams
) -> Page[CategoryRead]:
    items, total = await category_repository.list_categories(
        session, pagination.limit, pagination.offset
    )
    return Page[CategoryRead](
        items=[CategoryRead.model_validate(item) for item in items],
        total=total,
        limit=pagination.limit,
        offset=pagination.offset,
    )


async def get_category(session: AsyncSession, category_id: int) -> VehicleCategory:
    category = await category_repository.get_by_id(session, category_id)
    if category is None:
        raise AppError(404, "CATEGORY_NOT_FOUND", "Kategorija ne postoji.")
    return category


async def create_category(
    session: AsyncSession, data: CategoryCreate
) -> VehicleCategory:
    if await category_repository.get_by_name(session, data.name):
        raise AppError(409, "CATEGORY_NAME_TAKEN", "Kategorija s tim imenom već postoji.")

    category = await category_repository.add(session, VehicleCategory(**data.model_dump()))
    await session.commit()
    await session.refresh(category)
    return category


async def update_category(
    session: AsyncSession, category_id: int, data: CategoryUpdate
) -> VehicleCategory:
    category = await get_category(session, category_id)
    changes = data.model_dump(exclude_unset=True, exclude_none=True)

    new_name = changes.get("name")
    if new_name and new_name != category.name:
        if await category_repository.get_by_name(session, new_name):
            raise AppError(
                409, "CATEGORY_NAME_TAKEN", "Kategorija s tim imenom već postoji."
            )

    for field, value in changes.items():
        setattr(category, field, value)

    await session.commit()
    await session.refresh(category)
    return category


async def delete_category(session: AsyncSession, category_id: int) -> None:
    category = await get_category(session, category_id)

    if await category_repository.has_vehicles(session, category.id):
        raise AppError(
            409, "CATEGORY_HAS_VEHICLES", "Kategorija ima vozila i ne može se obrisati."
        )

    await category_repository.delete(session, category)
    await session.commit()