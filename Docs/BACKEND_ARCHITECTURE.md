# 🏗️ АРХИТЕКТУРА БЭКЕНДА: ONLINE SHOP

## 📋 ОБЗОР СИСТЕМЫ

**Назначение:** Бэкенд для онлайн магазина с каталогом товаров и корзиной

**Технологический стек:**
- **Framework:** FastAPI
- **ORM:** SQLAlchemy 2.0 (async)
- **Validation:** Pydantic v2
- **Database:** PostgreSQL
- **Testing:** Pytest (async)
- **Auth:** JWT + refresh tokens
- **Docs:** OpenAPI 3.0 (auto-generated)

---

## 🏛️ МОДУЛЬНАЯ СТРУКТУРА

```
backend/
├── core/                            # Ядро системы
│   ├── app.py                       # FastAPI приложение
│   ├── config.py                    # Конфигурация (settings)
│   ├── database.py                  # SQLAlchemy async setup
│   ├── security.py                  # JWT, hash, auth utils
│   ├── logger.py                    # Логирование
│   ├── exceptions.py                 # Кастомные исключения
│   └── dependencies.py               # FastAPI dependencies
│
├── shared/                          # Общие утилиты для всех модулей
│   ├── dto/                        # Base DTOs
│   ├── utils/                      # formatters, validators
│   └── middleware/                 # CORS, logging, error handling
│
├── modules/                         # Модули (domain + infrastructure)
│   ├── users/                      # 👤 Пользователи
│   │   ├── README.md
│   │   ├── domain/
│   │   ├── application/
│   │   ├── infrastructure/
│   │   ├── presentation/
│   │   └── tests/
│   │
│   ├── products/                   # 📦 Товары
│   │   ├── README.md
│   │   ├── domain/
│   │   │   ├── entities/
│   │   │   │   ├── product.entity.py
│   │   │   │   └── category.entity.py
│   │   │   ├── value_objects/
│   │   │   │   ├── money.py
│   │   │   │   └── quantity.py
│   │   │   ├── repositories/
│   │   │   │   └── product_repository.py
│   │   │   └── services/
│   │   │       └── product_search_service.py
│   │   │
│   │   ├── application/
│   │   │   ├── use_cases/
│   │   │   │   ├── create_product.use_case.py
│   │   │   │   ├── update_product.use_case.py
│   │   │   │   ├── delete_product.use_case.py
│   │   │   │   ├── get_product.use_case.py
│   │   │   │   ├── list_products.use_case.py
│   │   │   │   └── search_products.use_case.py
│   │   │   ├── dto/
│   │   │   │   ├── product_dto.py
│   │   │   │   └── product_filters_dto.py
│   │   │   └── events/
│   │   │       └── product_events.py
│   │   │
│   │   ├── infrastructure/
│   │   │   ├── database/
│   │   │   │   ├── models.py
│   │   │   │   └── sqlalchemy_product_repository.py
│   │   │   └── storage/
│   │   │       └ └── image_storage.py
│   │   │
│   │   └── presentation/
│   │       └── api/
│   │           ├── routes.py
│   │           └── schemas.py
│   │
│   ├── cart/                       # 🛒 Корзина
│   │   ├── README.md
│   │   ├── domain/
│   │   │   ├── entities/
│   │   │   │   ├── cart.entity.py
│   │   │   │   └── cart_item.entity.py
│   │   │   ├── value_objects/
│   │   │   │   └── cart_item_data.py
│   │   │   └── repositories/
│   │   │       └── cart_repository.py
│   │   │
│   │   ├── application/
│   │   │   ├── use_cases/
│   │   │   │   ├── add_item.use_case.py
│   │   │   │   ├── update_item_quantity.use_case.py
│   │   │   │   ├── remove_item.use_case.py
│   │   │   │   ├── clear_cart.use_case.py
│   │   │   │   └── get_cart.use_case.py
│   │   │   ├── dto/
│   │   │   │   ├── cart_dto.py
│   │   │   │   └── cart_item_dto.py
│   │   │   └── events/
│   │   │       └── cart_events.py
│   │   │
│   │   ├── infrastructure/
│   │   │   └── database/
│   │   │       ├── models.py
│   │   │       └── sqlalchemy_cart_repository.py
│   │   │
│   │   └── presentation/
│   │       └── api/
│   │           ├── routes.py
│   │           └── schemas.py
│   │
│   └── orders/                     # 📋 Заказы
│       ├── README.md
│       ├── domain/
│       │   ├── entities/
│       │   │   ├── order.entity.py
│       │   │   ├── order_item.entity.py
│       │   │   └── order_status.entity.py
│       │   ├── value_objects/
│       │   │   └── order_address.py
│       │   └── repositories/
│       │       └── order_repository.py
│       │
│       ├── application/
│       │   ├── use_cases/
│       │   │   ├── create_order.use_case.py
│       │   │   ├── get_order.use_case.py
│       │   │   ├── list_user_orders.use_case.py
│       │   │   ├── update_order_status.use_case.py
│       │   │   └── cancel_order.use_case.py
│       │   ├── dto/
│       │   │   ├── order_dto.py
│       │   │   └── create_order_dto.py
│       │   └── events/
│       │       └── order_events.py
│       │
│       ├── infrastructure/
│       │   └── database/
│       │       ├── models.py
│       │       └── sqlalchemy_order_repository.py
│       │
│       └── presentation/
│           └── api/
│               ├── routes.py
│               └── schemas.py
│
└── tests/                          # Общие тесты
    ├── conftest.py
    └── fixtures/
```

