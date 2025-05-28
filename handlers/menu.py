from aiogram import Bot, Dispatcher, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from iiko_integration.iiko_api import IikoAPI
from keyboards.inline import menu_categories_keyboard
import logging


async def show_menu(message: Message, state: FSMContext):
    """
    Показывает категории меню из iiko
    Args:
        message: Объект сообщения
        state: Текущее состояние FSM
    """
    try:
        iiko = IikoAPI()
        menu = await iiko.get_menu()

        if not menu:
            await message.answer("⚠️ Меню временно недоступно. Попробуйте позже.")
            return

        categories = menu.get("groups", [])
        if not categories:
            await message.answer("🍽 Категории пока пусты.")
            return

        await message.answer(
            "🍽 Выберите категорию:",
            reply_markup=menu_categories_keyboard(categories)
        )

    except Exception as e:
        await message.answer("⚠️ Ошибка загрузки меню.")
        logging.error(f"Error in show_menu: {e}", exc_info=True)


async def handle_category(callback: CallbackQuery, state: FSMContext):
    """
    Обработка выбора категории и показ товаров
    Args:
        callback: Callback запрос
        state: Текущее состояние FSM
    """
    try:
        category_id = callback.data.split("_")[1]
        iiko = IikoAPI()
        menu = await iiko.get_menu()

        if not menu:
            await callback.message.edit_text("⚠️ Ошибка загрузки меню.")
            return

        products = [
            item for item in menu["products"]
            if item["parentGroup"] == category_id
        ]

        if not products:
            await callback.message.edit_text("🍽 В этой категории пока нет позиций.")
            return

        response = "🍜 Доступные позиции:\n" + "\n".join(
            f"{p['name']} - {p['price']} руб."
            for p in sorted(products, key=lambda x: x['name'])
        )

        await callback.message.edit_text(response)

    except Exception as e:
        await callback.message.edit_text("⚠️ Произошла ошибка. Попробуйте позже.")
        logging.error(f"Error in handle_category: {e}", exc_info=True)


def register_menu_handlers(dp: Dispatcher):
    """
    Регистрация всех обработчиков меню
    Args:
        dp: Диспетчер бота
    """
    # Обработка текстовых команд и кнопки меню
    dp.message.register(
        show_menu,
        Command("menu") | F.text == "🍜 Меню"  # Комбинация фильтров
    )

    # Обработка выбора категории
    dp.callback_query.register(
        handle_category,
        F.data.startswith("category_")
    )