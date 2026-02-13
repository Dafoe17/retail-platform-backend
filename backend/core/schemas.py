"""Pydantic схемы для API"""
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


# ============================================
# БАЗОВЫЕ СХЕМЫ
# ============================================

class PaginatedResponse(BaseModel):
    """Пагинированный ответ"""
    items: list
    total: int
    page: int
    page_size: int
    total_pages: int


class SuccessResponse(BaseModel):
    """Ответ об успехе"""
    success: bool = True
    message: Optional[str] = None


# ============================================
# USERS
# ============================================

class UserProfileSchema(BaseModel):
    """Профиль пользователя"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class UserSchema(BaseModel):
    """Пользователь"""
    id: int
    email: EmailStr
    role: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login_at: Optional[datetime] = None
    profile: Optional[UserProfileSchema] = None

    model_config = ConfigDict(from_attributes=True)


class UserRegisterSchema(BaseModel):
    """Регистрация"""
    email: EmailStr = Field(..., description="Email пользователя")
    password: str = Field(..., min_length=8, description="Пароль (минимум 8 символов)")
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)


class UserLoginSchema(BaseModel):
    """Логин"""
    email: EmailStr = Field(..., description="Email пользователя")
    password: str = Field(..., description="Пароль")


class TokensResponseSchema(BaseModel):
    """JWT токены"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 900  # 15 минут


class UserWithTokensSchema(UserSchema):
    """Пользователь с токенами (после регистрации/логина)"""
    tokens: TokensResponseSchema


# ============================================
# PRODUCTS
# ============================================

class CategorySchema(BaseModel):
    """Категория"""
    id: int
    name: str
    slug: str
    description: Optional[str] = None
    parent_id: Optional[int] = None
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProductSchema(BaseModel):
    """Товар"""
    id: int
    name: str
    slug: str
    description: Optional[str] = None
    price: Decimal = Field(..., description="Цена в рублях")
    stock: int = Field(..., ge=0, description="Количество на складе")
    category_id: Optional[int] = None
    category: Optional[CategorySchema] = None
    images: List[str] = Field(default_factory=list)
    is_available: bool = Field(..., description="Доступен для заказа")
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProductCreateSchema(BaseModel):
    """Создание товара (admin)"""
    name: str = Field(..., min_length=1, max_length=255)
    slug: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    price: Decimal = Field(..., gt=0, decimal_places=2)
    stock: int = Field(..., ge=0)
    category_id: Optional[int] = None
    images: List[str] = Field(default_factory=list)


class ProductUpdateSchema(BaseModel):
    """Обновление товара (admin)"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    price: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    stock: Optional[int] = Field(None, ge=0)
    category_id: Optional[int] = None
    images: Optional[List[str]] = None
    is_active: Optional[bool] = None


class ProductFiltersSchema(BaseModel):
    """Фильтры товаров"""
    category_id: Optional[int] = None
    min_price: Optional[Decimal] = None
    max_price: Optional[Decimal] = None
    in_stock: Optional[bool] = None
    search: Optional[str] = None
    sort_by: str = Field(default="created", pattern="^(name|price_asc|price_desc|created)$")
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


# ============================================
# CART
# ============================================

class CartItemSchema(BaseModel):
    """Элемент корзины"""
    id: int
    product_id: int
    product_name: str
    product_slug: Optional[str] = None
    product_image: Optional[str] = None
    quantity: int
    unit_price: Decimal
    subtotal: Decimal
    is_available: bool
    stock_available: int

    model_config = ConfigDict(from_attributes=True)


class CartSchema(BaseModel):
    """Корзина"""
    id: int
    user_id: Optional[int] = None
    items: List[CartItemSchema] = Field(default_factory=list)
    total: Decimal = Field(default=0, description="Общая сумма")
    items_count: int = Field(default=0, description="Общее количество товаров")
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CartItemAddSchema(BaseModel):
    """Добавление товара в корзину"""
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0, le=99, description="Количество (1-99)")


class CartItemUpdateSchema(BaseModel):
    """Обновление количества товара"""
    quantity: int = Field(..., gt=0, le=99, description="Новое количество (1-99)")


# ============================================
# ORDERS
# ============================================

class AddressSchema(BaseModel):
    """Адрес доставки"""
    recipient_name: str = Field(..., min_length=1)
    phone: str = Field(..., min_length=10)
    country: Optional[str] = None
    city: str = Field(..., min_length=1)
    street: str = Field(..., min_length=1)
    building: str = Field(..., min_length=1)
    apartment: Optional[str] = None
    postal_code: str = Field(..., min_length=1)


class OrderItemSchema(BaseModel):
    """Элемент заказа"""
    id: int
    product_id: int
    product_name: str
    product_slug: Optional[str] = None
    quantity: int
    unit_price: Decimal
    subtotal: Decimal

    model_config = ConfigDict(from_attributes=True)


class OrderStatusHistorySchema(BaseModel):
    """История статусов заказа"""
    id: int
    status: str
    comment: Optional[str] = None
    changed_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OrderSchema(BaseModel):
    """Заказ"""
    id: int
    order_number: str
    user_id: int
    status: str
    status_display: str = Field(..., description="Отображаемое название статуса")
    items: List[OrderItemSchema] = Field(default_factory=list)
    subtotal: Decimal
    shipping_cost: Decimal
    discount: Decimal
    tax: Decimal
    total: Decimal
    shipping_address: AddressSchema
    comment: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    status_history: List[OrderStatusHistorySchema] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class OrderCreateSchema(BaseModel):
    """Создание заказа"""
    shipping_address: AddressSchema
    comment: Optional[str] = None


class OrderSummarySchema(BaseModel):
    """Краткая информация о заказе (для списка)"""
    id: int
    order_number: str
    status: str
    status_display: str
    total: Decimal
    items_count: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OrderUpdateStatusSchema(BaseModel):
    """Обновление статуса заказа (admin)"""
    status: str = Field(..., description="Новый статус")
    comment: Optional[str] = None
