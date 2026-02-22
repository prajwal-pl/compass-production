"""
Usage: python -m db.push
Equivalent to `prisma db push` — syncs all models to the database.
"""
import asyncio
from sqlalchemy import text
from db.db import engine, Base
from db.models import *  # noqa: F401 — import all models so Base knows about them


async def push():
    print("🔄 Pushing schema to database...")
    async with engine.begin() as conn:
        # Enable required extensions first
        await conn.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"'))
        await conn.execute(text('CREATE EXTENSION IF NOT EXISTS "vector"'))
        print("✅ Extensions enabled.")

        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()
    print("✅ All tables created/verified.")


if __name__ == "__main__":
    asyncio.run(push())