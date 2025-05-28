from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def menu_categories_keyboard(categories: list):
    markup = InlineKeyboardMarkup()
    for category in categories:
        markup.add(
            InlineKeyboardButton(
                category["name"],
                callback_data=f"category_{category['id']}"
            )
        )
    return markup