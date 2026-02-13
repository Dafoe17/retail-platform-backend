# 🛒 МОДУЛЬ CART (Корзина)

## 📋 НАЗНАЧЕНИЕ

Управление корзиной покупателя: добавление товаров, изменение количества, удаление, очистка, расчет итоговой суммы.

---

## 🎯 ОТВЕТСТВЕННОСТИ

- Хранение корзины пользователя (сессия или БД)
- Добавление товаров в корзину
- Обновление количества товаров
- Удаление товаров из корзины
- Очистка корзины
- Расчет итоговой суммы
- Валидация товаров (наличие, цена, остаток)

---

## 🔄 ВЗАИМОДЕЙСТВИЯ

### Публикуемые события

| Событие | Данные | Подписчики |
|---------|--------|------------|
| `cart:created` | `{user_id, cart_id}` | — |
| `cart:item_added` | `{cart_id, product_id, quantity}` | Products (обновление популярности) |
| `cart:item_updated` | `{cart_id, product_id, old_qty, new_qty}` | — |
| `cart:item_removed` | `{cart_id, product_id}` | — |
| `cart:cleared` | `{cart_id}` | — |
| `cart:checkout_started` | `{cart_id, user_id, items}` | Orders (создание заказа) |

### Подписчики

| Событие | Обработка |
|---------|-----------|
| `user:created` | Автоматическое создание пустой корзины для нового пользователя |
| `product:updated` | Обновление цен/проверка доступности товаров в корзине |
| `product:deleted` | Удаление недоступных товаров из всех корзин |

---

## 🏗️ СТРУКТУРА МОДУЛЯ

```
backend/modules/cart/
├── README.md                          # Этот файл
│
├── domain/                            # Бизнес-логика
│   ├── entities/
│   │   ├── cart.entity.py            # Сущность Корзина
│   │   └── cart_item.entity.py       # Сущность Элемент корзины
│   │
│   ├── value_objects/
│   │   ├── cart_item_data.py         # Данные элемента (product_id, qty)
│   │   └── cart_total.py             # Итоговая сумма
│   │
│   ├── repositories/
│   │   └── cart_repository.py        # Интерфейс репозитория
│   │
│   └── services/
│       └── cart_validation_service.py # Валидация товаров
│
├── application/                       # Use Cases
│   ├── use_cases/
│   │   ├── get_or_create_cart.use_case.py
│   │   ├── add_item.use_case.py
│   │   ├── update_item_quantity.use_case.py
│   │   ├── remove_item.use_case.py
│   │   ├── clear_cart.use_case.py
│   │   └── get_cart.use_case.py
│   │
│   ├── dto/
│   │   ├── cart_dto.py              # CartDTO, CartItemDTO
│   │   └── cart_summary_dto.py      # CartSummaryDTO
│   │
│   └── events/
│       ├── cart_events.py           # Все события модуля
│
├── infrastructure/                    # Внешние зависимости
│   └── database/
│       ├── models.py                # SQLAlchemy модели
│       └── sqlalchemy_cart_repository.py
│
├── presentation/                      # API
│   └── api/
│       ├── routes.py                # FastAPI роуты
│       ├── schemas.py               # Pydantic модели
│       └── dependencies.py         # Dependencies (get_current_cart)
│
└── tests/                           # Тесты
    ├── unit/
    │   ├── test_cart_entity.py
    │   ├── test_cart_item_entity.py
    │   └── test_cart_validation.py
    ├── integration/
    │   ├── test_cart_api.py
    │   └── test_cart_repository.py
    └── fixtures/
        └── cart_fixtures.py
```

---

## 🧱 DOMAIN LAYER

### Entities (Сущности)

