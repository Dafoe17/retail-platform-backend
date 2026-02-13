"""API роуты для авторизации"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_session
from core.schemas import (
    UserRegisterSchema,
    UserLoginSchema,
    UserWithTokensSchema,
    TokensResponseSchema,
    UserSchema,
    SuccessResponse
)
from core.dependencies import get_current_user, require_admin
from core.models import UserModel

router = APIRouter(prefix="/api/auth", tags=["Auth"])


@router.post("/register", response_model=UserWithTokensSchema, summary="Регистрация")
async def register(
    data: UserRegisterSchema,
    session: AsyncSession = Depends(get_session)
):
    """
    Регистрация нового пользователя.

    - **email**: Email адрес (уникальный)
    - **password**: Пароль (минимум 8 символов)
    - **first_name**: Имя (опционально)
    - **last_name**: Фамилия (опционально)

    Возвращает пользователя с JWT токенами.
    """
    # TODO: Реализовать регистрацию в БД
    # Заглушка
    from datetime import datetime, timedelta
    from jose import jwt
    from core.config import get_settings

    settings = get_settings()

    user = UserModel(
        id=1,
        email=data.email,
        role="customer",
        is_active=True,
        is_verified=True,
        created_at=datetime.utcnow()
    )

    # Генерация токенов
    access_payload = {
        "sub": str(user.id),
        "email": user.email,
        "role": user.role,
        "type": "access"
    }
    access_token = jwt.encode(access_payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    refresh_payload = {
        "sub": str(user.id),
        "type": "refresh"
    }
    refresh_token = jwt.encode(refresh_payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    tokens = TokensResponseSchema(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

    return UserWithTokensSchema(
        id=user.id,
        email=user.email,
        role=user.role,
        is_active=user.is_active,
        is_verified=user.is_verified,
        created_at=user.created_at,
        tokens=tokens
    )


@router.post("/login", response_model=TokensResponseSchema, summary="Логин")
async def login(
    data: UserLoginSchema,
    session: AsyncSession = Depends(get_session)
):
    """
    Аутентификация пользователя.

    - **email**: Email адрес
    - **password**: Пароль

    Возвращает JWT токены (access + refresh).
    """
    # TODO: Реализовать проверку пароля
    from jose import jwt
    from core.config import get_settings

    settings = get_settings()

    # Заглушка - всегда успешный логин
    access_payload = {
        "sub": "1",
        "email": data.email,
        "role": "customer",
        "type": "access"
    }
    access_token = jwt.encode(access_payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    refresh_payload = {
        "sub": "1",
        "type": "refresh"
    }
    refresh_token = jwt.encode(refresh_payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    return TokensResponseSchema(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post("/logout", response_model=SuccessResponse, summary="Логаут")
async def logout(
    current_user: UserModel = Depends(get_current_user)
):
    """
    Выход из системы.

    Отзывает refresh токен (текущий).
    """
    # TODO: Реализовать отзыв токена
    return SuccessResponse(message="Logged out successfully")


@router.get("/me", response_model=UserSchema, summary="Текущий пользователь")
async def get_me(
    current_user: UserModel = Depends(get_current_user)
):
    """
    Получить информацию о текущем пользователе.

    Требуется JWT токен в заголовке Authorization.
    """
    return UserSchema(
        id=current_user.id,
        email=current_user.email,
        role=current_user.role,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        created_at=current_user.created_at,
        last_login_at=current_user.last_login_at
    )
