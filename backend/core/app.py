"""Main FastAPI Application"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .config import get_settings
from .schemas import SuccessResponse

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle events"""
    # Startup
    print(f"{settings.APP_NAME} v{settings.APP_VERSION} starting...")
    print(f"Database: {settings.DATABASE_URL}")
    print(f"JWT expire: {settings.ACCESS_TOKEN_EXPIRE_MINUTES}min")

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
