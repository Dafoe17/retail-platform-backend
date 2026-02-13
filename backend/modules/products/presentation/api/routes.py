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
            price=Decimal("99999.00"),  # В копейках для БД (999.99 руб)
            stock=50,
            category_id=1,
            images=["https://images.unsplash.com/photo-1592750475338-74b7b210f4f7?w=400"],
            is_available=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        ),
        ProductSchema(
            id=2,
            name="Samsung Galaxy S24",
            slug="samsung-galaxy-s24",
            description="Флагманский смартфон Samsung",
            price=Decimal("89999.00"),  # В копейках для БД (899.99 руб)
            stock=30,
            category_id=1,
            images=["https://images.unsplash.com/photo-1610945415295-d9bbf067e59c?w=400"],
            is_available=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        ),
        ProductSchema(
            id=3,
            name="MacBook Air 13 M3",
            slug="macbook-air-13-m3",
            description="Облегченный ноутбук Apple с процессором M3, 8 ГБ RAM и 256 ГБ SSD.",
            price=Decimal("129999.00"),  # В копейках для БД (1299.99 руб)
            stock=20,
            category_id=1,
            images=["https://images.unsplash.com/photo-1517336714731-489679fd1ca8?w=400"],
            is_available=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        ),
        ProductSchema(
            id=4,
            name="Беспроводные наушники Sony",
            slug="sony-headphones",
            description="Беспроводные наушники с шумоподавлением и 30 часами работы.",
            price=Decimal("24999.00"),  # В копейках для БД (249.99 руб)
            stock=45,
            category_id=1,
            images=["https://images.unsplash.com/photo-1505740422586-c331084f1cc?w=400"],
            is_available=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        ),
        ProductSchema(
            id=5,
            name="Умные часы Apple Watch Series 9",
            slug="apple-watch-s9",
            description="Умные часы с GPS, LTE и датчиком ЭКГ.",
            price=Decimal("44999.00"),  # В копейках для БД (449.99 руб)
            stock=25,
            category_id=1,
            images=["https://images.unsplash.com/photo-15795860220-c9f22d2ef01?w=400"],
            is_available=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        ),
        ProductSchema(
            id=6,
            name="iPad Pro 12.9\"",
            slug="ipad-pro-129",
            description="Планшет Apple с дисплеем Liquid Retina и чипом M2.",
            price=Decimal("99999.00"),  # В копейках для БД (999.99 руб)
            stock=15,
            category_id=1,
            images=["https://images.unsplash.com/photo-1544244015-4df4352d93f5?w=400"],
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
        ),
        CategorySchema(
            id=2,
            name="Одежда",
            slug="clothing",
            description="Одежда для мужчин и женщин",
            parent_id=None,
            is_active=True,
            created_at=datetime.utcnow()
        ),
        CategorySchema(
            id=3,
            name="Бытовая техника",
            slug="appliances",
            description="Техника для дома",
            parent_id=None,
            is_active=True,
            created_at=datetime.utcnow()
        ),
        CategorySchema(
            id=4,
            name="Книги",
            slug="books",
            description="Книги различных жанров",
            parent_id=None,
            is_active=True,
            created_at=datetime.utcnow()
        ),
        CategorySchema(
            id=5,
            name="Спорт и отдых",
            slug="sports",
            description="Товары для спорта и отдыха",
            parent_id=None,
            is_active=True,
            created_at=datetime.utcnow()
        ),
        CategorySchema(
            id=6,
            name="Красота и здоровье",
            slug="beauty",
            description="Косметика и товары для здоровья",
            parent_id=None,
            is_active=True,
            created_at=datetime.utcnow()
        )
    ]
