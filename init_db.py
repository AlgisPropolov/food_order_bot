from database.session import async_engine
from database.models import Base
import asyncio

async def init_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ База данных инициализирована")

if __name__ == "__main__":
    asyncio.run(init_db())