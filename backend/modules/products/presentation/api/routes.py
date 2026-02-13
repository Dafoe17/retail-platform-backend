"""API роуты для товаров"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from decimal import Decimal

from core.database import get_session
from core.schemas import (
    ProductSchema,
    ProductCreateSchema,
    ProductUpdateSchema,
    ProductFiltersSchema,
    CategorySchema,
    PaginatedResponse
)
from core.dependencies import get_current_user, require_admin
from core.models import ProductModel, CategoryModel

router = APIRouter(prefix="/api/products", tags=["Products"])


@router.get("", response_model=PaginatedResponse, summary="Список товаров")
async def list_products(
    category_id: Optional[int] = Query(None, description="Фильтр по категории"),
    min_price: Optional[Decimal] = Query(None, description="Минимальная цена"),
    max_price: Optional[Decimal] = Query(None, description="Максимальная цена"),
    in_stock: Optional[bool] = Query(None, description="Только в наличии"),
    search: Optional[str] = Query(None, description="Поиск по названию"),
    sort_by: str = Query("created", description="Сортировка: name, price_asc, price_desc, created"),
    page: int = Query(1, ge=1, description="Номер страницы"),
    page_size: int = Query(20, ge=1, le=100, description="Размер страницы"),
    session: AsyncSession = Depends(get_session)
):
    """
    Получить список товаров с фильтрацией и пагинацией.

    - **category_id**: Фильтр по категории
    - **min_price**: Минимальная цена
    - **max_price**: Максимальная цена
    - **in_stock**: Только товары в наличии
    - **search**: Поиск по названию и описанию
    - **sort_by**: Сортировка (name, price_asc, price_desc, created)
    - **page**: Номер страницы (по умолчанию 1)
    - **page_size**: Размер страницы (макс 100)
    """
    # TODO: Реализовать запрос к БД
    # Заглушка
    from datetime import datetime

    products = [
        ProductSchema(
            id=1,
            name="iPhone 15 Pro",
            slug="iphone-15-pro",
            description="Флагманский смартфон Apple",
            price=Decimal("99999.00"),
            stock=50,
            category_id=1,
            images=["https://example.com/iphone.jpg"],
            is_available=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        ),
        ProductSchema(
            id=2,
            name="Samsung Galaxy S24",
            slug="samsung-galaxy-s24",
            description="Флагманский смартфон Samsung",
            price=Decimal("89999.00"),
            stock=30,
            category_id=1,
            images=["https://example.com/samsung.jpg"],
            is_available=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
    ]

    total_pages = 1
    total = len(products)

    return PaginatedResponse(
        items=products,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/{product_id}", response_model=ProductSchema, summary="Детали товара")
async def get_product(
    product_id: int,
    session: AsyncSession = Depends(get_session)
):
    """
    Получить детали товара по ID.

    - **product_id**: ID товара
    """
    # TODO: Реализовать запрос к БД
    from datetime import datetime

    return ProductSchema(
        id=product_id,
        name="iPhone 15 Pro",
        slug="iphone-15-pro",
        description="Флагманский смартфон Apple",
        price=Decimal("99999.00"),
        stock=50,
        category_id=1,
        images=["https://example.com/iphone.jpg"],
        is_available=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )


@router.post("", response_model=ProductSchema, summary="Создать товар", dependencies=[Depends(require_admin)])
async def create_product(
    data: ProductCreateSchema,
    session: AsyncSession = Depends(get_session)
):
    """
    Создать новый товар.

    Требуется роль **admin**.

    - **name**: Название товара
    - **slug**: URL-友好ный идентификатор
    - **description**: Описание
    - **price**: Цена (в рублях, 2 знака после запятой)
    - **stock**: Количество на складе
    - **category_id**: Категория (опционально)
    - **images**: Список URL изображений
    """
    # TODO: Реализовать создание товара в БД
    from datetime import datetime

    return ProductSchema(
        id=1,
        name=data.name,
        slug=data.slug,
        description=data.description,
        price=data.price,
        stock=data.stock,
        category_id=data.category_id,
        images=data.images,
        is_available=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )


@router.put("/{product_id}", response_model=ProductSchema, summary="Обновить товар", dependencies=[Depends(require_admin)])
async def update_product(
    product_id: int,
    data: ProductUpdateSchema,
    session: AsyncSession = Depends(get_session)
):
    """
    Обновить данные товара.

    Требуется роль **admin**.
    """
    # TODO: Реализовать обновление товара в БД
    from datetime import datetime

    return ProductSchema(
        id=product_id,
        name="iPhone 15 Pro",
        slug="iphone-15-pro",
        description="Флагманский смартфон Apple",
        price=Decimal("99999.00"),
        stock=50,
        category_id=1,
        images=["https://example.com/iphone.jpg"],
        is_available=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )


@router.delete("/{product_id}", summary="Удалить товар", dependencies=[Depends(require_admin)])
async def delete_product(
    product_id: int,
    session: AsyncSession = Depends(get_session)
):
    """
    Удалить товар (soft delete - is_active=False).

    Требуется роль **admin**.
    """
    # TODO: Реализовать удаление товара
    return {"success": True, "message": "Product deleted"}


@router.get("/categories/list", response_model=List[CategorySchema], summary="Список категорий")
async def list_categories(
    session: AsyncSession = Depends(get_session)
):
    """
    Получить список всех категорий.
    """
    # TODO: Реализовать запрос к БД
    from datetime import datetime

    return [
        CategorySchema(
            id=1,
            name="Электроника",
            slug="electronics",
            description="Электронные устройства и гаджеты",
            parent_id=None,
            is_active=True,
            created_at=datetime.utcnow()
        )
    ]
