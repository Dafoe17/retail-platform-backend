# 🚀 Online Shop API

## Установка

```bash
# Установка зависимостей
pip install -r requirements.txt
```

## Запуск

```bash
# Запуск сервера
uvicorn core.app:app --reload --host 0.0.0.0 --port 8000
```

## 📚 Документация

После запуска доступна по адресу:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 🔐 Тестовые данные

**Пользователь:**
- Email: `user@example.com`
- Пароль: `password123`

**База данных:**
- Adminer: http://localhost:8080
- Host: `postgres`
- User: `retail_user`
- Password: `retail_password`
- Database: `retail_shop`