#### Cart (Корзина)
```python
class Cart:
    id: CartId
    user_id: UserId | None           # None для неавторизованных
    items: list[CartItem]
    created_at: datetime
    updated_at: datetime

    # Методы бизнес-логики
    def add_item(self, product_id: ProductId, quantity: int) -> None
    def update_item_quantity(self, product_id: ProductId, quantity: int) -> None
    def remove_item(self, product_id: ProductId) -> None
    def clear(self) -> None
    def get_item(self, product_id: ProductId) -> CartItem | None
    def has_item(self, product_id: ProductId) -> bool
    def is_empty(self) -> bool
    def calculate_total(self) -> CartTotal  # (subtotal, vat, total)
    def get_items_count(self) -> int        # общее кол-во товаров
```

#### CartItem (Элемент корзины)
```python
class CartItem:
    id: CartItemId
    cart_id: CartId
    product_id: ProductId
    quantity: Quantity
    unit_price: Money              # цена на момент добавления
    added_at: datetime

    # Методы
    def update_quantity(self, new_quantity: int) -> None
    def calculate_subtotal(self) -> Money  # quantity * unit_price
    def is_same_product(self, other: CartItem) -> bool
```

### Value Objects (Объекты-значения)

#### CartItemData
```python
@dataclass
class CartItemData:
    product_id: int
    quantity: int

    def validate(self) -> None:
        if self.quantity <= 0:
            raise ValueError("Quantity must be positive")
```

#### CartTotal
```python
@dataclass
class CartTotal:
    subtotal: Money      # сумма товаров
    discount: Money      # скидка (будущее)
    tax: Money          # НДС (будущее)
    total: Money        # итог

    @classmethod
    def from_items(cls, items: list[CartItem]) -> CartTotal
```

### Repository Interface

```python
class ICartRepository(ABC):
    async def save(self, cart: Cart) -> Cart
    async def find_by_id(self, cart_id: CartId) -> Cart | None
    async def find_by_user(self, user_id: UserId) -> Cart | None
    async def find_or_create(self, user_id: UserId) -> Cart
    async def delete(self, cart_id: CartId) -> None
    async def find_expired(self, before: datetime) -> list[Cart]
```

---

## 📐 APPLICATION LAYER

### Use Cases

#### 1. GetOrCreateCartUseCase
**Назначение:** Получение корзины пользователя или создание новой

**Вход:** `user_id: UserId | None`

**Выход:** `CartDTO`

**Правила:**
- Если корзина существует → вернуть
- Если нет → создать новую
- Для анонимных пользователей можно использовать session_id

---

#### 2. AddItemUseCase
**Назначение:** Добавление товара в корзину

**Вход:** `cart_id`, `product_id`, `quantity`

**Правила:**
- quantity > 0
- Товар существует (проверить через Products module API)
- Товар доступен (is_active = True, stock > 0)
- Если товар уже есть → обновить количество
- Максимальное количество товара в корзине: 99

**События:**
- `cart:item_added`
- Если это первый товар → `cart:created`

---

#### 3. UpdateItemQuantityUseCase
**Назначение:** Изменение количества товара

**Вход:** `cart_id`, `product_id`, `new_quantity`

**Правила:**
- new_quantity > 0
- Если new_quantity > stock → ошибка
- Если new_quantity == 0 → удалить товар
- Товар должен быть в корзине

**События:**
- `cart:item_updated` или `cart:item_removed`

---

#### 4. RemoveItemUseCase
**Назначение:** Удаление товара из корзины

**Вход:** `cart_id`, `product_id`

**Правила:**
- Товар должен быть в корзине

**События:**
- `cart:item_removed`

---

#### 5. ClearCartUseCase
**Назначение:** Очистка корзины

**Вход:** `cart_id`

**Правила:**
- Удалить все элементы

**События:**
- `cart:cleared`

---

#### 6. GetCartUseCase
**Назначение:** Получение корзины с актуальными данными

**Вход:** `cart_id`

**Выход:** `CartDTO`

**Действия:**
- Загрузить корзину
- Для каждого элемента получить актуальные данные товара:
  - Товар все еще существует?
  - Цена изменилась?
  - Товар доступен?
- Обновить данные если нужно
- Рассчитать итоги

