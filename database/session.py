from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from config.config import DATABASE_URL

# Синхронные подключения (для Alembic и синхронного кода)
sync_engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    pool_pre_ping=True
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)

# Асинхронные подключения (для основного приложения)
async_engine = create_async_engine(
    DATABASE_URL.replace("sqlite://", "sqlite+aiosqlite://"),
    echo=True,
    pool_pre_ping=True
)
AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Синхронная версия для зависимостей
def get_db():
    """Синхронный генератор сессий"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Асинхронная версия для зависимостей
async def async_get_db():
    """Асинхронный генератор сессий"""
    async with AsyncSessionLocal() as session:
        yield session