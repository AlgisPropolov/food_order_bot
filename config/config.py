import os
from dotenv import load_dotenv
from typing import Dict, Any

load_dotenv()


class Config:
    # Основные настройки бота
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    if not BOT_TOKEN:
        raise ValueError("Не указан BOT_TOKEN в .env файле или переменных окружения")

    # Настройки подключения к БД
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///database.db")

    # Настройки интеграции с iiko
    IIKO_CREDENTIALS: Dict[str, Any] = {
        "login": os.getenv("IIKO_API_LOGIN"),
        "password": os.getenv("IIKO_API_PASSWORD"),
        "org_id": os.getenv("IIKO_ORG_ID"),
    }

    @classmethod
    def validate_iiko_credentials(cls) -> bool:
        """Проверяет, заполнены ли обязательные поля для iiko."""
        if not all(cls.IIKO_CREDENTIALS.values()):
            print(
                "Предупреждение: Не все обязательные параметры для iiko API указаны\n"
                f"Текущие значения: {cls.IIKO_CREDENTIALS}"
            )
            return False
        return True


# Проверяем настройки (без вызова исключения)
Config.validate_iiko_credentials()

# Для удобства импорта
DATABASE_URL = Config.DATABASE_URL
BOT_TOKEN = Config.BOT_TOKEN
IIKO_CREDENTIALS = Config.IIKO_CREDENTIALS