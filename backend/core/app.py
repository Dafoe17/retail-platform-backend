"""Main FastAPI Application"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlalchemy import select, text

from .config import get_settings
from .schemas import SuccessResponse
from .database import engine, Base, async_session_maker
from .models import CategoryModel, ProductModel, UserModel, UserProfileModel

settings = get_settings()


async def seed_database():
    """Seed database with initial data if empty"""
    async with async_session_maker() as session:
        # Check if categories exist
        result = await session.execute(select(CategoryModel).limit(1))
        if result.scalar():
            print("Database already seeded, skipping...")
            return

        print("Seeding database...")

        # Categories
        categories = [
            CategoryModel(name='Электроника', slug='elektronika', description='Смартфоны, ноутбуки и другие электронные устройства'),
            CategoryModel(name='Одежда', slug='odezhda', description='Одежда для мужчин и женщин'),
            CategoryModel(name='Бытовая техника', slug='byitovaya-tehnika', description='Техника для дома'),
            CategoryModel(name='Книги', slug='knigi', description='Книги различных жанров'),
            CategoryModel(name='Спорт и отдых', slug='sport-i-otdyh', description='Товары для спорта и отдыха'),
            CategoryModel(name='Красота и здоровье', slug='krasota-i-zdorove', description='Косметика и товары для здоровья'),
        ]
        session.add_all(categories)
        await session.flush()

        # Products
        products = [
            # Electronics
            ProductModel(name='iPhone 15 Pro 256GB', slug='iphone-15-pro-256gb',
                description='Смартфон Apple iPhone 15 Pro с дисплеем 6.1 дюйма, камерой 48 Мп и процессором A17 Pro.',
                price=9999000, stock=50, category_id=1, images='["https://images.unsplash.com/photo-1592750475338-74b7b210f4f7?w=400"]'),
            ProductModel(name='Samsung Galaxy S24 Ultra', slug='samsung-galaxy-s24-ultra',
                description='Флагман Samsung с экраном 6.8 дюйма, камерой 200 Мп и S Pen.',
                price=8999000, stock=35, category_id=1, images='["https://images.unsplash.com/photo-1610945415295-d9bbf067e59c?w=400"]'),
            ProductModel(name='MacBook Air 13" M3', slug='macbook-air-13-m3',
                description='Облегченный ноутбук Apple с процессором M3, 8 ГБ RAM и 256 ГБ SSD.',
                price=12999000, stock=20, category_id=1, images='["https://images.unsplash.com/photo-1517336714731-489679fd1ca8?w=400"]'),
            # Clothing
            ProductModel(name='Классический худи черного цвета', slug='hudi-chernyy',
                description='Удобный худи из хлопка 100%. Идеален для повседневной носки.',
                price=399900, stock=100, category_id=2, images='["https://images.unsplash.com/photo-1556821840-022fac958a99?w=400"]'),
            ProductModel(name='Джинсы slim fit', slug='dzhinsy-slim-fit',
                description='Классические джинсы прямого кроя из денима. Размеры: 28-34.',
                price=299900, stock=80, category_id=2, images='["https://images.unsplash.com/photo-1542272604-787c3835535d?w=400"]'),
            ProductModel(name='Кофта с капюшоном', slug='kofta-s-kapyushonom',
                description='Теплая кофта с капюшоном для прохладной погоды.',
                price=599900, stock=60, category_id=2, images='["https://images.unsplash.com/photo-1556905055-2f1480df5c44?w=400"]'),
            # Appliances
            ProductModel(name='Робот-пылесос Xiaomi', slug='robot-pylesos-xiaomi',
                description='Автоматический робот-пылесос с навигацией LDS, мощностью 2100 Па.',
                price=2499000, stock=25, category_id=3, images='["https://images.unsplash.com/photo-1558618666-f76279422b5a?w=400"]'),
            ProductModel(name='Умная колонка Яндекс Станция Макс', slug='yandex-stanciya-maks',
                description='Умная колонка с голосовым помощником Алиса, 60 Вт мощности.',
                price=3499000, stock=40, category_id=3, images='["https://images.unsplash.com/photo-1589492477829-5ee9a5c6e45d?w=400"]'),
            ProductModel(name='Фен Dyson Supersonic', slug='fen-dyson-supersonic',
                description='Профессиональный фен с умным контролем температуры и ионизацией.',
                price=2999000, stock=15, category_id=3, images='["https://images.unsplash.com/photo-1522338188442-1e2e3a72f8f9?w=400"]'),
            # Books
            ProductModel(name='Мастер и Маргарита', slug='master-i-margarita',
                description='Роман Михаила Булгакова. Перепечатка. Твердый переплет.',
                price=89900, stock=200, category_id=4, images='["https://images.unsplash.com/photo-1512820790803-83ca734de79d?w=400"]'),
            ProductModel(name='Властелин колец', slug='vlactelin-kolec',
                description='Роман-эпопея Дж.Р.Р. Толкина. Полное собрание в трех томах.',
                price=129900, stock=150, category_id=4, images='["https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=400"]'),
            ProductModel(name='Код Да Винчи', slug='kod-da-vinchi',
                description='Детективный роман Дэна Брауна. Бестселлер по всему миру.',
                price=69900, stock=180, category_id=4, images='["https://images.unsplash.com/photo-1589829085413-56de8ae18c29?w=400"]'),
            # Sport
            ProductModel(name='Йога-мат премиум', slug='yoga-mat-premium',
                description='Мат для йоги из экологического материала ТПЭ. Размер: 183x61 см.',
                price=199900, stock=90, category_id=5, images='["https://images.unsplash.com/photo-1601925261366-7df1bc1dbe51?w=400"]'),
            ProductModel(name='Гантели 2 кг хром', slug='ganteli-2kg-hrom',
                description='Комплект гантелей по 2 кг для фитнес-тренировок.',
                price=79900, stock=120, category_id=5, images='["https://images.unsplash.com/photo-1517927217850-9c592e83af84?w=400"]'),
            ProductModel(name='Велосипед дорожный', slug='velosiped-dorozhnyy',
                description='Дорожный велосипед с алюминиевой рамой, 21 скорость.',
                price=2999000, stock=12, category_id=5, images='["https://images.unsplash.com/photo-1532235289296-ecf7a1ca42ca?w=400"]'),
            # Beauty
            ProductModel(name='Парфюмерный набор Chanel', slug='parfyumernyy-nabor-chanel',
                description='Набор из трех ароматов: Chanel No.5, Coco Mademoiselle, Bleu de Chanel.',
                price=4999000, stock=30, category_id=6, images='["https://images.unsplash.com/photo-1541643600914-78a8685c2f0d?w=400"]'),
            ProductModel(name='Набор косметики MAC', slug='nabor-kosmetiki-mac',
                description='Профессиональный набор косметики MAC: тональник, помады, тушь.',
                price=3499000, stock=45, category_id=6, images='["https://images.unsplash.com/photo-1512496015851-a90fb94ba6f7?w=400"]'),
            ProductModel(name='Шампунь и кондиционер Loreal', slug='shampun-i-kondicioner-loreal',
                description='Набор для волос: шампунь 400мл + кондиционер 400мл.',
                price=99900, stock=200, category_id=6, images='["https://images.unsplash.com/photo-1596462502292-c2f2caa6cc38?w=400"]'),
        ]
        session.add_all(products)

        # Test users (password: password123)
        users = [
            UserModel(email='test@example.com', password_hash='$2b$12$LQv3c1yqBWVHxmd0VHW1O9qWBz.HfWKR.k', role='customer'),
            UserModel(email='admin@example.com', password_hash='$2b$12$LQv3c1yqBWVHxmd0VHW1O9qWBz.HfWKR.k', role='admin'),
        ]
        session.add_all(users)
        await session.flush()

        # User profiles
        profiles = [
            UserProfileModel(user_id=1, first_name='Иван', last_name='Иванов', phone='+79991234567'),
            UserProfileModel(user_id=2, first_name='Администратор', last_name='Системы', phone='+799976543210'),
        ]
        session.add_all(profiles)

        await session.commit()
        print("Database seeded: 6 categories, 18 products, 2 users")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle events"""
    # Startup
    print(f"{settings.APP_NAME} v{settings.APP_VERSION} starting...")
    print(f"Database: {settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else settings.DATABASE_URL}")

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Database tables created/verified")

    # Seed data
    await seed_database()

    yield

    # Shutdown
    print("Shutting down...")


# Create app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Online Shop API",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================
# HEALTH CHECK
# ============================================

@app.get("/", tags=["Health"])
async def root() -> SuccessResponse:
    """Health check"""
    return SuccessResponse(message=f"{settings.APP_NAME} is running")


@app.get("/health", tags=["Health"])
async def health_check() -> dict:
    """Detailed health check"""
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "debug": settings.DEBUG
    }


# ============================================
# INCLUDE ROUTERS
# ============================================

from modules.users.presentation.api.routes import router as auth_router
from modules.products.presentation.api.routes import router as products_router
from modules.cart.presentation.api.routes import router as cart_router
from modules.orders.presentation.api.routes import router as orders_router

app.include_router(auth_router)
app.include_router(products_router)
app.include_router(cart_router)
app.include_router(orders_router)