---

## 🔄 ВЗАИМОДЕЙСТВИЕ МОДУЛЕЙ

```
┌─────────────────────────────────────────────────────────────┐
│                        EVENT BUS                            │
│  (user:created, product:updated, order:created, etc.)     │
└─────────────────────────────────────────────────────────────┘
         ↑                    ↓                    ↑
    publishes            subscribes          publishes
         │                    │                    │
┌────────┐            ┌──────────┐         ┌─────────┐
│  USER  │───────────>│   CART   │────────>│  ORDER  │
│        │            │          │         │         │
└────────┘            └──────────┘         └─────────┘
                              ↑
                              │ subscribes
                         ┌─────────┐
                         │PRODUCTS │
                         └─────────┘
```

### Поток данных:

1. **User Module** → публикует `user:created`
2. **Cart Module** → подписан на `user:created`, создает пустую корзину
3. **Cart Module** → подписан на `product:updated` (обновление цен/стоков)
4. **Order Module** → подписан на `cart:checkout`, публикует `order:created`

---

## 🗄️ БАЗА ДАННЫХ

### Схема (по модулям):

```sql
-- Users Module
users (id, email, password_hash, role, created_at, updated_at)
user_profiles (user_id, first_name, last_name, phone, avatar_url)

-- Products Module
categories (id, name, slug, parent_id, description)
products (id, name, slug, description, price, stock, category_id, images, created_at, updated_at)
product_variants (id, product_id, sku, price, stock, attributes)

-- Cart Module
carts (id, user_id, created_at, updated_at)
cart_items (id, cart_id, product_id, quantity, added_at)

-- Orders Module
orders (id, user_id, status, total_amount, shipping_address, created_at, updated_at)
order_items (id, order_id, product_id, quantity, price_at_order)
order_status_history (id, order_id, status, comment, changed_at)
```

---

## 🔐 АВТОРИЗАЦИЯ И АВТЕНТИФИКАЦИЯ

### JWT Strategy:

```
Access Token:  15 минут  → для API запросов
Refresh Token: 7 дней    → для обновления access token
```

### Роли:

- **customer** - обычный покупатель
- **admin** - администратор (полный доступ)

### Auth Flow:

1. POST `/api/auth/login` → JWT tokens
2. GET `/api/auth/me` → текущий пользователь
3. POST `/api/auth/refresh` → обновление токена
4. POST `/api/auth/logout` → revoke refresh token

---

## 📡 API ENDPOINTS

### Auth Module
```
POST   /api/auth/register
POST   /api/auth/login
POST   /api/auth/logout
POST   /api/auth/refresh
GET    /api/auth/me
```

### Products Module
```
GET    /api/products              # список товаров
GET    /api/products/{id}         # деталь товара
POST   /api/products              # создать (admin)
PUT    /api/products/{id}         # обновить (admin)
DELETE /api/products/{id}         # удалить (admin)
GET    /api/products/search       # поиск
GET    /api/categories            # категории
```

### Cart Module
```
GET    /api/cart                  # получить корзину
POST   /api/cart/items            # добавить товар
PUT    /api/cart/items/{id}       # обновить количество
DELETE /api/cart/items/{id}       # удалить товар
DELETE /api/cart                  # очистить корзину
POST   /api/cart/checkout         # оформить заказ
```

### Orders Module
```
GET    /api/orders                # список заказов
GET    /api/orders/{id}           # деталь заказа
POST   /api/orders                # создать заказ
PUT    /api/orders/{id}/status    # обновить статус (admin)
POST   /api/orders/{id}/cancel   # отменить заказ
```

---

## 🎯 CLEAN ARCHITECTURE LAYERS

### Domain (Ядро)
- **Сущности (Entities):** Product, Cart, Order
- **Объекты-значения (Value Objects):** Money, Quantity
- **Интерфейсы репозиториев:** IProductRepository, ICartRepository
- **Доменные сервисы:** ProductSearchService

**Правило:** НЕТ импортов SQLAlchemy, FastAPI, requests

### Application (Приложение)
- **Use Cases:** CreateProduct, AddItemToCart, CreateOrder
- **DTO:** ProductDTO, CartDTO
- **События модуля:** ProductCreated, CartUpdated

**Правило:** Использует Domain, НЕТ импортов FastAPI

### Infrastructure (Инфраструктура)
- **SQLAlchemy модели:** ProductModel, CartModel
- **Репозитории:** SQLAlchemyProductRepository
- **Внешние API:** PaymentGateway, ImageStorage

**Правило:** Реализует интерфейсы из Domain

### Presentation (Представление)
- **FastAPI роуты:** @router.get("/products")
- **Pydantic схемы:** ProductResponse, CartResponse
- **Middleware:** AuthMiddleware, ErrorHandlingMiddleware

**Правило:** Минимум логики, делегирование Use Cases

---

## 🚀 ЗАПУСК ПРОЕКТА

```bash
# Установка зависимостей
poetry install

# Миграции БД
alembic upgrade head

# Запуск сервера
uvicorn backend.core.app:app --reload

# Тесты
pytest -v

# Документация (автоматически)
http://localhost:8000/docs
```

---

## 📦 КОНФИГУРАЦИЯ

**Файл:** `backend/core/config.py`

```python
class Settings(BaseSettings):
    # App
    APP_NAME: str = "Online Shop API"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str

    # JWT
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Storage
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 5 * 1024 * 1024  # 5MB
```

---

**Версия:** 1.0
**Статус:** 📐 Проектирование
