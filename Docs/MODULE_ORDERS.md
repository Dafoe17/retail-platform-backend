# 📋 МОДУЛЬ ORDERS (Заказы)

## 📋 НАЗНАЧЕНИЕ

Управление заказами: оформление из корзины, отслеживание статусов, отмена заказов, история заказов.

---

## 🎯 ОТВЕТСТВЕННОСТИ

- Создание заказа из корзины
- Управление статусами заказов
- История изменений статусов
- Список заказов пользователя
- Детализация заказа
- Отмена заказов

---

## 🔄 ВЗАИМОДЕЙСТВИЯ

### Публикуемые события

| Событие | Данные | Подписчики |
|---------|--------|------------|
| `order:created` | `{id, user_id, total, items}` | Cart (очистка), Products (остатки), Notifications |
| `order:status_changed` | `{id, old_status, new_status}` | Notifications |
| `order:cancelled` | `{id, user_id, reason}` | Cart (возврат?), Products (возврат остатков) |

### Подписчики

| Событие | Обработка |
|---------|-----------|
| `cart:checkout_started` | Создание заказа из корзины |
| `product:stock_changed` | Проверка доступности товаров |
| `user:created` | — |

---

## 🏗️ СТРУКТУРА МОДУЛЯ

```
backend/modules/orders/
├── README.md                          # Этот файл
│
├── domain/                            # Бизнес-логика
│   ├── entities/
│   │   ├── order.entity.py           # Сущность Заказ
│   │   ├── order_item.entity.py      # Сущность Элемент заказа
│   │   └── order_status.entity.py    # Сущность Статус
│   │
│   ├── value_objects/
│   │   ├── order_address.py          # Адрес доставки
│   │   ├── order_total.py            # Сумма заказа
│   │   └── order_number.py           # Номер заказа
│   │
│   ├── repositories/
│   │   └── order_repository.py       # Интерфейс репозитория
│   │
│   └── services/
│       └── order_calculator_service.py # Расчеты суммы
│
├── application/                       # Use Cases
│   ├── use_cases/
│   │   ├── create_order.use_case.py
│   │   ├── get_order.use_case.py
│   │   ├── list_user_orders.use_case.py
│   │   ├── update_order_status.use_case.py
│   │   ├── cancel_order.use_case.py
│   │   └── get_order_history.use_case.py
│   │
│   ├── dto/
│   │   ├── order_dto.py             # OrderDTO, OrderItemDTO
│   │   ├── create_order_dto.py      # CreateOrderRequest
│   │   └── order_filters_dto.py     # OrderFiltersDTO
│   │
│   └── events/
│       └── order_events.py           # Все события модуля
│
├── infrastructure/                    # Внешние зависимости
│   └── database/
│       ├── models.py                # SQLAlchemy модели
│       └── sqlalchemy_order_repository.py
│
├── presentation/                      # API
│   └── api/
│       ├── routes.py                # FastAPI роуты
│       ├── schemas.py               # Pydantic модели
│       └── dependencies.py         # Зависимости
│
└── tests/                           # Тесты
    ├── unit/
    │   ├── test_order_entity.py
    │   ├── test_order_status.py
    │   └── test_order_calculator.py
    ├── integration/
    │   ├── test_order_api.py
    │   ├── test_order_creation.py
    │   └── test_order_repository.py
    └── fixtures/
        └── order_fixtures.py
```

---

## 🧱 DOMAIN LAYER

### Entities (Сущности)

#### Order (Заказ)
```python
class Order:
    id: OrderId
    order_number: OrderNumber         # Уникальный номер заказа (например, "ORD-2024-001234")
    user_id: UserId
    status: OrderStatus              # Value Object
    items: list[OrderItem]
    total: OrderTotal               # Value Object
    shipping_address: OrderAddress  # Value Object
    comment: str | None
    created_at: datetime
    updated_at: datetime

    # Методы бизнес-логики
    def can_be_cancelled(self) -> bool
    def cancel(self, reason: str | None = None) -> None
    def update_status(self, new_status: OrderStatus, comment: str | None = None) -> None
    def add_status_history(self, status: OrderStatus, comment: str | None = None) -> None
    def calculate_total(self) -> OrderTotal
```

#### OrderItem (Элемент заказа)
```python
class OrderItem:
    id: OrderItemId
    order_id: OrderId
    product_id: ProductId
    product_name: str               # Сохраняется на момент заказа
    product_slug: str
    quantity: Quantity
    unit_price: Money               # Цена на момент заказа
    subtotal: Money                 # quantity * unit_price

    # Методы
    def calculate_subtotal(self) -> Money
```

