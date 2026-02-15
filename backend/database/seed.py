"""Seed database with initial data"""
import asyncio
import sys
from pathlib import Path

from sqlalchemy import text

from core.database import async_session_maker, engine, Base
# Import all models to register them
from core.models import (  # noqa: F401
    UserModel, UserProfileModel, RefreshTokenModel,
    CategoryModel, ProductModel,
    CartModel, CartItemModel,
    OrderModel, OrderItemModel, OrderStatusHistoryModel,
)


async def create_tables() -> None:
    """Create all tables if they don't exist"""
    print("Creating tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Tables created/verified")


async def run_sql_file(filepath: Path) -> None:
    """Execute SQL file"""
    if not filepath.exists():
        print(f"SQL file not found: {filepath}")
        return

    print(f"Executing: {filepath.name}")

    with open(filepath, "r", encoding="utf-8") as f:
        sql_content = f.read()

    # Split by semicolon and execute each statement
    statements = []
    current_statement = []

    for line in sql_content.split("\n"):
        stripped = line.strip()
        # Skip comments
        if stripped.startswith("--"):
            continue

        current_statement.append(line)

        # Check if statement ends with semicolon
        if stripped.endswith(";"):
            stmt = "\n".join(current_statement).strip()
            if stmt and stmt != ";":
                statements.append(stmt)
            current_statement = []

    print(f"Found {len(statements)} statements")

    async with async_session_maker() as session:
        success = 0
        errors = 0
        for i, stmt in enumerate(statements, 1):
            try:
                await session.execute(text(stmt))
                success += 1
            except Exception as e:
                errors += 1
                # Show first 200 chars of error
                print(f"Error in statement {i}: {str(e)[:200]}")

        await session.commit()
        print(f"Executed: {success} success, {errors} errors")


async def seed_database() -> None:
    """Initialize database with schema and sample data"""
    try:
        # First create tables
        await create_tables()

        db_dir = Path(__file__).parent

        # Run sample_data.sql only (init.sql conflicts with SQLAlchemy models)
        sample_sql = db_dir / "sample_data.sql"
        await run_sql_file(sample_sql)

        print("Database seeded successfully!")
    except Exception as e:
        print(f"Seed error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(seed_database())
