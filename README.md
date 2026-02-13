# 🛒️ RetailPlatform - Online Shop

Full-stack e-commerce platform with modular architecture.

## 📋 Structure

```
retail-platform/
├── backend/          # FastAPI backend
│   ├── core/       # Shared code (app, models, config)
│   ├── modules/     # Feature modules (users, products, cart, orders)
│   └── database/    # Database schema & Docker
│
├── frontend/         # Web frontend (HTML/CSS/JS)
│   ├── core/       # Event Bus, shared utils
│   └── modules/     # Feature modules
│
└── data/           # Architecture docs & design system
```

## 🚀 Quick Start

### Backend (API + Database)

```bash
cd backend
pip install -r requirements.txt
docker-compose up -d      # PostgreSQL + Adminer
uvicorn core.app:app --reload  # API server
```

**API Documentation:** http://localhost:8000/docs

### Database (Adminer)

**URL:** http://localhost:8080
- System: PostgreSQL
- Server: `postgres`
- User: `retail_user`
- Password: `retail_password`
- Database: `retail_shop`

## 🔐 Test Data

**User:** `user@example.com` / `password123`

**Products in DB:**
- iPhone 15 Pro - 99,999 ₽
- Samsung Galaxy S24 - 89,999 ₽
- Basic T-shirt - 1,999 ₽
- Slim Jeans - 3,999 ₽
- War and Peace - 599 ₽

## 🛠️ Architecture

**Backend:** FastAPI + SQLAlchemy 2.0 (async) + PostgreSQL
**Frontend:** Vanilla JS + Event Bus architecture
**Pattern:** Clean Architecture (domain/application/infrastructure/presentation)

**Modules:**
- **Users** - Auth, JWT, profiles
- **Products** - Catalog, categories, search
- **Cart** - Shopping cart, totals calculation
- **Orders** - Order management, statuses, history

## 🧪 Testing

```bash
cd backend
pytest -v                   # All tests
pytest modules/*/tests/unit/    # Unit tests only
pytest --cov=.            # With coverage
```

**Results:** 21 unit tests ✅ (100% passing)

## 📚 API Endpoints

| Module | Endpoints | Auth |
|--------|-----------|------|
| **Auth** | `/api/auth/register`, `/api/auth/login`, `/api/auth/me` | Required |
| **Products** | `/api/products` (CRUD + search) | Optional |
| **Cart** | `/api/cart` (add/update/remove/clear) | Required |
| **Orders** | `/api/orders` (create/list/cancel) | Required |

Full docs: http://localhost:8000/docs

## 🔗 Links

- **GitLab:** https://gitlab.effective-mobile.ru/ramazan.gasanbekov/retailplatform
- **API Docs:** http://localhost:8000/docs
- **Database:** http://localhost:8080
