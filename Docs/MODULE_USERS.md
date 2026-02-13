# 👤 МОДУЛЬ USERS (Пользователи и Авторизация)

## 📋 НАЗНАЧЕНИЕ

Управление пользователями, аутентификация, авторизация, JWT токены, профили пользователей.

---

## 🎯 ОТВЕТСТВЕННОСТИ

- Регистрация новых пользователей
- Аутентификация (login/logout)
- Управление JWT токенами (access + refresh)
- Управление профилем пользователя
- Ролевая модель доступа (RBAC)
- Восстановление пароля (будущее)

---

## 🔄 ВЗАИМОДЕЙСТВИЯ

### Публикуемые события

| Событие | Данные | Подписчики |
|---------|--------|------------|
| `user:registered` | `{id, email, role}` | Cart (создание корзины) |
| `user:created` | `{id, email}` | Cart, Notifications |
| `user:email_changed` | `{id, old_email, new_email}` | Notifications |
| `user:password_changed` | `{id}` | — (логирование) |
| `user:logged_in` | `{id, ip}` | Analytics (будущее) |
| `user:logged_out` | `{id}` | — |

### Подписчики

| Событие | Обработка |
|---------|-----------|
| — | — |

---

## 🏗️ СТРУКТУРА МОДУЛЯ

```
backend/modules/users/
├── README.md                          # Этот файл
│
├── domain/                            # Бизнес-логика
│   ├── entities/
│   │   ├── user.entity.py            # Сущность Пользователь
│   │   ├── user_profile.entity.py    # Сущность Профиль
│   │   └── role.entity.py           # Сущность Роль
│   │
│   ├── value_objects/
│   │   ├── email.py                 # Email (валидация)
│   │   ├── password.py              # Password (хеширование)
│   │   └── user_id.py               # UserId
│   │
│   ├── repositories/
│   │   ├── user_repository.py       # Интерфейс репозитория
│   │   └── refresh_token_repository.py
│   │
│   └── services/
│       └── auth_service.py           # Логика аутентификации
│
├── application/                       # Use Cases
│   ├── use_cases/
│   │   ├── register.use_case.py
│   │   ├── login.use_case.py
│   │   ├── logout.use_case.py
│   │   ├── refresh_token.use_case.py
│   │   ├── get_current_user.use_case.py
│   │   ├── update_profile.use_case.py
│   │   ├── change_password.use_case.py
│   │   └── change_email.use_case.py
│   │
│   ├── dto/
│   │   ├── user_dto.py              # UserDTO, UserProfileDTO
│   │   ├── auth_dto.py             # LoginRequest, TokensResponse
│   │   └── register_dto.py          # RegisterRequest
│   │
│   └── events/
│       └── user_events.py           # Все события модуля
│
├── infrastructure/                    # Внешние зависимости
│   ├── database/
│   │   ├── models.py                # SQLAlchemy модели
│   │   ├── sqlalchemy_user_repository.py
│   │   └── sqlalchemy_refresh_token_repository.py
│   │
│   └── security/
│       ├── jwt_manager.py           # Управление JWT токенами
│       ├── password_hasher.py       # Хеширование паролей
│       └── token_store.py          # Хранение refresh токенов
│
├── presentation/                      # API
│   └── api/
│       ├── routes.py                # FastAPI роуты
│       ├── schemas.py               # Pydantic модели
│       └── dependencies.py         # get_current_user, require_admin
│
└── tests/                           # Тесты
    ├── unit/
    │   ├── test_user_entity.py
    │   ├── test_email_vo.py
    │   ├── test_password_vo.py
    │   └── test_jwt_manager.py
    ├── integration/
    │   ├── test_auth_api.py
    │   ├── test_user_api.py
    │   └── test_user_repository.py
    └── fixtures/
        └── user_fixtures.py
```

---

## 🧱 DOMAIN LAYER

### Entities (Сущности)

#### User (Пользователь)
```python
class User:
    id: UserId
    email: Email                      # Value Object
    password_hash: str
    role: Role                        # Value Object
    is_active: bool
    is_verified: bool                  # email verified
    created_at: datetime
    updated_at: datetime
    last_login_at: datetime | None

    # Методы бизнес-логики
    def verify_password(self, plain_password: str) -> bool
    def change_password(self, old_password: str, new_password: str) -> None
    def change_email(self, new_email: Email) -> None
    def login(self) -> None           # обновляет last_login_at
    def logout(self) -> None
    def deactivate(self) -> None
    def activate(self) -> None
    def is_admin(self) -> bool
```

#### UserProfile (Профиль)
```python
class UserProfile:
    user_id: UserId
    first_name: str | None
    last_name: str | None
    phone: str | None
    avatar_url: str | None
    date_of_birth: date | None
    updated_at: datetime

    # Методы
    def update(self, **fields) -> None
    def get_full_name(self) -> str
```

