from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup
from database.models import UserRole

def get_admin_keyboard() -> ReplyKeyboardMarkup:
    """Основная клавиатура админ-панели"""
    builder = ReplyKeyboardBuilder()
    builder.button(text="📊 Статистика")
    builder.button(text="👥 Управление пользователями")
    builder.button(text="📝 Управление меню")
    builder.button(text="📦 Управление заказами")
    builder.button(text="⚙️ Настройки системы")
    builder.button(text="◀️ В главное меню")
    builder.adjust(2, 2, 1, 1)
    return builder.as_markup(resize_keyboard=True)

def get_user_management_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура управления пользователями"""
    builder = ReplyKeyboardBuilder()
    builder.button(text="🔍 Поиск пользователя")
    builder.button(text="📝 Изменить права")
    builder.button(text="📨 Отправить сообщение")
    builder.button(text="🚫 Заблокировать")
    builder.button(text="✅ Разблокировать")
    builder.button(text="◀️ Назад")
    builder.adjust(2, 2, 1, 1)
    return builder.as_markup(resize_keyboard=True)

def get_menu_management_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура управления меню"""
    builder = ReplyKeyboardBuilder()
    builder.button(text="📋 Список категорий")
    builder.button(text="➕ Добавить позицию")
    builder.button(text="✏️ Редактировать позицию")
    builder.button(text="👁️ Скрыть/показать")
    builder.button(text="📦 Импорт из iiko")
    builder.button(text="◀️ Назад")
    builder.adjust(2, 2, 1, 1)
    return builder.as_markup(resize_keyboard=True)

def get_orders_management_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура управления заказами"""
    builder = ReplyKeyboardBuilder()
    builder.button(text="📋 Активные заказы")
    builder.button(text="📦 Заказы за сегодня")
    builder.button(text="📆 История заказов")
    builder.button(text="🔄 Изменить статус")
    builder.button(text="👤 Назначить курьера")
    builder.button(text="◀️ Назад")
    builder.adjust(2, 2, 1, 1)
    return builder.as_markup(resize_keyboard=True)

def get_role_selection_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """Inline-клавиатура для выбора роли"""
    builder = InlineKeyboardBuilder()
    for role in UserRole:
        builder.button(
            text=f"{role.value.capitalize()}",
            callback_data=f"setrole_{user_id}_{role.value}"
        )
    builder.button(
        text="❌ Отмена",
        callback_data="cancel_action"
    )
    builder.adjust(2, 1)
    return builder.as_markup()

def get_confirmation_keyboard(action: str) -> InlineKeyboardMarkup:
    """Клавиатура подтверждения действия"""
    builder = InlineKeyboardBuilder()
    builder.button(
        text="✅ Подтвердить",
        callback_data=f"confirm_{action}"
    )
    builder.button(
        text="❌ Отменить",
        callback_data="cancel_action"
    )
    return builder.as_markup()

def get_pagination_keyboard(page: int, total_pages: int, prefix: str) -> InlineKeyboardMarkup:
    """Клавиатура пагинации"""
    builder = InlineKeyboardBuilder()
    builder.button(
        text="⬅️ Назад",
        callback_data=f"{prefix}_page_{max(1, page-1)}"
    )
    builder.button(
        text=f"{page}/{total_pages}",
        callback_data="current_page"
    )
    builder.button(
        text="Вперед ➡️",
        callback_data=f"{prefix}_page_{min(total_pages, page+1)}"
    )
    return builder.as_markup()