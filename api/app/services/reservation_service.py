from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.models import Reservation, User
from app.repositories import reservation_repository
from app.schemas.common import Page, PaginationParams
from app.schemas.reservation import ReservationCreate, ReservationRead
from app.services import category_service, vehicle_service


def _is_admin(user: User) -> bool:
    return user.role == "admin"


async def list_reservations(
    session: AsyncSession, user: User, pagination: PaginationParams
) -> Page[ReservationRead]:
    owner_id = None if _is_admin(user) else user.id
    items, total = await reservation_repository.list_reservations(
        session, pagination.limit, pagination.offset, owner_id
    )
    return Page[ReservationRead](
        items=[ReservationRead.model_validate(item) for item in items],
        total=total,
        limit=pagination.limit,
        offset=pagination.offset,
    )


async def get_reservation(
    session: AsyncSession, reservation_id: int, user: User
) -> Reservation:
    reservation = await reservation_repository.get_by_id(session, reservation_id)

    if reservation is None or (
        not _is_admin(user) and reservation.user_id != user.id
    ):
        raise AppError(404, "RESERVATION_NOT_FOUND", "Rezervacija ne postoji.")

    return reservation


async def create_reservation(
    session: AsyncSession, data: ReservationCreate, user: User
) -> Reservation:
    if data.end_date <= data.start_date:
        raise AppError(
            400,
            "INVALID_DATE_RANGE",
            "Datum povratka mora biti nakon datuma preuzimanja.",
        )
    if data.start_date < date.today():
        raise AppError(
            400, "START_DATE_IN_PAST", "Rezervacija ne može početi u prošlosti."
        )

    vehicle = await vehicle_service.get_vehicle(session, data.vehicle_id)
    if not vehicle.is_active:
        raise AppError(409, "VEHICLE_INACTIVE", "Vozilo trenutno nije u ponudi.")

    category = await category_service.get_category(session, vehicle.category_id)
    days = (data.end_date - data.start_date).days

    if await reservation_repository.has_overlap(session, vehicle.id, data.start_date, data.end_date):
        raise AppError(409, "VEHICLE_NOT_AVAILABLE", "Vozilo je već rezervirano u tom terminu.")

    reservation = await reservation_repository.add(
        session,
        Reservation(
            user_id=user.id,
            vehicle_id=vehicle.id,
            start_date=data.start_date,
            end_date=data.end_date,
            total_price=category.daily_price * days,
        ),
    )
    await session.commit()
    return reservation