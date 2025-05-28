from aiogram import Dispatcher, F
from aiogram.types import Message

async def show_faq(message: Message):
    await message.answer("Часто задаваемые вопросы...")

def register_faq_handlers(dp: Dispatcher):
    dp.message.register(show_faq, F.text == "❓ Помощь")