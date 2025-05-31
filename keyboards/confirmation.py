from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import ReplyKeyboardMarkup

def confirmation_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура для подтверждения заказа"""
    builder = ReplyKeyboardBuilder()
    builder.button(text="✅ Подтвердить")
    builder.button(text="❌ Отменить")
    builder.adjust(2)
    return builder.as_markup(
        resize_keyboard=True,
        input_field_placeholder="Подтвердите заказ"
    )