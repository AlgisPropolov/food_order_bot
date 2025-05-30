from aiogram import types, Dispatcher
from aiogram.filters import Command
from keyboards.main_kb import main_keyboard

async def cmd_start(message: types.Message):
    """Обработчик команды /start с клавиатурой"""
    await message.answer(
        "🍔 Бот для заказов готов к работе!\n"
        "Выберите действие:",
        reply_markup=main_keyboard()
    )

def register_start_handlers(dp: Dispatcher):
    """Регистрация обработчиков"""
    dp.message.register(cmd_start, Command(commands=["start", "старт"]))