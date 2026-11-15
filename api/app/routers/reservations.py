from fastapi import APIRouter

from app.core.deps import CurrentUser, Pagination, SessionDep
from app.models import Reservation
from app.schemas.common import Page
from app.schemas.reservation import ReservationCreate, ReservationRead
from app.services import reservation_service

router = APIRouter(prefix="/reservations", tags=["reservations"])


@router.get("", response_model=Page[ReservationRead])
async def list_reservations(
    session: SessionDep, user: CurrentUser, pagination: Pagination
) -> Page[ReservationRead]:
    return await reservation_service.list_reservations(session, user, pagination)


@router.get("/{reservation_id}", response_model=ReservationRead)
async def get_reservation(
    reservation_id: int, session: SessionDep, user: CurrentUser
) -> Reservation:
    return await reservation_service.get_reservation(session, reservation_id, user)


@router.post("", response_model=ReservationRead, status_code=201)
async def create_reservation(
    data: ReservationCreate, session: SessionDep, user: CurrentUser
) -> Reservation:
    return await reservation_service.create_reservation(session, data, user)