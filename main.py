from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config.config import Config
from handlers import register_handlers
import logging
import asyncio

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("bot.log"),  # Логи в файл
        logging.StreamHandler()  # Логи в консоль
    ]
)
logger = logging.getLogger(__name__)


async def on_startup():
    """Действия при запуске бота"""
    logger.info("✅ Бот успешно запущен")
    # Здесь можно добавить дополнительные действия при запуске
    # Например: уведомление админа, загрузку данных и т.д.


async def on_shutdown():
    """Действия при завершении работы"""
    logger.info("⛔ Бот завершает работу")
    # Здесь можно добавить cleanup-действия


async def main():
    """Основная асинхронная функция запуска бота"""
    try:
        # Инициализация бота с HTML-разметкой по умолчанию
        bot = Bot(token=Config.BOT_TOKEN, parse_mode="HTML")

        # Настройка хранилища состояний
        storage = MemoryStorage()
        dp = Dispatcher(storage=storage)

        # Регистрация обработчиков
        register_handlers(dp)

        # Запуск бота с настройками
        await dp.start_polling(
            bot,
            on_startup=on_startup,
            on_shutdown=on_shutdown,
            skip_updates=True,
            allowed_updates=dp.resolve_used_update_types(),
            close_bot_session=True
        )
    except Exception as e:
        logger.critical(f"⛔ Критическая ошибка: {e}", exc_info=True)
    finally:
        if 'bot' in locals():
            await bot.session.close()
            logger.info("Сессия бота корректно закрыта")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен вручную")
    except Exception as e:
        logger.critical(f"Непредвиденная ошибка: {e}", exc_info=True)