from aiogram import Dispatcher, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from keyboards.admin_kb import (
    get_admin_keyboard,
    get_user_management_keyboard,
    get_menu_management_keyboard
)
from database.crud import (
    get_user_by_id,
    update_user_role,
    search_users,
    get_orders_stats,
    get_menu_categories,
    update_menu_item
)
from database.models import UserRole
from config.config import Config
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class AdminStates:
    USER_SEARCH = "admin_user_search"
    ROLE_EDIT = "admin_role_edit"
    MENU_ITEM_EDIT = "menu_item_edit"


async def admin_start(message: Message):
    """Главное меню админ-панели"""
    try:
        await message.answer(
            "🛠 Панель администратора",
            reply_markup=get_admin_keyboard()
        )
    except Exception as e:
        logger.error(f"Error in admin_start: {e}", exc_info=True)
        await message.answer("⚠️ Ошибка доступа к админ-панели")


async def handle_admin_stats(message: Message):
    """Обработчик статистики с реальными данными"""
    try:
        stats = get_orders_stats(message.bot.get('db'))
        response = (
            "📊 Статистика бота:\n\n"
            f"• Пользователей: {stats.get('total_users', 0)}\n"
            f"• Активных заказов: {stats.get('active_orders', 0)}\n"
            f"• Выручка: {stats.get('total_revenue', 0)} руб.\n"
            f"• Новых за неделю: {stats.get('weekly_orders', 0)}"
        )
        await message.answer(response)
    except Exception as e:
        logger.error(f"Error in handle_admin_stats: {e}", exc_info=True)
        await message.answer("⚠️ Ошибка получения статистики")


async def handle_user_management(message: Message):
    """Управление пользователями с inline-кнопками"""
    try:
        builder = InlineKeyboardBuilder()
        builder.button(text="По ID", callback_data="search_by_id")
        builder.button(text="По имени", callback_data="search_by_name")
        builder.button(text="Все менеджеры", callback_data="list_managers")
        builder.adjust(2)

        await message.answer(
            "👥 Выберите тип поиска:",
            reply_markup=builder.as_markup()
        )
    except Exception as e:
        logger.error(f"Error in handle_user_management: {e}", exc_info=True)
        await message.answer("⚠️ Ошибка управления пользователями")


async def handle_menu_management(message: Message):
    """Управление меню"""
    try:
        categories = get_menu_categories(message.bot.get('db'))
        builder = InlineKeyboardBuilder()

        for category in categories:
            builder.button(
                text=category.name,
                callback_data=f"category_{category.id}"
            )

        builder.adjust(2)
        await message.answer(
            "📝 Управление меню:",
            reply_markup=get_menu_management_keyboard()
        )
    except Exception as e:
        logger.error(f"Error in handle_menu_management: {e}", exc_info=True)
        await message.answer("⚠️ Ошибка управления меню")


async def process_role_selection(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора роли для пользователя"""
    try:
        data = callback.data.split('_')
        user_id = int(data[1])
        role = UserRole(data[2])

        if update_user_role(callback.bot.get('db'), user_id, role):
            await callback.message.edit_text(f"✅ Роль пользователя {user_id} изменена на {role.value}")
        else:
            await callback.message.edit_text("⚠️ Не удалось изменить роль")

    except Exception as e:
        logger.error(f"Error in process_role_selection: {e}", exc_info=True)
        await callback.message.edit_text("⚠️ Ошибка изменения роли")


def register_admin_handlers(dp: Dispatcher):
    """Регистрация обработчиков с проверкой прав"""
    try:
        # Основные команды
        dp.message.register(admin_start, Command("admin"))

        # Главное меню
        dp.message.register(handle_admin_stats, F.text == "📊 Статистика")
        dp.message.register(handle_user_management, F.text == "👥 Пользователи")
        dp.message.register(handle_menu_management, F.text == "📝 Меню")
        dp.message.register(handle_back_to_admin, F.text == "◀️ Назад")

        # Callback-обработчики
        dp.callback_query.register(process_role_selection, F.data.startswith("setrole_"))

        logger.info("Admin handlers registered successfully")
    except Exception as e:
        logger.error(f"Failed to register admin handlers: {e}", exc_info=True)
        raise