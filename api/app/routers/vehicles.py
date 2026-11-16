from fastapi import APIRouter

from app.core.deps import AdminUser, Pagination, SessionDep
from app.models import Vehicle
from app.schemas.common import Page
from app.schemas.vehicle import VehicleCreate, VehicleRead, VehicleUpdate
from app.services import vehicle_service

router = APIRouter(prefix="/vehicles", tags=["vehicles"])


@router.get("", response_model=Page[VehicleRead])
async def list_vehicles(
    session: SessionDep, pagination: Pagination, category_id: int | None = None
) -> Page[VehicleRead]:
    return await vehicle_service.list_vehicles(session, pagination, category_id)


@router.get("/{vehicle_id}", response_model=VehicleRead)
async def get_vehicle(vehicle_id: int, session: SessionDep) -> Vehicle:
    return await vehicle_service.get_vehicle(session, vehicle_id)


@router.post("", response_model=VehicleRead, status_code=201)
async def create_vehicle(
    data: VehicleCreate, session: SessionDep, _: AdminUser
) -> Vehicle:
    return await vehicle_service.create_vehicle(session, data)


@router.patch("/{vehicle_id}", response_model=VehicleRead)
async def update_vehicle(
    vehicle_id: int, data: VehicleUpdate, session: SessionDep, _: AdminUser
) -> Vehicle:
    return await vehicle_service.update_vehicle(session, vehicle_id, data)


@router.delete("/{vehicle_id}", status_code=204)
async def delete_vehicle(vehicle_id: int, session: SessionDep, _: AdminUser) -> None:
    await vehicle_service.delete_vehicle(session, vehicle_id)
