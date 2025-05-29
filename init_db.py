from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database.session import async_engine, init_models, async_get_db
from database.models import Base
import asyncio
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def check_database_connection():
    """Проверяет соединение с базой данных"""
    try:
        async with async_engine.connect() as conn:
            result = await conn.execute(select(1))
            if result.scalar() == 1:
                return True
        return False
    except Exception as e:
        logger.error(f"Ошибка проверки соединения: {e}")
        return False


async def initialize_database():
    """
    Полная инициализация базы данных:
    1. Создает таблицы
    2. Проверяет соединение
    3. Возвращает статус
    """
    try:
        logger.info("Начало инициализации базы данных...")

        # Создание таблиц
        await init_models()

        # Проверка соединения
        if not await check_database_connection():
            raise ConnectionError("Не удалось подключиться к базе данных")

        logger.info("✅ База данных успешно инициализирована")
        return True

    except Exception as e:
        logger.error(f"❌ Ошибка инициализации: {e}")
        return False


if __name__ == "__main__":
    result = asyncio.run(initialize_database())
    if not result:
        exit(1)