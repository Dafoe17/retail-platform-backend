"""API роуты для заказов"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from decimal import Decimal

from core.database import get_session
from core.schemas import (
    OrderSchema,
    OrderSummarySchema,
    OrderCreateSchema,
    OrderUpdateStatusSchema,
    PaginatedResponse,
    SuccessResponse
)
from core.dependencies import get_current_user, require_admin
from core.models import UserModel
from datetime import datetime

router = APIRouter(prefix="/api/orders", tags=["Orders"])


@router.get("", response_model=PaginatedResponse, summary="Список заказов")
async def list_orders(
    status: Optional[str] = Query(None, description="Фильтр по статусу"),
    page: int = Query(1, ge=1, description="Номер страницы"),
    page_size: int = Query(20, ge=1, le=100, description="Размер страницы"),
    current_user: UserModel = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Получить список заказов текущего пользователя.

    - **status**: Фильтр по статусу (опционально)
    - **page**: Номер страницы
    - **page_size**: Размер страницы
    """
    # TODO: Реализовать запрос к БД
    orders = [
        OrderSummarySchema(
            id=1,
            order_number="ORD-2024-000001",
            status="delivered",
            status_display="Доставлен",
            total=Decimal("64970.00"),
            items_count=1,
            created_at=datetime.utcnow()
        )
    ]

    return PaginatedResponse(
        items=orders,
        total=len(orders),
        page=page,
        page_size=page_size,
        total_pages=1
    )


@router.get("/{order_id}", response_model=OrderSchema, summary="Детали заказа")
async def get_order(
    order_id: int,
    current_user: UserModel = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Получить детали заказа по ID.

    Пользователь видит только свои заказы.
    """
    # TODO: Реализовать запрос к БД
    from core.schemas import AddressSchema

    return OrderSchema(
        id=order_id,
        order_number="ORD-2024-000001",
        user_id=current_user.id,
        status="delivered",
        status_display="Доставлен",
        items=[],
        subtotal=Decimal("59980.00"),
        shipping_cost=Decimal("4990.00"),
        discount=Decimal("0"),
        tax=Decimal("0"),
        total=Decimal("64970.00"),
        shipping_address=AddressSchema(
            recipient_name="Иван Иванов",
            phone="+79001234567",
            country="Россия",
            city="Москва",
            street="Улица Примерная",
            building="123",
            apartment=None,
            postal_code="123456"
        ),
        comment=None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        status_history=[]
    )


@router.post("", response_model=OrderSchema, summary="Создать заказ")
async def create_order(
    data: OrderCreateSchema,
    current_user: UserModel = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Создать новый заказ из корзины.

    - **shipping_address**: Адрес доставки
    - **comment**: Комментарий к заказу (опционально)
    """
    # TODO: Реализовать создание заказа
    # - Получить корзину пользователя
    # - Валидировать товары (наличие, цена)
    # - Создать заказ и элементы
    # - Очистить корзину
    # - Уменьшить stock товаров

    from core.schemas import AddressSchema

    return OrderSchema(
        id=1,
        order_number="ORD-2024-000002",
        user_id=current_user.id,
        status="pending",
        status_display="В ожидании",
        items=[],
        subtotal=Decimal("0"),
        shipping_cost=Decimal("0"),
        discount=Decimal("0"),
        tax=Decimal("0"),
        total=Decimal("0"),
        shipping_address=data.shipping_address,
        comment=data.comment,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        status_history=[]
    )


@router.post("/{order_id}/cancel", response_model=SuccessResponse, summary="Отменить заказ")
async def cancel_order(
    order_id: int,
    current_user: UserModel = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Отменить заказ.

    Заказ можно отменить только в статусах: pending, confirmed.
    """
    # TODO: Реализовать отмену заказа
    # - Проверить статус заказа
    # - Вернуть stock товаров
    # - Изменить статус на cancelled
    return SuccessResponse(message="Order cancelled")


@router.put("/{order_id}/status", response_model=OrderSchema, summary="Обновить статус", dependencies=[Depends(require_admin)])
async def update_order_status(
    order_id: int,
    data: OrderUpdateStatusSchema,
    session: AsyncSession = Depends(get_session)
):
    """
    Обновить статус заказа.

    Требуется роль **admin**.
    """
    # TODO: Реализовать обновление статуса
    # - Проверить валидность перехода статуса
    # - Добавить запись в историю
    from core.schemas import AddressSchema

    return OrderSchema(
        id=order_id,
        order_number="ORD-2024-000001",
        user_id=1,
        status=data.status,
        status_display=data.status.capitalize(),
        items=[],
        subtotal=Decimal("59980.00"),
        shipping_cost=Decimal("4990.00"),
        discount=Decimal("0"),
        tax=Decimal("0"),
        total=Decimal("64970.00"),
        shipping_address=AddressSchema(
            recipient_name="Иван Иванов",
            phone="+79001234567",
            country="Россия",
            city="Москва",
            street="Улица Примерная",
            building="123",
            apartment=None,
            postal_code="123456"
        ),
        comment=data.comment,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        status_history=[]
    )