---

### DTO

#### CartDTO
```python
@dataclass
class CartDTO:
    id: int
    user_id: int | None
    items: list[CartItemDTO]
    total: CartTotalDTO
    items_count: int
    created_at: datetime
    updated_at: datetime
```

#### CartItemDTO
```python
@dataclass
class CartItemDTO:
    id: int
    product_id: int
    product_name: str
    product_slug: str
    product_image: str | None
    quantity: int
    unit_price: Decimal
    subtotal: Decimal
    is_available: bool
    stock_available: int
```

#### CartTotalDTO
```python
@dataclass
class CartTotalDTO:
    subtotal: Decimal
    discount: Decimal = 0
    tax: Decimal = 0
    total: Decimal
```

---

## 🗄️ INFRASTRUCTURE LAYER

### Database Models (SQLAlchemy)

```python
class CartModel(Base):
    __tablename__ = "carts"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("UserModel", back_populates="cart")
    items = relationship("CartItemModel", cascade="all, delete-orphan")
```

```python
class CartItemModel(Base):
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True)
    cart_id = Column(Integer, ForeignKey("carts.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    unit_price = Column(Integer, nullable=False)  # в копейках
    added_at = Column(DateTime, default=datetime.utcnow)

    cart = relationship("CartModel", back_populates="items")
    product = relationship("ProductModel")

    __table_args__ = (
        UniqueConstraint('cart_id', 'product_id', name='uq_cart_product'),
    )
```

---

## 🌐 PRESENTATION LAYER

### API Routes

```python
# /api/cart
router = APIRouter(prefix="/cart", tags=["cart"])

# Требуется авторизация
@router.get("", response_model=CartResponse)
@router.post("/items", response_model=CartResponse)
@router.put("/items/{product_id}", response_model=CartResponse)
@router.delete("/items/{product_id}", response_model=CartResponse)
@router.delete("", response_model=CartResponse)
```

### Pydantic Schemas

#### AddItemRequest
```python
class AddItemRequest(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0, le=99)
```

#### UpdateItemRequest
```python
class UpdateItemRequest(BaseModel):
    quantity: int = Field(..., gt=0, le=99)
```

#### CartResponse
```python
class CartResponse(BaseModel):
    id: int
    items: list[CartItemResponse]
    total: CartTotalResponse
    items_count: int
```

---

## 🧪 ТЕСТИРОВАНИЕ

### Unit Tests
- Тестирование бизнес-логики Cart entity
- Тестирование CartItem entity
- Тестирование расчета итогов
- Тестирование валидации

### Integration Tests
- API endpoints
- Repository operations
- События

### Test Scenarios

```
✓ Создание корзины для нового пользователя
✓ Добавление товара в пустую корзину
✓ Добавление товара, который уже есть → увеличение quantity
✓ Добавление товара с quantity > stock → ошибка
✓ Добавление недоступного товара → ошибка
✓ Обновление количества товара
✓ Обновление quantity до 0 → товар удален
✓ Удаление товара из корзины
✓ Очистка корзины
✓ Расчет итоговой суммы
✓ Получение корзины с неактуальными ценами → обновление
✓ Обработка события user:created
✓ Обработка события product:deleted
```

---

## 📋 CHECKLIST ДЛЯ РЕАЛИЗАЦИИ

- [ ] Созданы entity: Cart, CartItem
- [ ] Созданы value objects: CartItemData, CartTotal
- [ ] Создан интерфейс репозитория
- [ ] Созданы SQLAlchemy модели
- [ ] Реализован репозиторий
- [ ] Реализованы все use cases
- [ ] Созданы DTO
- [ ] Настроен Event Bus (подписка на user:created, product:*)
- [ ] Созданы API routes
- [ ] Созданы Pydantic схемы
- [ ] Написаны unit тесты
- [ ] Написаны integration тесты
- [ ] Обновлен README.md модуля

---

**Версия:** 1.0
**Статус:** 📐 Спроектировано