#### OrderStatus (Статус заказа)
```python
class OrderStatus:
    value: str

    # Возможные статусы
    PENDING = "pending"              # Создан, ожидает обработки
    CONFIRMED = "confirmed"          # Подтвержден
    PROCESSING = "processing"        # В обработке (сборка)
    SHIPPED = "shipped"             # Отправлен
    DELIVERED = "delivered"         # Доставлен
    CANCELLED = "cancelled"         # Отменен
    REFUNDED = "refunded"           # Возвращен

    # Переходы статусов
    TRANSITIONS = {
        PENDING: [CONFIRMED, CANCELLED],
        CONFIRMED: [PROCESSING, CANCELLED],
        PROCESSING: [SHIPPED, CANCELLED],
        SHIPPED: [DELIVERED],
        DELIVERED: [REFUNDED],
        CANCELLED: [],
        REFUNDED: []
    }

    def can_transition_to(self, new_status: OrderStatus) -> bool
    def is_final(self) -> bool
    def is_cancellable(self) -> bool
```

### Value Objects (Объекты-значения)

#### OrderNumber
```python
class OrderNumber:
    value: str  # Формат: "ORD-2024-001234"

    @classmethod
    def generate(cls) -> OrderNumber:
        # Генерация уникального номера
        year = datetime.now().year
        sequence = get_next_sequence()
        return OrderNumber(f"ORD-{year}-{sequence:06d}")
```

#### OrderTotal
```python
@dataclass
class OrderTotal:
    subtotal: Money     # Сумма товаров
    shipping: Money     # Доставка
    discount: Money     # Скидка
    tax: Money         # Налог
    total: Money       # Итого

    @classmethod
    def calculate(cls, items: list[OrderItem], shipping: Money = None) -> OrderTotal
```

#### OrderAddress
```python
@dataclass
class OrderAddress:
    recipient_name: str
    phone: str
    country: str
    city: str
    street: str
    building: str
    apartment: str | None
    postal_code: str
    comment: str | None

    def to_display_string(self) -> str
```

### Repository Interface

```python
class IOrderRepository(ABC):
    async def save(self, order: Order) -> Order
    async def find_by_id(self, order_id: OrderId) -> Order | None
    async def find_by_number(self, order_number: OrderNumber) -> Order | None
    async def find_by_user(
        self,
        user_id: UserId,
        filters: OrderFilters,
        pagination: Pagination
    ) -> tuple[list[Order], int]
    async def find_all(
        self,
        filters: OrderFilters,
        pagination: Pagination
    ) -> tuple[list[Order], int]
    async def delete(self, order_id: OrderId) -> None
```

---

## 📐 APPLICATION LAYER

### Use Cases

#### 1. CreateOrderUseCase
**Назначение:** Создание заказа из корзины

**Вход:** `CreateOrderRequest`
```python
{
    "user_id": int,
    "shipping_address": OrderAddressData,
    "comment": str | None,
    "cart_items": list[CartItemData]  # из модуля Cart
}
```

**Выход:** `OrderDTO`

**Правила валидации:**
- Корзина не пуста
- Все товары существуют
- Все товары доступны (is_active = True)
-остаток достаточен для заказа
- Адрес доставки валиден

**Действия:**
1. Получить корзину пользователя
2. Валидировать товары
3. Создать Order со статусом PENDING
4. Создать OrderItem для каждого товара
5. Рассчитать итоговую сумму
6. Уменьшить stock товаров
7. Очистить корзину
8. Сохранить заказ

**События:**
- `order:created`
- `product:stock_changed` (для каждого товара)

---

#### 2. GetOrderUseCase
**Назначение:** Получение заказа по ID или номеру

**Вход:** `order_id` или `order_number`

**Выход:** `OrderDTO` с историей статусов

**Правила:**
- Пользователь может видеть только свои заказы (если не admin)

---

#### 3. ListUserOrdersUseCase
**Назначение:** Список заказов пользователя с фильтрацией

**Вход:** `user_id`, `OrderFiltersDTO`
- status: str | None
- date_from: date | None
- date_to: date | None
- sort_by: str  # "created", "total"
- page: int
- page_size: int

**Выход:** `PaginatedResponse[OrderSummaryDTO]`

---

#### 4. UpdateOrderStatusUseCase
**Назначение:** Обновление статуса заказа (только admin)

**Вход:** `order_id`, `new_status`, `comment`

**Правила:**
- Переход статуса разрешен
- Добавить запись в историю

**События:**
- `order:status_changed`

---

#### 5. CancelOrderUseCase
**Назначение:** Отмена заказа

**Вход:** `order_id`, `reason`, `user_id`

**Правила:**
- Заказ принадлежит пользователю (или пользователь - admin)
- Статус позволяет отмену
- Вернуть остатки товаров на склад

**События:**
- `order:cancelled`
- `product:stock_changed` (возврат остатков)

---

### DTO

#### OrderDTO
```python
@dataclass
class OrderDTO:
    id: int
    order_number: str
    user_id: int
    status: str
    items: list[OrderItemDTO]
    total: OrderTotalDTO
    shipping_address: OrderAddressDTO
    comment: str | None
    created_at: datetime
    updated_at: datetime
    status_history: list[OrderStatusHistoryDTO]
```

#### OrderItemDTO
```python
@dataclass
class OrderItemDTO:
    id: int
    product_id: int
    product_name: str
    product_slug: str
    quantity: int
    unit_price: Decimal
    subtotal: Decimal
```

#### OrderSummaryDTO (для списка)
```python
@dataclass
class OrderSummaryDTO:
    id: int
    order_number: str
    status: str
    status_display: str
    total: Decimal
    items_count: int
    created_at: datetime
```

