from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker, declarative_base
from config.config import DATABASE_URL
import logging

logger = logging.getLogger(__name__)

# Базовый класс для моделей
Base = declarative_base()

# Синхронные подключения (для Alembic и CLI-утилит)
sync_engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    echo=False
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=sync_engine,
    expire_on_commit=False
)

# Асинхронные подключения (для основного приложения)
async_engine = create_async_engine(
    DATABASE_URL.replace("sqlite://", "sqlite+aiosqlite://") if "sqlite" in DATABASE_URL else DATABASE_URL,
    echo=True,
    # Для SQLite убираем параметры пула, для других СУБД можно оставить
    **({} if "sqlite" in DATABASE_URL else {
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