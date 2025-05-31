from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker, declarative_base
from config.config import settings
import logging

logger = logging.getLogger(__name__)

# Базовый класс для моделей
Base = declarative_base()

def get_database_url() -> str:
    """Получаем URL базы данных с учетом асинхронного режима"""
    db_url = settings.DATABASE_URL
    if "sqlite" in db_url:
        return db_url.replace("sqlite://", "sqlite+aiosqlite://")
    return db_url

# Синхронные подключения (для Alembic и CLI-утилит)
sync_engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
    echo=settings.DB_ECHO
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=sync_engine,
    expire_on_commit=False
)

# Асинхронные подключения (для основного приложения)
async_engine = create_async_engine(
    get_database_url(),
    echo=settings.DB_ECHO,
    **({} if "sqlite" in settings.DATABASE_URL else {
        "pool_size": 20,
        "max_overflow": 10,
        "pool_pre_ping": True
    })
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

def get_db():
    """Генератор синхронных сессий"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def async_get_db():
    """Генератор асинхронных сессий"""
    async with AsyncSessionLocal() as session:
        yield session
async def init_models():
    """Создание таблиц в базе данных"""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

def get_db():
    """Синхронный генератор сессий"""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

async def async_get_db():
    """Асинхронный генератор сессий"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Async database error: {e}")
            raise
        finally:
            await session.close()