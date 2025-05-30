import os
from dotenv import load_dotenv
from typing import Dict, List
from pydantic_settings import BaseSettings
from pydantic import validator
import logging

# Загрузка переменных окружения
load_dotenv()


class Settings(BaseSettings):
    """Основной класс настроек приложения"""

    # Основные настройки бота
    BOT_TOKEN: str = ""
    ADMIN_IDS: List[int] = []

    # Настройки базы данных
    DATABASE_URL: str = "sqlite:///database.db"
    DB_ECHO: bool = False

    # Настройки iikoCloud API
    IIKO_API_URL: str = "https://api-ru.iiko.services"
    IIKO_API_LOGIN: str = ""
    IIKO_API_PASSWORD: str = ""
    IIKO_ORG_ID: str = ""

    # Настройки логирования
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "bot.log"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @validator("ADMIN_IDS", pre=True)
    def parse_admin_ids(cls, v):
        if isinstance(v, str):
            return [int(id_str.strip()) for id_str in v.split(",") if id_str.strip()]
        return v or []

    @validator("DB_ECHO", pre=True)
    def parse_db_echo(cls, v):
        if isinstance(v, str):
            return v.lower() == "true"
        return v


class Config:
    """Обертка для удобного доступа к настройкам"""

    def __init__(self):
        self.settings = Settings()
        self.validate()

    def validate(self):
        """Проверка обязательных параметров"""
        errors = []

        if not self.settings.BOT_TOKEN:
            errors.append("Не указан BOT_TOKEN в .env")

        if not self.settings.ADMIN_IDS:
            errors.append("Не указаны ADMIN_IDS в .env")

        required_iiko = [
            self.settings.IIKO_API_LOGIN,
            self.settings.IIKO_API_PASSWORD,
            self.settings.IIKO_ORG_ID
        ]

        if not all(required_iiko):
            errors.append("Не все обязательные параметры для iiko API указаны")

        if errors:
            for error in errors:
                logging.error(error)
            logging.warning(f"Текущие настройки iiko: {required_iiko}")
            raise ValueError("Ошибка валидации конфигурации")

        logging.info("Конфигурация успешно загружена")


# Инициализация конфига
try:
    config = Config()
except Exception as e:
    logging.critical(f"Ошибка загрузки конфигурации: {e}")
    raise