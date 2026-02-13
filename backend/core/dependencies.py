"""Зависимости для FastAPI (Dependency Injection)"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from jose import jwt, JWTError

from .database import get_session
from .config import get_settings
from .models import UserModel

settings = get_settings()
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_session)
) -> UserModel:
    """Получить текущего пользователя по JWT токену"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    # TODO: Загрузить пользователя из БД
    # user = await session.get(UserModel, user_id)
    # if user is None or not user.is_active:
    #     raise HTTPException(status_code=401, detail="User not found")

    # Заглушка
    user = UserModel(id=user_id, email="user@example.com", is_active=True, role="customer")

    return user


async def require_admin(current_user: UserModel = Depends(get_current_user)) -> UserModel:
    """Требуется роль admin"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user
