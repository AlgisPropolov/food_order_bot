from aiogram import F, types, Dispatcher
from aiogram.filters import Command

async def cmd_start(message: types.Message):
    """Обработчик команды /start"""
    await message.answer("Добро пожаловать в бот заказов!")

def register_start_handlers(dp: Dispatcher):
    """Регистрация стартовых обработчиков"""
    dp.message.register(cmd_start, Command("start"))