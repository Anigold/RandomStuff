from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session

from apps.api.auth.passwords import verify_password
from apps.api.auth.tokens import AuthTokenError, create_token, decode_token
from apps.api.dependencies import get_db_session, get_settings
from apps.api.schemas.auth_schema import (
    AuthTokenResponseSchema,
    CurrentUserSchema,
    LoginRequestSchema,
    LogoutResponseSchema,
)
from workbot_core.config.settings import Settings
from workbot_core.domain.models.user import User
from workbot_core.infrastructure.database.repositories.user_repository import (
    SqlUserRepository,
)


router = APIRouter(prefix="/auth", tags=["auth"])


def user_to_schema(user: User) -> CurrentUserSchema:
    return CurrentUserSchema(
        id=user.id,
        username=user.username,
        email=getattr(user, "email", None),
        display_name=getattr(user, "display_name", None),
    )


def set_refresh_cookie(
    *,
    response: Response,
    refresh_token: str,
    settings: Settings,
) -> None:
    response.set_cookie(
        key=settings.auth_refresh_cookie_name,
        value=refresh_token,
        httponly=True,
        secure=settings.auth_cookie_secure,
        samesite=settings.auth_cookie_samesite,
        max_age=60 * 60 * 24 * settings.auth_refresh_token_days,
        path="/api/auth",
    )


def clear_refresh_cookie(
    *,
    response: Response,
    settings: Settings,
) -> None:
    response.delete_cookie(
        key=settings.auth_refresh_cookie_name,
        path="/api/auth",
    )


def create_auth_response(
    *,
    user: User,
    response: Response,
    settings: Settings,
) -> AuthTokenResponseSchema:
    access_token = create_token(
        user_id=user.id,
        token_type="access",
        secret_key=settings.auth_secret_key,
        algorithm=settings.auth_jwt_algorithm,
        expires_delta=timedelta(minutes=settings.auth_access_token_minutes),
    )

    refresh_token = create_token(
        user_id=user.id,
        token_type="refresh",
        secret_key=settings.auth_secret_key,
        algorithm=settings.auth_jwt_algorithm,
        expires_delta=timedelta(days=settings.auth_refresh_token_days),
    )

    set_refresh_cookie(
        response=response,
        refresh_token=refresh_token,
        settings=settings,
    )

    return AuthTokenResponseSchema(
        access_token=access_token,
        user=user_to_schema(user),
    )


@router.post("/login", response_model=AuthTokenResponseSchema)
def login(
    request: LoginRequestSchema,
    response: Response,
    db: Session = Depends(get_db_session),
    settings: Settings = Depends(get_settings),
) -> AuthTokenResponseSchema:
    user_repository = SqlUserRepository(db)
    user = user_repository.get_by_username(request.username)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    if not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    return create_auth_response(
        user=user,
        response=response,
        settings=settings,
    )


@router.post("/refresh", response_model=AuthTokenResponseSchema)
def refresh(
    request: Request,
    response: Response,
    db: Session = Depends(get_db_session),
    settings: Settings = Depends(get_settings),
) -> AuthTokenResponseSchema:
    refresh_token = request.cookies.get(settings.auth_refresh_cookie_name)

    if refresh_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing refresh token",
        )

    try:
        payload = decode_token(
            token=refresh_token,
            expected_token_type="refresh",
            secret_key=settings.auth_secret_key,
            algorithm=settings.auth_jwt_algorithm,
        )
    except AuthTokenError:
        clear_refresh_cookie(response=response, settings=settings)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    user_repository = SqlUserRepository(db)
    user = user_repository.get_by_id(payload.sub)

    if user is None:
        clear_refresh_cookie(response=response, settings=settings)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return create_auth_response(
        user=user,
        response=response,
        settings=settings,
    )


@router.post("/logout", response_model=LogoutResponseSchema)
def logout(
    response: Response,
    settings: Settings = Depends(get_settings),
) -> LogoutResponseSchema:
    clear_refresh_cookie(
        response=response,
        settings=settings,
    )

    return LogoutResponseSchema(ok=True)