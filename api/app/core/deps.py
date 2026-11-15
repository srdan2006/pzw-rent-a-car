from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.errors import AppError
from app.core.security import decode_token
from app.models import User
from app.repositories import user_repository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

SessionDep = Annotated[AsyncSession, Depends(get_session)]


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: SessionDep,
) -> User:
    payload = decode_token(token, "access")
    user = await user_repository.get_by_id(session, int(payload["sub"]))
    if user is None:
        raise AppError(401, "INVALID_TOKEN", "Token nije valjan ili je istekao.")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_role(*roles: str):
    async def checker(user: CurrentUser) -> User:
        if user.role not in roles:
            raise AppError(403, "FORBIDDEN", "Nemate ovlasti za ovu radnju.")
        return user

    return checker


AdminUser = Annotated[User, Depends(require_role("admin"))]