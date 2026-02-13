# 🏗️ АРХИТЕКТУРНЫЕ ПРАВИЛА ДЛЯ AI

## ОБЩИЙ ПРИНЦИП

**Модульная архитектура + Clean Architecture внутри каждого модуля**

---

## СТРУКТУРА ПРОЕКТА

```
project/
├── backend/
│   ├── core/                    # Ядро приложения
│   │   ├── app.py              # Главное приложение FastAPI
│   │   ├── config.py           # Конфигурация
│   │   ├── database.py         # Подключение к БД
│   │   ├── logger.py           # Логирование
│   │   └── shared/             # Общие утилиты
│   │
│   └── modules/                 # Модули приложения
│       └── [module_name]/       # Каждый модуль - независимая программа
│           │
│           ├── README.md        # Описание модуля
│           │
│           ├── domain/          # Бизнес-логика (НЕ зависит от внешних библиотек)
│           │   ├── entities/    # Сущности (классы)
│           │   ├── value_objects/ # Объекты-значения
│           │   ├── repositories/  # Интерфейсы репозиториев
│           │   └── services/      # Доменные сервисы
│           │
│           ├── application/     # Сценарии использования
│           │   ├── use_cases/   # Use Cases (бизнес-процессы)
│           │   ├── dto/         # Data Transfer Objects
│           │   ├── events/      # События модуля
│           │   └── services/    # Сервисы приложения
│           │
│           ├── infrastructure/  # Внешние зависимости
│           │   ├── database/    # Модели SQLAlchemy
│           │   ├── repositories/ # Реализации репозиториев
│           │   ├── storage/     # Файловое хранилище
│           │   └── external/    # Внешние API
│           │
│           ├── presentation/    # API и интерфейсы
│           │   └── api/
│           │       ├── routes.py     # FastAPI роуты
│           │       └── schemas.py    # Pydantic модели
│           │
│           └── tests/           # Тесты модуля
│               ├── unit/        # Юнит-тесты
│               ├── integration/ # Интеграционные тесты
│               └── fixtures/    # Фикстуры для тестов
│
└── frontend/
    ├── core/                    # Ядро фронтенда
    │   ├── shared/              # Общие утилиты (api.js, formatters.js)
    │   └── events/              # Event Bus
    │
    └── modules/                 # Модули фронтенда
        └── [module_name]/       # Каждый модуль
            ├── README.md
            │
            ├── domain/          # Бизнес-логика (если есть)
            │
            ├── application/     # Логика приложения
            │   └── use-cases/
            │
            ├── infrastructure/  # API, storage
            │   ├── api/
            │   └── storage/
            │
            └── presentation/    # UI
                ├── pages/       # HTML страницы
                ├── components/  # Компоненты
                ├── controllers/ # Контроллеры
                └── styles/      # CSS
```

---

## ПРАВИЛА МОДУЛЕЙ

### ✅ МОЖНО

1. **Модули общаются через Event Bus**
   ```javascript
   eventBus.publish('user:created', { userId: 123 });
   ```

2. **Используют общие утилиты из core/shared**
   ```javascript
   import api from '/core/shared/api.js';
   ```

3. **Имеют собственную документацию (README.md)**

### ❌ НЕЛЬЗЯ

1. **Прямые импорты между модулями**
   ```javascript
   // ❌ ПЛОХО
   import { UserService } from '../users/domain/services/user.service.js';
   ```

2. **Прямые вызовы use cases других модулей**
   ```javascript
   // ❌ ПЛОХО
   const createUserUseCase = new CreateUserUseCase();
   ```

3. **Общие таблицы БД между модулями**
   - Каждый модуль имеет свои таблицы
   - Если нужны данные другого модуля - через Event Bus или API

---

## ЗАВИСИМОСТИ (ВНУТРИ МОДУЛЯ)

```
Presentation → Application → Domain ← Infrastructure
                                ↑
                        НЕ ЗАВИСИТ НИ ОТ КОГО!
```

### Domain (Домен)
- Чистая бизнес-логика
- Только Python/JavaScript
- НЕТ импортов SQLAlchemy, FastAPI, requests и т.д.

### Application (Приложение)
- Use Cases (сценарии)
- Использует Domain
- НЕТ импортов FastAPI, requests

