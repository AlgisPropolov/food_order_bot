import os
from dotenv import load_dotenv
from typing import Dict, Any, Optional
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Загрузка переменных окружения
load_dotenv()


class Config:
    # Основные настройки бота
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    ADMIN_IDS: list[int] = [
        int(id_str) for id_str in os.getenv("ADMIN_IDS", "").split(",") if id_str
    ]

    # Настройки подключения к БД
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///database.db")
    DB_ECHO: bool = os.getenv("DB_ECHO", "False").lower() == "true"

    # Настройки интеграции с iiko
    IIKO_API_URL: str = os.getenv("IIKO_API_URL", "https://api-ru.iiko.services")
    IIKO_CREDENTIALS: Dict[str, Optional[str]] = {
        "api_login": os.getenv("IIKO_API_LOGIN"),
        "password": os.getenv("IIKO_API_PASSWORD"),
        "organization_id": os.getenv("IIKO_ORG_ID"),
    }

    # Настройки логирования
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "bot.log")

    @classmethod
    def validate(cls) -> bool:
        """Проверка обязательных настроек"""
        errors = []

        if not cls.BOT_TOKEN:
            errors.append("Не указан BOT_TOKEN в .env")

        if not cls.ADMIN_IDS:
            errors.append("Не указаны ADMIN_IDS в .env")

        if not all(cls.IIKO_CREDENTIALS.values()):
            errors.append("Не все обязательные параметры для iiko API указаны")

        if errors:
            for error in errors:
                logger.error(error)
            logger.warning(f"Текущие настройки iiko: {cls.IIKO_CREDENTIALS}")
            return False
        return True


# Проверка конфигурации при импорте
if not Config.validate():
    logger.warning("Некоторые настройки не прошли валидацию!")

# Для удобства импорта
DATABASE_URL = Config.DATABASE_URL
BOT_TOKEN = Config.BOT_TOKEN
IIKO_CREDENTIALS = Config.IIKO_CREDENTIALS
ADMIN_IDS = Config.ADMIN_IDS
DB_ECHO = Config.DB_ECHO