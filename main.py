import logging
from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from config.config import settings
from handlers import register_handlers
from handlers.cart import register_cart_handlers
from database.cart_repository import CartRepository
from services.iiko_service import IikoService
import asyncio

# Настройка логирования
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(settings.LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def on_startup(bot: Bot):
    """Действия при запуске бота"""
    try:
        commands = [
            types.BotCommand(command="start", description="Главное меню"),
            types.BotCommand(command="help", description="Помощь"),
            types.BotCommand(command="cart", description="Корзина"),
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
    """Основная функция запуска бота"""
    try:
        # Инициализация сервисов
        iiko_service = IikoService(
            api_login=settings.IIKO_API_LOGIN,
            api_password=settings.IIKO_API_PASSWORD,
            organization_id=settings.IIKO_ORG_ID,
            base_url=settings.IIKO_API_URL
        )
        cart_repo = CartRepository()

        # Инициализация бота
        bot = Bot(
            token=settings.BOT_TOKEN,
            default=DefaultBotProperties(
                parse_mode="HTML",
                link_preview_is_disabled=True
            )
        )

        # Инициализация диспетчера
        dp = Dispatcher(storage=MemoryStorage())

        # Регистрация обработчиков
        register_handlers(dp)
        register_cart_handlers(dp, cart_repo, iiko_service)

        # Подключение обработчиков жизненного цикла
        dp.startup.register(on_startup)
        dp.shutdown.register(on_shutdown)

        # Удаление вебхука (на всякий случай)
        await bot.delete_webhook(drop_pending_updates=True)

        # Запуск бота
        logger.info("Запуск бота...")
        await dp.start_polling(
            bot,
            skip_updates=True,
            allowed_updates=dp.resolve_used_update_types()
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