### Infrastructure (Инфраструктура)
- Реализация интерфейсов из Domain
- SQLAlchemy модели
- Репозитории
- Внешние API

### Presentation (Представление)
- FastAPI роуты
- Pydantic схемы
- HTML/CSS/JS

---

## NAMING CONVENTIONS

### Backend

**Use Cases:**
```python
create_user.use_case.py
update_mentor_status.use_case.py
generate_report.use_case.py
```

**Entities:**
```python
user.entity.py
mentor.entity.py
work_record.entity.py
```

**Repositories:**
```python
# Интерфейс (domain)
user_repository.py

# Реализация (infrastructure)
sqlalchemy_user_repository.py
```

**Events:**
```python
user_created.event.py
order_placed.event.py
```

### Frontend

**Use Cases:**
```javascript
login.use-case.js
create-mentor.use-case.js
```

**Controllers:**
```javascript
dashboard.controller.js
mentor-list.controller.js
```

**Pages:**
```html
mentors-list.html
create-mentor.html
```

---

## ПРИНЦИПЫ SOLID

### S - Single Responsibility
Каждый класс/функция имеет одну ответственность

### O - Open/Closed
Открыт для расширения, закрыт для модификации

### L - Liskov Substitution
Подклассы должны заменять родительские классы

### I - Interface Segregation
Много специфичных интерфейсов лучше одного общего

### D - Dependency Inversion
Зависимость от абстракций, а не от конкретных реализаций

---

## ПРИМЕРЫ

### Создание нового модуля

**Шаг 1: Структура**
```bash
backend/modules/notifications/
├── README.md
├── domain/
│   └── entities/
│       └── notification.entity.py
├── application/
│   └── use_cases/
│       └── send_notification.use_case.py
├── infrastructure/
│   └── email_service.py
└── presentation/
    └── api/
        └── routes.py
```

**Шаг 2: README.md**
```markdown
# Модуль Notifications

## Назначение
Отправка уведомлений пользователям

## События
- Подписывается на: `user:created`, `order:placed`
- Публикует: `notification:sent`

## API
- POST /api/notifications/send
```

**Шаг 3: Domain Entity**
```python
# domain/entities/notification.entity.py
class Notification:
    def __init__(self, recipient: str, message: str):
        self.recipient = recipient
        self.message = message
    
    def is_valid(self) -> bool:
        return bool(self.recipient and self.message)
```

**Шаг 4: Use Case**
```python
# application/use_cases/send_notification.use_case.py
class SendNotificationUseCase:
    def __init__(self, email_service):
        self.email_service = email_service
    
    def execute(self, recipient: str, message: str):
        notification = Notification(recipient, message)
        if not notification.is_valid():
            raise ValueError("Invalid notification")
        
        self.email_service.send(notification)
        # Публикуем событие
        event_bus.publish('notification:sent', {
            'recipient': recipient
        })
```

**Шаг 5: API Route**
```python
# presentation/api/routes.py
from fastapi import APIRouter

router = APIRouter(prefix="/notifications", tags=["notifications"])

@router.post("/send")
async def send_notification(request: SendNotificationRequest):
    use_case = SendNotificationUseCase(EmailService())
    use_case.execute(request.recipient, request.message)
    return {"status": "sent"}
```

---

## ЧЕКЛИСТ ДЛЯ AI

При создании нового функционала проверь:

- [ ] Определен модуль (или используется существующий)
- [ ] Domain слой НЕ зависит от внешних библиотек
- [ ] Use Case содержит бизнес-логику
- [ ] Repository использует интерфейс из Domain
- [ ] Модули НЕ импортируют друг друга напрямую
- [ ] Общение через Event Bus или API
- [ ] README.md обновлен
- [ ] Названия файлов следуют конвенции
- [ ] Соблюдены принципы SOLID

---

## ТЕХНОЛОГИИ

### Backend
- **Framework:** FastAPI
- **ORM:** SQLAlchemy
- **Validation:** Pydantic
- **Testing:** Pytest
- **Auth:** JWT

### Frontend
- **Базовые:** HTML5, CSS3, JavaScript (ES6+)
- **Event Bus:** Собственная реализация
- **Testing:** Playwright (E2E)

---

**Версия:** 1.0  
**Статус:** ✅ Готово к использованию

