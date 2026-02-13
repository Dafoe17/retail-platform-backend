# 📦 МОДУЛЬ PRODUCTS (Каталог товаров)

## 📋 НАЗНАЧЕНИЕ

Управление каталогом товаров: создание, чтение, обновление, удаление, поиск и фильтрация товаров.

---

## 🎯 ОТВЕТСТВЕННОСТИ

- Управление карточками товаров
- Управление категориями (иерархия)
- Загрузка и хранение изображений
- Поиск и фильтрация товаров
- Управление остатками на складе

---

## 🔄 ВЗАИМОДЕЙСТВИЯ

### Публикуемые события

| Событие | Данные | Подписчики |
|---------|--------|------------|
| `product:created` | `{id, name, price, category_id}` | Cart (валидация), Orders |
| `product:updated` | `{id, price, stock, ...}` | Cart (обновление цен в корзине) |
| `product:deleted` | `{id}` | Cart (удаление из корзины) |
| `product:stock_changed` | `{id, old_stock, new_stock}` | Orders |

### Подписчики

| Событие | Обработка |
|---------|-----------|
| — | — |

---

## 🏗️ СТРУКТУРА МОДУЛЯ

```
backend/modules/products/
├── README.md                          # Этот файл
│
├── domain/                            # Бизнес-логика
│   ├── entities/
│   │   ├── product.entity.py         # Сущность Товар
│   │   └── category.entity.py        # Сущность Категория
│   │
│   ├── value_objects/
│   │   ├── money.py                  # Объект-значение: Деньги
│   │   ├── quantity.py              # Объект-значение: Количество
│   │   └── product_slug.py          # Объект-значение: Slug
│   │
│   ├── repositories/
│   │   ├── product_repository.py    # Интерфейс репозитория
│   │   └── category_repository.py   # Интерфейс репозитория
│   │
│   └── services/
│       └── product_search_service.py # Доменный сервис поиска
│
├── application/                       # Use Cases
│   ├── use_cases/
│   │   ├── create_product.use_case.py
│   │   ├── update_product.use_case.py
│   │   ├── delete_product.use_case.py
│   │   ├── get_product.use_case.py
│   │   ├── list_products.use_case.py
│   │   ├── search_products.use_case.py
│   │   ├── update_stock.use_case.py
│   │   ├── create_category.use_case.py
│   │   └── list_categories.use_case.py
│   │
│   ├── dto/
│   │   ├── product_dto.py           # ProductDTO, ProductListDTO
│   │   ├── category_dto.py          # CategoryDTO
│   │   └── product_filters_dto.py   # ProductFiltersDTO
│   │
│   └── events/
│       ├── product_created.event.py
│       ├── product_updated.event.py
│       ├── product_deleted.event.py
│       └── stock_changed.event.py
│
├── infrastructure/                    # Внешние зависимости
│   ├── database/
│   │   ├── models.py                # SQLAlchemy модели
│   │   ├── sqlalchemy_product_repository.py
│   │   └── sqlalchemy_category_repository.py
│   │
│   └── storage/
│       └── image_storage.py         # Хранение изображений
│
├── presentation/                     # API
│   └── api/
│       ├── routes.py                # FastAPI роуты
│       ├── schemas.py               # Pydantic модели запросов/ответов
│       └── dependencies.py         # Зависимости роутов
│
└── tests/                           # Тесты
    ├── unit/
    │   ├── test_product_entity.py
    │   ├── test_money_vo.py
    │   └── test_product_search_service.py
    ├── integration/
    │   ├── test_product_api.py
    │   └── test_product_repository.py
    └── fixtures/
        └── product_fixtures.py
```

---

## 🧱 DOMAIN LAYER

### Entities (Сущности)

#### Product (Товар)
```python
class Product:
    id: ProductId
    name: str
    slug: str
    description: str
    price: Money               # Value Object
    stock: Quantity            # Value Object
    category_id: CategoryId
    images: list[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    # Методы бизнес-логики
    def update_price(self, new_price: Money) -> None
    def update_stock(self, new_quantity: Quantity) -> None
    def decrease_stock(self, quantity: Quantity) -> None
    def increase_stock(self, quantity: Quantity) -> None
    def is_available(self) -> bool
    def add_image(self, image_url: str) -> None
    def remove_image(self, image_url: str) -> None
    def activate() -> None
    def deactivate() -> None
```

