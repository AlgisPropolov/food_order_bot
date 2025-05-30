from aiogram import Dispatcher
import logging
import importlib
from typing import List

logger = logging.getLogger(__name__)


def register_handlers(dp: Dispatcher) -> None:
    """Регистрация всех обработчиков"""
    handler_modules = get_handler_modules()

    for module_name in handler_modules:
        try:
            module = importlib.import_module(f"handlers.{module_name}")
            register_func = getattr(module, f"register_{module_name}_handlers", None)

            if register_func:
                register_func(dp)
                logger.info(f"Успешно зарегистрирован модуль {module_name}")
            else:
                logger.warning(f"Функция регистрации не найдена в {module_name}")

        except ImportError as e:
            logger.warning(f"Модуль {module_name} не найден: {e}")
        except Exception as e:
            logger.error(f"Ошибка в модуле {module_name}: {e}", exc_info=True)


def get_handler_modules() -> List[str]:
    """Список модулей обработчиков"""
    return ["start", "menu", "order", "faq", "admin"]  # Убрал cancel_order