#### Role (Роль)
```python
class Role:
    name: str                         # "customer", "admin"
    permissions: set[str]

    # Предопределенные роли
    CUSTOMER = Role("customer", {"cart:write", "order:write"})
    ADMIN = Role("admin", {"*"})      # все права

    def has_permission(self, permission: str) -> bool
```

### Value Objects (Объекты-значения)

#### Email
```python
class Email:
    value: str

    def __init__(self, value: str):
        # Валидация формата email
        if not self._is_valid(value):
            raise ValueError("Invalid email format")
        self.value = value.lower()

    def _is_valid(self, value: str) -> bool
    def __eq__(self, other) -> bool
    def __hash__(self) -> int
```

#### Password
```python
class Password:
    MIN_LENGTH = 8

    def __init__(self, plain_password: str):
        self._validate(plain_password)
        self._plain_value = plain_password

    def _validate(self, password: str) -> None:
        # Минимум 8 символов
        # Хотя бы 1 буква и 1 цифра
        pass

    def hash(self) -> str:
        # bcrypt hash
        pass
```

### Repository Interfaces

```python
class IUserRepository(ABC):
    async def save(self, user: User) -> User
    async def find_by_id(self, user_id: UserId) -> User | None
    async def find_by_email(self, email: Email) -> User | None
    async def email_exists(self, email: Email) -> bool
    async def delete(self, user_id: UserId) -> None

class IRefreshTokenRepository(ABC):
    async def save(self, token: RefreshToken) -> RefreshToken
    async def find(self, token_str: str) -> RefreshToken | None
    async def revoke(self, token_str: str) -> None
    async def revoke_all_for_user(self, user_id: UserId) -> None
    async def delete_expired(self) -> None
```

---

## 📐 APPLICATION LAYER

### Use Cases

#### 1. RegisterUseCase
**Назначение:** Регистрация нового пользователя

**Вход:** `RegisterRequest`
- email: str
- password: str
- first_name: str | None
- last_name: str | None

**Выход:** `TokensResponse` + `UserDTO`

**Правила:**
- Email не занят
- Password валиден
- Создается User с ролью "customer"
- Автоматически is_verified = True (простая версия)

**События:**
- `user:registered`
- `user:created`

---

#### 2. LoginUseCase
**Назначение:** Аутентификация пользователя

**Вход:** `LoginRequest`
- email: str
- password: str

**Выход:** `TokensResponse`
```python
{
    "access_token": "eyJ...",
    "refresh_token": "eyJ...",
    "token_type": "bearer",
    "expires_in": 900  # 15 минут
}
```

**Правила:**
- Email существует
- Password совпадает
- User is_active = True

**Действия:**
- Сгенерировать access_token (15 мин)
- Сгенерировать refresh_token (7 дней)
- Сохранить refresh_token в БД
- Обновить last_login_at

**События:**
- `user:logged_in`

---

#### 3. LogoutUseCase
**Назначение:** Выход из системы

**Вход:** `refresh_token` (из cookie или body)

**Действия:**
- Отозвать refresh_token
- Отозвать все refresh токены пользователя (опционально)

**События:**
- `user:logged_out`

---

#### 4. RefreshTokenUseCase
**Назначение:** Обновление access токена

**Вход:** `refresh_token`

**Выход:** `TokensResponse` (новая пара токенов)

**Правила:**
- Refresh token валиден
- Не истек
- Не отозван
- User активен

**Действия:**
- Создать новую пару токенов
- Отозвать старый refresh_token

---

#### 5. GetCurrentUserUseCase
**Назначение:** Получение текущего пользователя

**Вход:** `user_id` (из access_token)

**Выход:** `UserDTO` с профилем

---

#### 6. UpdateProfileUseCase
**Назначение:** Обновление профиля

**Вход:** `user_id`, `UpdateProfileRequest`
- first_name: str | None
- last_name: str | None
- phone: str | None

**Выход:** `UserDTO`

---

#### 7. ChangePasswordUseCase
**Назначение:** Изменение пароля

**Вход:** `user_id`, `ChangePasswordRequest`
- old_password: str
- new_password: str

**Правила:**
- Старый пароль верный
- Новый пароль валиден
- Новый пароль != старый

**Действия:**
- Хешировать новый пароль
- Сохранить
- Отозвать все refresh токены (безопасность)

**События:**
- `user:password_changed`

---

### DTO

#### UserDTO
```python
@dataclass
class UserDTO:
    id: int
    email: str
    role: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login_at: datetime | None
    profile: UserProfileDTO | None
```

#### UserProfileDTO
```python
@dataclass
class UserProfileDTO:
    first_name: str | None
    last_name: str | None
    full_name: str
    phone: str | None
    avatar_url: str | None
```

