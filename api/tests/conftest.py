from decimal import Decimal

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import settings
from app.core.database import get_session
from app.core.security import hash_password
from app.main import app
from app.models import Base, User, Vehicle, VehicleCategory

assert settings.test_database_url, "U .env nedostaje TEST_DATABASE_URL"

engine = create_async_engine(settings.test_database_url, poolclass=NullPool)
TestSession = async_sessionmaker(engine, expire_on_commit=False)

PASSWORDS = {
    "admin@test.hr": "admin123",
    "ana@test.hr": "ana12345",
    "marko@test.hr": "marko12345",
}


@pytest.fixture(scope="session", autouse=True)
async def create_schema():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


@pytest.fixture(scope="session")
def password_hashes() -> dict[str, str]:
    return {email: hash_password(password) for email, password in PASSWORDS.items()}


@pytest.fixture(autouse=True)
async def seed_data(create_schema, password_hashes):
    async with engine.begin() as conn:
        await conn.execute(
            text(
                "TRUNCATE reservations, vehicles, vehicle_categories, users "
                "RESTART IDENTITY CASCADE"
            )
        )

    async with TestSession() as session:
        session.add_all(
            [
                User(email="admin@test.hr", full_name="Admin", role="admin",
                     password_hash=password_hashes["admin@test.hr"]),
                User(email="ana@test.hr", full_name="Ana", role="customer",
                     password_hash=password_hashes["ana@test.hr"]),
                User(email="marko@test.hr", full_name="Marko", role="customer",
                     password_hash=password_hashes["marko@test.hr"]),
                VehicleCategory(name="Mali", daily_price=Decimal("35.00")),
            ]
        )
        await session.flush()
        session.add(
            Vehicle(category_id=1, brand="Volkswagen", model="Polo",
                    license_plate="ZD-001-AA", year=2022)
        )
        await session.commit()


async def override_get_session():
    async with TestSession() as session:
        yield session


@pytest.fixture
async def client():
    app.dependency_overrides[get_session] = override_get_session
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as c:
        yield c
    app.dependency_overrides.clear()


async def login_headers(client: AsyncClient, email: str) -> dict[str, str]:
    response = await client.post(
        "/auth/login", json={"email": email, "password": PASSWORDS[email]}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def admin_headers(client):
    return await login_headers(client, "admin@test.hr")


@pytest.fixture
async def ana_headers(client):
    return await login_headers(client, "ana@test.hr")


@pytest.fixture
async def marko_headers(client):
    return await login_headers(client, "marko@test.hr")