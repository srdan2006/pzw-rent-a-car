from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
)
from app.repositories import user_repository
from app.schemas.auth import TokenResponse


async def login(session: AsyncSession, email: str, password: str) -> TokenResponse:
    user = await user_repository.get_by_email(session, email)

    if user is None or not verify_password(password, user.password_hash):
        raise AppError(401, "INVALID_CREDENTIALS", "Pogrešan email ili lozinka.")

    return TokenResponse(
        access_token=create_access_token(user.id, user.role),
        refresh_token=create_refresh_token(user.id, user.role),
    )


async def refresh(session: AsyncSession, refresh_token: str) -> TokenResponse:
    payload = decode_token(refresh_token, "refresh")
    user = await user_repository.get_by_id(session, int(payload["sub"]))
    if user is None:
        raise AppError(401, "INVALID_TOKEN", "Token nije valjan ili je istekao.")

    return TokenResponse(
        access_token=create_access_token(user.id, user.role),
        refresh_token=create_refresh_token(user.id, user.role),
    )
