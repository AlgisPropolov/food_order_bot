from aiogram import Router, types
from aiogram.filters import Text

router = Router()

@router.message(Text(text="ℹ️ Помощь"))
async def show_help(message: types.Message):
    await message.answer(
        "❓ Помощь:\n\n"
        "/start - Главное меню\n"
        "/menu - Показать меню\n"
        "/cart - Показать корзину\n"
        "/help - Эта справка\n\n"
        "Техподдержка: @support"
    )