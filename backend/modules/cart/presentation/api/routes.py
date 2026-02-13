"""API роуты для корзины"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_session
from core.schemas import (
    CartSchema,
    CartItemAddSchema,
    CartItemUpdateSchema,
    SuccessResponse
)
from core.dependencies import get_current_user
from core.models import UserModel
from datetime import datetime
from decimal import Decimal

router = APIRouter(prefix="/api/cart", tags=["Cart"])


@router.get("", response_model=CartSchema, summary="Получить корзину")
async def get_cart(
    current_user: UserModel = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Получить текущую корзину пользователя.

    Если корзина не существует - создается пустая.
    """
    # TODO: Реализовать запрос к БД
    return CartSchema(
        id=1,
        user_id=current_user.id,
        items=[],
        total=Decimal("0"),
        items_count=0,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )


@router.post("/items", response_model=CartSchema, summary="Добавить товар в корзину")
async def add_item(
    data: CartItemAddSchema,
    current_user: UserModel = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Добавить товар в корзину.

    - **product_id**: ID товара
    - **quantity**: Количество (1-99)

    Если товар уже есть - увеличивает количество.
    """
    # TODO: Реализовать добавление товара в корзину
    # - Проверить существование товара
    # - Проверить наличие на складе
    # - Добавить или обновить элемент корзины

    return CartSchema(
        id=1,
        user_id=current_user.id,
        items=[],
        total=Decimal("0"),
        items_count=data.quantity,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )


@router.put("/items/{item_id}", response_model=CartSchema, summary="Обновить количество товара")
async def update_item_quantity(
    item_id: int,
    data: CartItemUpdateSchema,
    current_user: UserModel = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Обновить количество товара в корзине.

    - **quantity**: Новое количество (1-99)

    Если quantity=0 - товар удаляется из корзины.
    """
    # TODO: Реализовать обновление количества
    return CartSchema(
        id=1,
        user_id=current_user.id,
        items=[],
        total=Decimal("0"),
        items_count=data.quantity,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )


@router.delete("/items/{item_id}", response_model=CartSchema, summary="Удалить товар из корзины")
async def remove_item(
    item_id: int,
    current_user: UserModel = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Удалить товар из корзины.

    - **item_id**: ID элемента корзины
    """
    # TODO: Реализовать удаление товара
    return CartSchema(
        id=1,
        user_id=current_user.id,
        items=[],
        total=Decimal("0"),
        items_count=0,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )


@router.delete("", response_model=SuccessResponse, summary="Очистить корзину")
async def clear_cart(
    current_user: UserModel = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Удалить все товары из корзины.
    """
    # TODO: Реализовать очистку корзины
    return SuccessResponse(message="Cart cleared")


@router.post("/checkout", response_model=dict, summary="Оформить заказ")
async def checkout(
    shipping_address: dict,
    current_user: UserModel = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Оформить заказ из корзины.

    Создает заказ, очищает корзину, уменьшает остатки товаров.

    - **shipping_address**: Адрес доставки

    Возвращает созданный заказ.
    """
    # TODO: Реализовать оформление заказа
    # - Валидировать корзину (не пуста)
    # - Проверить наличие товаров
    # - Создать заказ
    # - Уменьшить stock товаров
    # - Очистить корзину
    # - Публиковать событие order:created

    return {
        "success": True,
        "order_id": 1,
        "message": "Order created successfully"
    }
