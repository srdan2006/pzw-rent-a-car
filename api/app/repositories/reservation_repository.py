from datetime import date

from sqlalchemy import exists, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Reservation
from app.models.reservation import BLOCKING_STATUSES

async def list_reservations(
    session: AsyncSession, limit: int, offset: int, user_id: int | None
) -> tuple[list[Reservation], int]:
    query = select(Reservation)
    if user_id is not None:
        query = query.where(Reservation.user_id == user_id)

    total = await session.scalar(select(func.count()).select_from(query.subquery()))
    result = await session.scalars(
        query.order_by(Reservation.id).limit(limit).offset(offset)
    )
    return list(result), total or 0


async def get_by_id(session: AsyncSession, reservation_id: int) -> Reservation | None:
    return await session.get(Reservation, reservation_id)


async def add(session: AsyncSession, reservation: Reservation) -> Reservation:
    session.add(reservation)
    await session.flush()
    return reservation

async def has_overlap(
    session: AsyncSession, vehicle_id: int, start_date: date, end_date: date
) -> bool:
    return bool(
        await session.scalar(
            select(
                exists().where(
                    Reservation.vehicle_id == vehicle_id,
                    Reservation.status.in_(BLOCKING_STATUSES),
                    Reservation.start_date < end_date,
                    Reservation.end_date > start_date,
                )
            )
        )
    )