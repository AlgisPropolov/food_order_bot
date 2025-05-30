from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import ReplyKeyboardMarkup

def main_keyboard() -> ReplyKeyboardMarkup:
    """Основная клавиатура"""
    builder = ReplyKeyboardBuilder()
    builder.button(text="🍽 Меню")
    builder.button(text="📦 Мои заказы")
    builder.button(text="🛒 Корзина")
    builder.button(text="ℹ️ Помощь")
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)