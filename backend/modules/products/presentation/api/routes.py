"""API роуты для товаров"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from typing import Optional, List
from decimal import Decimal
import json

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
    # Базовый запрос с join категорий
    query = select(ProductModel).join(CategoryModel, ProductModel.category_id == CategoryModel.id)

    # Применение фильтров
    if category_id:
        query = query.where(ProductModel.category_id == category_id)

    if min_price is not None:
        query = query.where(ProductModel.price >= int(min_price * 100))  # Конвертируем рубли в копейки

    if max_price is not None:
        query = query.where(ProductModel.price <= int(max_price * 100))

    if in_stock:
        query = query.where(ProductModel.stock > 0)

    if search:
        search_pattern = f"%{search}%"
        query = query.where(or_(
            ProductModel.name.ilike(search_pattern),
            ProductModel.description.ilike(search_pattern)
        ))

    # Сортировка
    if sort_by == "name":
        query = query.order_by(ProductModel.name)
    elif sort_by == "price_asc":
        query = query.order_by(ProductModel.price)
    elif sort_by == "price_desc":
        query = query.order_by(ProductModel.price.desc())
    else:  # created
        query = query.order_by(ProductModel.created_at.desc())

    # Подсчёт общего количества
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await session.execute(count_query)
    total = total_result.scalar() or 0

    # Пагинация
    total_pages = (total + page_size - 1) // page_size
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    # Выполнение запроса
    result = await session.execute(query)
    products = result.scalars().all()

    # Конвертация в Pydantic модели
    from datetime import datetime
    product_schemas = []
    for p in products:
        # Парсинг images из JSON
        images_list = []
        if p.images:
            try:
                images_list = json.loads(p.images) if isinstance(p.images, str) else p.images
            except:
                images_list = []

        product_schemas.append(ProductSchema(
            id=p.id,
            name=p.name,
            slug=p.slug,
            description=p.description,
            price=Decimal(str(p.price / 100)),  # Конвертируем копейки в рубли
            stock=p.stock,
            category_id=p.category_id,
            images=images_list,
            is_available=p.is_active and p.stock > 0,
            created_at=p.created_at or datetime.utcnow(),
            updated_at=p.updated_at or datetime.utcnow()
        ))

    total_pages = max(total_pages, 1)

    return PaginatedResponse(
        items=product_schemas,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/categories/list", response_model=List[CategorySchema], summary="Список категорий")
async def list_categories(
    session: AsyncSession = Depends(get_session)
):
    """
    Получить список всех категорий.
    """
    # Реальный запрос к БД
    result = await session.execute(
        select(CategoryModel)
        .where(CategoryModel.is_active == True)
        .order_by(CategoryModel.name)
    )
    categories = result.scalars().all()

    return [
        CategorySchema(
            id=c.id,
            name=c.name,
            slug=c.slug,
            description=c.description,
            parent_id=c.parent_id,
            is_active=c.is_active,
            created_at=c.created_at
        )
        for c in categories
    ]


@router.get("/{product_id}", response_model=ProductSchema, summary="Детали товара")
async def get_product(
    product_id: int,
    session: AsyncSession = Depends(get_session)
):
    """
    Получить детали товара по ID.

    - **product_id**: ID товара
    """
    result = await session.execute(
        select(ProductModel).where(ProductModel.id == product_id)
    )
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Парсинг images
    images_list = []
    if product.images:
        try:
            images_list = json.loads(product.images) if isinstance(product.images, str) else product.images
        except:
            images_list = []

    return ProductSchema(
        id=product.id,
        name=product.name,
        slug=product.slug,
        description=product.description,
        price=Decimal(str(product.price / 100)),
        stock=product.stock,
        category_id=product.category_id,
        images=images_list,
        is_available=product.is_active and product.stock > 0,
        created_at=product.created_at,
        updated_at=product.updated_at
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
    - **slug**: URL-дружный идентификатор
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
        images=["https://images.unsplash.com/photo-1592750475338-74b7b210f4f7?w=400"],
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
