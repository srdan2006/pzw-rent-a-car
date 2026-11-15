import asyncio
from decimal import Decimal

from sqlalchemy import select

from app.core.database import SessionLocal, engine
from app.core.security import hash_password
from app.models import User, Vehicle, VehicleCategory

USERS = [
    ("admin@rentacar.hr", "Admin Agencije", "admin", "admin123"),
    ("ana@example.com", "Ana Anić", "customer", "ana12345"),
    ("marko@example.com", "Marko Marić", "customer", "marko12345"),
]

CATEGORIES = [
    ("Mali", Decimal("35.00")),
    ("Srednji", Decimal("50.00")),
    ("SUV", Decimal("80.00")),
]

VEHICLES = [
    ("Mali", "Volkswagen", "Polo", "ZD-101-AA", 2021),
    ("Mali", "Renault", "Clio", "ZD-102-AA", 2022),
    ("Srednji", "Škoda", "Octavia", "ZD-201-BB", 2023),
    ("Srednji", "Toyota", "Corolla", "ZD-202-BB", 2022),
    ("SUV", "Dacia", "Duster", "ZD-301-CC", 2024),
]


async def seed() -> None:
    async with SessionLocal() as session:
        for email, full_name, role, password in USERS:
            existing = await session.scalar(select(User).where(User.email == email))
            if existing is None:
                session.add(
                    User(
                        email=email,
                        full_name=full_name,
                        role=role,
                        password_hash=hash_password(password),
                    )
                )

        for name, daily_price in CATEGORIES:
            existing = await session.scalar(
                select(VehicleCategory).where(VehicleCategory.name == name)
            )
            if existing is None:
                session.add(VehicleCategory(name=name, daily_price=daily_price))

        await session.flush()

        for category_name, brand, model, plate, year in VEHICLES:
            existing = await session.scalar(
                select(Vehicle).where(Vehicle.license_plate == plate)
            )
            if existing is None:
                category = await session.scalar(
                    select(VehicleCategory).where(VehicleCategory.name == category_name)
                )
                session.add(
                    Vehicle(
                        category_id=category.id,
                        brand=brand,
                        model=model,
                        license_plate=plate,
                        year=year,
                    )
                )

        await session.commit()

    await engine.dispose()
    print("Početni podaci su upisani.")


if __name__ == "__main__":
    asyncio.run(seed())