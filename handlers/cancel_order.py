from aiogram import Dispatcher, F
from aiogram.types import Message

async def cancel_order(message: Message):
    await message.answer("Ваш заказ отменен")

def register_cancel_handlers(dp: Dispatcher):
    dp.message.register(cancel_order, F.text == "❌ Отменить заказ")