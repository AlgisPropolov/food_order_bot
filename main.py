from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from config.config import Config
from handlers import register_handlers
from handlers.cart import register_cart_handlers
from database.cart_repository import CartRepository
from services.iiko_service import IikoService
import logging
import asyncio

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("bot.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


async def on_startup(bot: Bot):
    """Действия при запуске бота"""
    try:
        commands = [
            types.BotCommand(command="/start", description="Главное меню"),
            types.BotCommand(command="/help", description="Помощь"),
        ]
        await bot.set_my_commands(commands)
        logger.info("✅ Бот успешно запущен")
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}", exc_info=True)


async def on_shutdown(bot: Bot):
    """Действия при завершении работы"""
    logger.info("⛔ Бот завершает работу")
    try:
        await bot.session.close()
    except Exception as e:
        logger.error(f"Ошибка при закрытии сессии: {e}")


async def main():
    """Основная асинхронная функция запуска бота"""
    try:
        # Инициализация конфигурации
        config = Config()

        # Инициализация сервисов
        iiko_service = IikoService(
            api_login=config.IIKO_API_LOGIN,
            organization_id=config.IIKO_ORG_ID
        )
        cart_repo = CartRepository()

        # Инициализация бота
        bot = Bot(
            token=config.BOT_TOKEN,
            default=DefaultBotProperties(
                parse_mode="HTML",
                link_preview_is_disabled=True
            )
        )

        # Настройка диспетчера
        dp = Dispatcher(storage=MemoryStorage())

        # Регистрация обработчиков
        register_handlers(dp)
        register_cart_handlers(dp, cart_repo, iiko_service)

        # Установка обработчиков жизненного цикла
        dp.startup.register(on_startup)
        dp.shutdown.register(on_shutdown)

        # Запуск бота
        await dp.start_polling(
            bot,
            skip_updates=True,
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