#### Category (Категория)
```python
class Category:
    id: CategoryId
    name: str
    slug: str
    description: str | None
    parent_id: CategoryId | None
    children: list[Category]
    is_active: bool
    created_at: datetime

    # Методы
    def add_child(self, category: Category) -> None
    def remove_child(self, category_id: CategoryId) -> None
    def has_parent(self) -> bool
    def get_path(self) -> list[str]  # ["Electronics", "Phones"]
```

### Value Objects (Объекты-значения)

#### Money (Деньги)
```python
class Money:
    amount: Decimal   # хранится в минимальных единицах (центы/копейки)
    currency: str     # "USD", "EUR", "RUB"

    def __init__(self, amount: Decimal, currency: str = "RUB")
    def add(self, other: Money) -> Money
    def multiply(self, factor: int) -> Money
    def to_display(self) -> str  # "1 234.56 ₽"
    def is_zero(self) -> bool
    def is_negative(self) -> bool
```

#### Quantity (Количество)
```python
class Quantity:
    value: int

    def __init__(self, value: int)
    def increase(self, amount: int) -> Quantity
    def decrease(self, amount: int) -> Quantity
    def is_zero(self) -> bool
    def is_positive(self) -> bool
    def is_available(self, requested: int) -> bool
```

### Repositories (Интерфейсы)

```python
class IProductRepository(ABC):
    async def save(self, product: Product) -> Product
    async def find_by_id(self, product_id: ProductId) -> Product | None
    async def find_by_slug(self, slug: str) -> Product | None
    async def find_all(
        self,
        filters: ProductFilters,
        pagination: Pagination
    ) -> tuple[list[Product], int]  # (items, total)
    async def delete(self, product_id: ProductId) -> None
    async def update_stock(self, product_id: ProductId, quantity: Quantity) -> None

class ICategoryRepository(ABC):
    async def save(self, category: Category) -> Category
    async def find_by_id(self, category_id: CategoryId) -> Category | None
    async def find_by_slug(self, slug: str) -> Category | None
    async def find_all(self, active_only: bool = True) -> list[Category]
    async def find_children(self, parent_id: CategoryId) -> list[Category]
    async def delete(self, category_id: CategoryId) -> None
```

---

## 📐 APPLICATION LAYER

### Use Cases

#### 1. CreateProductUseCase
**Назначение:** Создание нового товара

**Вход:** `CreateProductRequest`
- name: str
- description: str
- price: Decimal
- stock: int
- category_id: int
- images: list[str]

**Выход:** `ProductDTO`

**Правила валидации:**
- Название не пустое
- Цена > 0
- Stock >= 0
- Категория существует
- Slug уникален

**События:**
- Продублировать: `product:created`

---

#### 2. UpdateProductUseCase
**Назначение:** Обновление данных товара

**Вход:** `UpdateProductRequest` + `product_id`

**Правила:**
- Товар существует
- Если изменилась цена → создать событие `product:price_changed`
- Если изменился stock → создать событие `product:stock_changed`

**События:**
- `product:updated`

---

#### 3. DeleteProductUseCase
**Назначение:** Удаление товара (soft delete)

**Правила:**
- Товар не должен быть в активных заказах
- is_active = False
- Событие `product:deleted`

---

#### 4. GetProductUseCase
**Назначение:** Получение товара по ID или slug

**Выход:** `ProductDTO` или `NotFoundError`

---

#### 5. ListProductsUseCase
**Назначение:** Список товаров с фильтрацией и пагинацией

**Вход:** `ProductFiltersDTO`
- category_id: int | None
- min_price: Decimal | None
- max_price: Decimal | None
- in_stock: bool | None
- search: str | None  # поиск по названию/описанию
- sort_by: str  # "name", "price_asc", "price_desc", "created"
- page: int
- page_size: int

**Выход:** `PaginatedResponse[ProductDTO]`

---

#### 6. UpdateStockUseCase
**Назначение:** Обновление остатков

**Вход:** `product_id`, `new_stock`

**Правила:**
- stock >= 0
- Событие `product:stock_changed`

---

#### 7. CreateCategoryUseCase
**Назначение:** Создание категории

**Правила:**
- Уникальный slug
- Если есть parent_id → родитель существует

---

#### 8. ListCategoriesUseCase
**Назначение:** Дерево категорий

**Выход:** `list[CategoryTreeDTO]`

---

### DTO (Data Transfer Objects)

#### ProductDTO
```python
@dataclass
class ProductDTO:
    id: int
    name: str
    slug: str
    description: str
    price: Decimal
    stock: int
    category_id: int
    category_name: str | None
    images: list[str]
    is_available: bool
    created_at: datetime
```

