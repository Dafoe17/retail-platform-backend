# 🗄️ База данных Online Shop

## 🚀 Запуск

```bash
# Из папки backend
docker-compose up -d
```

## 🌐 Доступ к БД

### Adminer (в браузере)
```
http://localhost:8080
```

**Данные для подключения:**
- Система: PostgreSQL
- Сервер: `postgres`
- Пользователь: `retail_user`
- Пароль: `retail_password`
- База данных: `retail_shop`

### PostgreSQL напрямую
```
Host: localhost
Port: 5433
User: retail_user
Password: retail_password
Database: retail_shop
```

## 📊 Тестовые данные

**Пользователь:**
- Email: `user@example.com`
- Пароль: `password123`

**Товары:**
- iPhone 15 Pro — 99 999 ₽
- Samsung Galaxy S24 — 89 999 ₽
- И другие...

## 🛑 Остановка

```bash
docker-compose down
```

## 🗑️ Удаление с данными

```bash
docker-compose down -v
```
