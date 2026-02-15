"""Seed database with initial data"""
import asyncio
import os
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import async_session_maker


async def run_sql_file(session: AsyncSession, filepath: Path) -> None:
    """Execute SQL file"""
    if not filepath.exists():
        print(f"SQL file not found: {filepath}")
        return

    with open(filepath, "r", encoding="utf-8") as f:
        sql_content = f.read()

    # Split by semicolon and execute each statement
    statements = []
    current_statement = []

    for line in sql_content.split("\n"):
        # Skip comments
        stripped = line.strip()
        if stripped.startswith("--"):
            continue

        current_statement.append(line)

        # Check if statement ends with semicolon
        if stripped.endswith(";"):
            stmt = "\n".join(current_statement).strip()
            if stmt and stmt != ";":
                statements.append(stmt)
            current_statement = []

    # Execute statements
    for stmt in statements:
        try:
            await session.execute(text(stmt))
        except Exception as e:
            # Log but continue (some statements may fail if already exist)
            print(f"Warning: {str(e)[:100]}")

    await session.commit()
    print(f"Executed: {filepath.name}")


async def seed_database() -> None:
    """Initialize database with schema and sample data"""
    db_dir = Path(__file__).parent

    async with async_session_maker() as session:
        # Run init.sql (schema + basic sample data)
        init_sql = db_dir / "init.sql"
        if init_sql.exists():
            await run_sql_file(session, init_sql)

        # Run sample_data.sql (more test data)
        sample_sql = db_dir / "sample_data.sql"
        if sample_sql.exists():
            await run_sql_file(session, sample_sql)

    print("Database seeded successfully!")


if __name__ == "__main__":
    asyncio.run(seed_database())
