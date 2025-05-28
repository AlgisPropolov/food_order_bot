from aiogram import Dispatcher, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

async def process_order(message: Message, state: FSMContext):
    """Обработчик начала оформления заказа"""
    await message.answer("Давайте оформим ваш заказ...")

def register_order_handlers(dp: Dispatcher):
    """Регистрация обработчиков заказов"""
    dp.message.register(process_order, F.text == "🛒 Оформить заказ")