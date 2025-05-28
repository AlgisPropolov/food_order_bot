from aiogram import Dispatcher
from typing import Optional
import logging

logger = logging.getLogger(__name__)


def register_all_handlers(dp: Dispatcher) -> bool:
    """
    Регистрация всех обработчиков бота с обработкой ошибок

    Args:
        dp: Экземпляр диспетчера aiogram

    Returns:
        bool: True если все обработчики зарегистрированы успешно, False при ошибке
    """
    try:
        # Импорты обработчиков
        from .start import register_start_handlers
        from .menu import register_menu_handlers
        from .order import register_order_handlers
        from .cancel_order import register_cancel_handlers
        from .faq import register_faq_handlers
        from .admin import register_admin_handlers  # Новый модуль

        # Регистрация обработчиков
        register_start_handlers(dp)
        register_menu_handlers(dp)
        register_order_handlers(dp)
        register_cancel_handlers(dp)
        register_faq_handlers(dp)

        # Попытка зарегистрировать административные обработчики
        try:
            register_admin_handlers(dp)
        except ImportError:
            logger.warning("Admin handlers not registered - module not found")

        logger.info("All handlers registered successfully")
        return True

    except Exception as e:
        logger.error(f"Failed to register handlers: {e}", exc_info=True)
        return False


def register_handlers(dp: Dispatcher) -> None:
    """Основная функция регистрации обработчиков (для обратной совместимости)"""
    if not register_all_handlers(dp):
        raise RuntimeError("Failed to register some handlers")


# Альтернативный вариант для поэтапной регистрации
def get_handler_modules() -> list[str]:
    """Возвращает список модулей с обработчиками"""
    return [
        'start',
        'menu',
        'order',
        'cancel_order',
        'faq',
        'admin'  # Опциональный модуль
    ]