---

## 🗄️ INFRASTRUCTURE LAYER

### Database Models (SQLAlchemy)

```python
class OrderModel(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    order_number = Column(String(50), unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String(50), nullable=False, default="pending")
    subtotal = Column(Integer, nullable=False)  # в копейках
    shipping_cost = Column(Integer, nullable=False, default=0)
    discount = Column(Integer, nullable=False, default=0)
    tax = Column(Integer, nullable=False, default=0)
    total = Column(Integer, nullable=False)

    # Address
    recipient_name = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=False)
    country = Column(String(100))
    city = Column(String(100))
    street = Column(String(255))
    building = Column(String(20))
    apartment = Column(String(20))
    postal_code = Column(String(20))

    comment = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("UserModel")
    items = relationship("OrderItemModel", cascade="all, delete-orphan")
    status_history = relationship("OrderStatusHistoryModel", cascade="all, delete-orphan")
```

```python
class OrderItemModel(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    product_name = Column(String(255), nullable=False)
    product_slug = Column(String(255))
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Integer, nullable=False)  # в копейках
    subtotal = Column(Integer, nullable=False)

    order = relationship("OrderModel", back_populates="items")
    product = relationship("ProductModel")
```

```python
class OrderStatusHistoryModel(Base):
    __tablename__ = "order_status_history"

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    status = Column(String(50), nullable=False)
    comment = Column(Text)
    changed_at = Column(DateTime, default=datetime.utcnow)

    order = relationship("OrderModel", back_populates="status_history")
```

---

## 🌐 PRESENTATION LAYER

### API Routes

```python
# /api/orders
router = APIRouter(prefix="/orders", tags=["orders"])

# Пользовательские (с авторизацией)
@router.get("", response_model=OrderListResponse)
@router.get("/{order_id}", response_model=OrderResponse)
@router.get("/number/{order_number}", response_model=OrderResponse)
@router.post("", response_model=OrderResponse)
@router.post("/{order_id}/cancel", response_model=OrderResponse)

# Только для admin
@router.put("/{order_id}/status", response_model=OrderResponse, dependencies=[Depends(require_admin)])
@router.get("/all", response_model=OrderListResponse, dependencies=[Depends(require_admin)])
```

### Pydantic Schemas

#### CreateOrderRequest
```python
class CreateOrderRequest(BaseModel):
    shipping_address: AddressSchema
    comment: str | None = None
```

#### AddressSchema
```python
class AddressSchema(BaseModel):
    recipient_name: str = Field(..., min_length=1)
    phone: str = Field(..., min_length=10)
    country: str
    city: str = Field(..., min_length=1)
    street: str = Field(..., min_length=1)
    building: str = Field(..., min_length=1)
    apartment: str | None
    postal_code: str = Field(..., min_length=1)
    comment: str | None
```

#### OrderResponse
```python
class OrderResponse(BaseModel):
    id: int
    order_number: str
    status: str
    status_display: str
    items: list[OrderItemResponse]
    total: OrderTotalResponse
    shipping_address: AddressSchema
    comment: str | None
    created_at: datetime
```

---

## 🧪 ТЕСТИРОВАНИЕ

### Unit Tests
- Тестирование Order entity
- Тестирование OrderStatus (переходы)
- Тестирование OrderNumber генерации
- Тестирование OrderTotal расчетов

### Integration Tests
- Создание заказа из корзины
- Отмена заказа
- Обновление статуса
- API endpoints

### Test Scenarios

```
✓ Создание заказа из валидной корзины
✓ Создание заказа с пустой корзиной → ошибка
✓ Создание заказа с недоступным товаром → ошибка
✓ Создание заказа с недостаточным stock → ошибка
✓ При создании stock уменьшается
✓ При создании корзина очищается
✓ Генерация уникального order_number
✓ Отмена заказа в статусе pending
✓ Отмена заказа в статусе shipped → ошибка
✓ При отмене stock возвращается
✓ Переход статуса pending → confirmed
✓ Переход статуса shipped → pending → ошибка
✓ Получение списка заказов пользователя
✓ Фильтрация заказов по статусу
✓ Пагинация списка заказов
✓ Получение истории статусов
✓ Админ может видеть все заказы
✓ Пользователь видит только свои заказы
```

---

## 📋 CHECKLIST ДЛЯ РЕАЛИЗАЦИИ

- [ ] Созданы entity: Order, OrderItem, OrderStatus
- [ ] Созданы value objects: OrderNumber, OrderTotal, OrderAddress
- [ ] Создан интерфейс репозитория
- [ ] Созданы SQLAlchemy модели
- [ ] Реализован репозиторий
- [ ] Реализованы все use cases
- [ ] Созданы DTO
- [ ] Настроен Event Bus (подписка на cart:checkout)
- [ ] Созданы API routes
- [ ] Созданы Pydantic схемы
- [ ] Написаны unit тесты
- [ ] Написаны integration тесты
- [ ] Обновлен README.md модуля

---

**Версия:** 1.0
**Статус:** 📐 Спроектировано