#### TokensResponse
```python
@dataclass
class TokensResponse:
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 900  # 15 минут
```

---

## 🔐 SECURITY

### JWT Structure

**Access Token:**
```json
{
  "sub": "123",           # user_id
  "email": "user@example.com",
  "role": "customer",
  "exp": 1234567890,
  "iat": 1234567890,
  "type": "access"
}
```

**Refresh Token:**
```json
{
  "sub": "123",
  "jti": "uuid",          # unique token ID
  "exp": 1234567890,
  "type": "refresh"
}
```

### Password Hashing
- Алгоритм: bcrypt
- Rounds: 12
- Salt: автоматический

### Token Storage
- Access Token: не хранится на сервере (stateless)
- Refresh Token: хранится в БД (таблица `refresh_tokens`)

```python
class RefreshTokenModel(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True)
    token_id = Column(String(36), unique=True)  # JTI
    user_id = Column(Integer, ForeignKey("users.id"))
    expires_at = Column(DateTime)
    created_at = Column(DateTime)
    revoked_at = Column(DateTime, nullable=True)
    ip_address = Column(String(45))  # IPv6 support
    user_agent = Column(String(255))
```

---

## 🗄️ INFRASTRUCTURE LAYER

### Database Models (SQLAlchemy)

```python
class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="customer")
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login_at = Column(DateTime, nullable=True)

    profile = relationship("UserProfileModel", back_populates="user", uselist=False)
    refresh_tokens = relationship("RefreshTokenModel", back_populates="user")
```

```python
class UserProfileModel(Base):
    __tablename__ = "user_profiles"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    first_name = Column(String(100))
    last_name = Column(String(100))
    phone = Column(String(20))
    avatar_url = Column(String(500))
    date_of_birth = Column(Date)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("UserModel", back_populates="profile")
```

---

## 🌐 PRESENTATION LAYER

### API Routes

```python
# /api/auth
auth_router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserWithTokensResponse)
@router.post("/login", response_model=TokensResponse)
@router.post("/logout")
@router.post("/refresh", response_model=TokensResponse)
@router.get("/me", response_model=UserResponse)

# /api/users
users_router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=UserResponse)
@router.put("/me", response_model=UserResponse)
@router.put("/me/password")
@router.put("/me/email")
```

### Dependencies

```python
# FastAPI dependency для получения текущего пользователя
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    repo: IUserRepository = Depends(get_user_repository)
) -> User:
    # Декодировать JWT
    # Найти пользователя в БД
    # Проверить is_active
    pass

# Требуется роль admin
async def require_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    if not current_user.is_admin():
        raise HTTPException(403, "Admin required")
    return current_user
```

---

## 🧪 ТЕСТИРОВАНИЕ

### Unit Tests
- Тестирование User entity
- Тестирование Email VO
- Тестирование Password VO
- Тестирование JWT manager

### Integration Tests
- Регистрация пользователя
- Логин с неверными данными
- Обновление токена
- Изменение пароля
- Доступ к защищенным endpoint

### Test Scenarios

```
✓ Регистрация с валидными данными
✓ Регистрация с существующим email → ошибка
✓ Регистрация со слабым паролем → ошибка
✓ Логин с верными данными → токены
✓ Логин с неверным паролем → ошибка
✓ Логин неактивного пользователя → ошибка
✓ Обновление access токена через refresh
✓ Обновление с истекшим refresh → ошибка
✓ Logout → refresh токен отозван
✓ Получение текущего пользователя
✓ Изменение пароля с неверным старым → ошибка
✓ Изменение пароля → все refresh токены отозваны
✓ Доступ к /api/cart без токена → 401
✓ Доступ к /api/products с токеном → 200
✓ Доступ к /admin с ролью customer → 403
✓ Доступ к /admin с ролью admin → 200
```

---

## 📋 CHECKLIST ДЛЯ РЕАЛИЗАЦИИ

- [ ] Созданы entity: User, UserProfile, Role
- [ ] Созданы value objects: Email, Password
- [ ] Созданы интерфейсы репозиториев
- [ ] Созданы SQLAlchemy модели
- [ ] Реализованы репозитории
- [ ] Реализован JWTManager
- [ ] Реализован PasswordHasher
- [ ] Реализованы все use cases
- [ ] Созданы DTO
- [ ] Настроен Event Bus (публикация событий)
- [ ] Созданы API routes
- [ ] Созданы Pydantic схемы
- [ ] Созданы dependencies (get_current_user)
- [ ] Написаны unit тесты
- [ ] Написаны integration тесты
- [ ] Обновлен README.md модуля

---

**Версия:** 1.0
**Статус:** 📐 Спроектировано
