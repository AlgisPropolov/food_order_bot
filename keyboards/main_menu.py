from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def main_menu_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("🍜 Меню"))
    markup.add(KeyboardButton("📦 Мои заказы"), KeyboardButton("❓ Помощь"))
    return markup