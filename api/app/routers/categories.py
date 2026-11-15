from fastapi import APIRouter

from app.core.deps import AdminUser, Pagination, SessionDep
from app.models import VehicleCategory
from app.schemas.category import CategoryCreate, CategoryRead, CategoryUpdate
from app.schemas.common import Page
from app.services import category_service

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=Page[CategoryRead])
async def list_categories(
    session: SessionDep, pagination: Pagination
) -> Page[CategoryRead]:
    return await category_service.list_categories(session, pagination)


@router.get("/{category_id}", response_model=CategoryRead)
async def get_category(category_id: int, session: SessionDep) -> VehicleCategory:
    return await category_service.get_category(session, category_id)


@router.post("", response_model=CategoryRead, status_code=201)
async def create_category(
    data: CategoryCreate, session: SessionDep, _: AdminUser
) -> VehicleCategory:
    return await category_service.create_category(session, data)


@router.patch("/{category_id}", response_model=CategoryRead)
async def update_category(
    category_id: int, data: CategoryUpdate, session: SessionDep, _: AdminUser
) -> VehicleCategory:
    return await category_service.update_category(session, category_id, data)


@router.delete("/{category_id}", status_code=204)
async def delete_category(category_id: int, session: SessionDep, _: AdminUser) -> None:
    await category_service.delete_category(session, category_id)