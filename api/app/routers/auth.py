from fastapi import APIRouter

from app.core.deps import CurrentUser, SessionDep
from app.models import User
from app.schemas.auth import LoginRequest, RefreshRequest, TokenResponse
from app.schemas.user import UserRead
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, session: SessionDep) -> TokenResponse:
    return await auth_service.login(session, data.email, data.password)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(data: RefreshRequest, session: SessionDep) -> TokenResponse:
    return await auth_service.refresh(session, data.refresh_token)


@router.get("/me", response_model=UserRead)
async def me(user: CurrentUser) -> User:
    return user
