import os
from dotenv import load_dotenv
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import field_validator
import logging

# Настройка логирования до загрузки конфига
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
    ]
)
logger = logging.getLogger(__name__)

# Загрузка переменных окружения
load_dotenv()


class AppSettings(BaseSettings):
    """Основные настройки приложения"""

    # Telegram Bot
    BOT_TOKEN: str
    ADMIN_IDS: List[int] = []

    # Database
    DATABASE_URL: str = "sqlite:///database.db"
    DB_ECHO: bool = False

    # iikoCloud API
    IIKO_API_URL: str = "https://api-ru.iiko.services"
    IIKO_API_LOGIN: str
    IIKO_API_PASSWORD: str
    IIKO_ORG_ID: str

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: Optional[str] = "bot.log"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

    @field_validator('ADMIN_IDS', mode='before')
    @classmethod
    def parse_admin_ids(cls, value):
        if isinstance(value, str):
            try:
                if value.startswith('[') and value.endswith(']'):
                    # JSON-формат
                    return [int(i) for i in value.strip('[]').split(',')]
                # Простой список через запятую
                return [int(i.strip()) for i in value.split(',') if i.strip()]
            except ValueError as e:
                logger.error(f"Ошибка парсинга ADMIN_IDS: {e}")
                raise ValueError("ADMIN_IDS должен содержать только числа")
        return value or []

    @field_validator('DB_ECHO', mode='before')
    @classmethod
    def parse_db_echo(cls, value):
        if isinstance(value, str):
            return value.lower() in ('true', '1', 'yes')
        return value


def load_config() -> AppSettings:
    """Загрузка и валидация конфигурации"""
    try:
        config = AppSettings()

        # Валидация обязательных полей
        if not config.BOT_TOKEN:
            raise ValueError("BOT_TOKEN не указан в .env")

        if not all([config.IIKO_API_LOGIN, config.IIKO_API_PASSWORD, config.IIKO_ORG_ID]):
            raise ValueError("Не все обязательные параметры для iiko API указаны")

        # Настройка логирования
        if config.LOG_FILE:
            file_handler = logging.FileHandler(config.LOG_FILE, encoding='utf-8')
            file_handler.setLevel(config.LOG_LEVEL)
            logging.getLogger().addHandler(file_handler)

        logger.info("Конфигурация успешно загружена")
        return config

    except Exception as e:
        logger.critical(f"Ошибка загрузки конфигурации: {e}")
        raise


# Глобальный объект настроек
settings: AppSettings = load_config()