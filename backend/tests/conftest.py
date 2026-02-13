"""Конфигурация pytest для всех тестов"""
import pytest
import asyncio
from typing import AsyncGenerator, Generator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
from httpx import AsyncClient, ASGITransport
from functools import partial

from core.models import Base
from core.config import get_settings
from core.app import app

settings = get_settings()

# Test database URL (in-memory SQLite for fast tests)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create test database session"""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestSessionLocal() as session:
        yield session
        await session.rollback()

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create test HTTP client"""
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test"
    ) as ac:
        # Override dependency injection
        from core.dependencies import get_session
        from unittest.mock import AsyncMock

        async def override_get_session():
            yield db_session

        app.dependency_overrides[get_session] = override_get_session

        yield ac

        app.dependency_overrides.clear()


@pytest.fixture
def auth_headers(client: AsyncClient) -> dict:
    """Get authenticated headers"""
    # TODO: После реализации авторизации в БД
    # return {"Authorization": "Bearer <token>"}
    return {}


# ============================================
# TEST HELPERS
# ============================================

class TestHelper:
    """Helper class for tests"""

    @staticmethod
    async def create_user(
        session: AsyncSession,
        email: str = "test@example.com",
        password: str = "password123",
        role: str = "customer"
    ):
        """Create test user"""
        from core.models import UserModel
        from passlib.context import CryptContext

        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        user = UserModel(
            email=email,
            password_hash=pwd_context.hash(password),
            role=role,
            is_active=True,
            is_verified=True
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

    @staticmethod
    async def create_category(
        session: AsyncSession,
        name: str = "Test Category",
        slug: str = "test-category"
    ):
        """Create test category"""
        from core.models import CategoryModel

        category = CategoryModel(
            name=name,
            slug=slug,
            description="Test category description"
        )
        session.add(category)
        await session.commit()
        await session.refresh(category)
        return category

    @staticmethod
    async def create_product(
        session: AsyncSession,
        name: str = "Test Product",
        slug: str = "test-product",
        price: int = 10000,  # 100.00 in kopecks
        stock: int = 10,
        category_id: int = None
    ):
        """Create test product"""
        from core.models import ProductModel

        product = ProductModel(
            name=name,
            slug=slug,
            description="Test product description",
            price=price,
            stock=stock,
            category_id=category_id,
            is_active=True
        )
        session.add(product)
        await session.commit()
        await session.refresh(product)
        return product

    @staticmethod
    async def create_cart(
        session: AsyncSession,
        user_id: int = None
    ):
        """Create test cart"""
        from core.models import CartModel

        cart = CartModel(user_id=user_id)
        session.add(cart)
        await session.commit()
        await session.refresh(cart)
        return cart

    @staticmethod
    async def create_order(
        session: AsyncSession,
        user_id: int,
        total: int = 10000
    ):
        """Create test order"""
        from core.models import OrderModel
        from datetime import datetime, timezone

        order = OrderModel(
            order_number=f"TEST-{datetime.now().year}-000001",
            user_id=user_id,
            status="pending",
            subtotal=total,
            shipping_cost=0,
            discount=0,
            tax=0,
            total=total,
            recipient_name="Test User",
            phone="+79001234567",
            city="Moscow",
            street="Test Street",
            building="1",
            postal_code="123456"
        )
        session.add(order)
        await session.commit()
        await session.refresh(order)
        return order


@pytest.fixture
def test_helper():
    """Test helper instance"""
    return TestHelper