#### ProductFiltersDTO
```python
@dataclass
class ProductFiltersDTO:
    category_id: int | None = None
    min_price: Decimal | None = None
    max_price: Decimal | None = None
    in_stock: bool | None = None
    search: str | None = None
    sort_by: str = "created"
    page: int = 1
    page_size: int = 20
```

---

## 🗄️ INFRASTRUCTURE LAYER

### Database Models (SQLAlchemy)

```python
class ProductModel(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False)
    description = Column(Text)
    price = Column(Integer, nullable=False)  # в копейках
    stock = Column(Integer, nullable=False, default=0)
    category_id = Column(Integer, ForeignKey("categories.id"))
    images = Column(JSON, default=list)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    category = relationship("CategoryModel", back_populates="products")
```

```python
class CategoryModel(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False)
    description = Column(Text)
    parent_id = Column(Integer, ForeignKey("categories.id"))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    parent = relationship("CategoryModel", remote_side=[id])
    children = relationship("CategoryModel")
    products = relationship("ProductModel")
```

### Image Storage

```python
class IImageStorage(ABC):
    async def save(self, file: UploadFile, product_id: int) -> str
    async def delete(self, image_url: str) -> None
    async def get_url(self, filename: str) -> str
```

Реализация: сохранение в `uploads/products/{product_id}/`

---

## 🌐 PRESENTATION LAYER

### API Routes

```python
# /api/products
router = APIRouter(prefix="/products", tags=["products"])

# Публичные (без авторизации)
@router.get("", response_model=ProductListResponse)
@router.get("/{product_id}", response_model=ProductResponse)
@router.get("/search", response_model=ProductListResponse)
@router.get("/categories", response_model=list[CategoryResponse])

# Только для admin
@router.post("", response_model=ProductResponse, dependencies=[Depends(require_admin)])
@router.put("/{product_id}", response_model=ProductResponse, dependencies=[Depends(require_admin)])
@router.delete("/{product_id}", dependencies=[Depends(require_admin)])
@router.patch("/{product_id}/stock", dependencies=[Depends(require_admin)])
```

### Pydantic Schemas

#### ProductRequest (создание)
```python
class ProductRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., max_length=5000)
    price: Decimal = Field(..., gt=0, decimal_places=2)
    stock: int = Field(..., ge=0)
    category_id: int = Field(..., gt=0)
    images: list[str] = Field(default_factory=list)
```

#### ProductResponse
```python
class ProductResponse(BaseModel):
    id: int
    name: str
    slug: str
    description: str
    price: Decimal
    stock: int
    category_id: int
    category: CategorySummary | None
    images: list[str]
    is_available: bool
    created_at: datetime
```

---

## 🧪 ТЕСТИРОВАНИЕ

### Unit Tests
- `test_product_entity.py` - тестирование бизнес-логики Product
- `test_money_vo.py` - тестирование Money (арифметика, форматирование)
- `test_quantity_vo.py` - тестирование Quantity
- `test_category_entity.py` - тестирование иерархии категорий

### Integration Tests
- `test_product_api.py` - тестирование API endpoints
- `test_product_repository.py` - тестирование SQLAlchemy репозитория
- `test_product_search.py` - тестирование поиска

### Test Scenarios

```
✓ Создание товара с валидными данными
✓ Ошибка при создании товара с дубликатом slug
✓ Ошибка при создании товара с несуществующей категорией
✓ Обновление цены товара
✓ Уменьшение stock (при заказе)
✓ Ошибка при уменьшении stock ниже 0
✓ Поиск товаров по названию
✓ Фильтрация по категории и цене
✓ Сортировка по цене
✓ Пагинация списка товаров
✓ Создание категории с родителем
✓ Получение дерева категорий
```

---

## 📋 CHECKLIST ДЛЯ РЕАЛИЗАЦИИ

- [ ] Созданы entity: Product, Category
- [ ] Созданы value objects: Money, Quantity
- [ ] Созданы интерфейсы репозиториев
- [ ] Созданы SQLAlchemy модели
- [ ] Реализованы репозитории
- [ ] Реализованы все use cases
- [ ] Созданы DTO
- [ ] Настроен Event Bus (публикация событий)
- [ ] Созданы API routes
- [ ] Созданы Pydantic схемы
- [ ] Написаны unit тесты
- [ ] Написаны integration тесты
- [ ] Обновлен README.md модуля

---

**Версия:** 1.0
**Статус:** 📐 Спроектировано
