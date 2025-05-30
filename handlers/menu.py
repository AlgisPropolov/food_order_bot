from aiogram import Router, types, Bot, F
from aiogram.filters import Command, Text
from aiogram.fsm.context import FSMContext
from typing import Optional
from keyboards import (
    main_keyboard,
    menu_categories_keyboard,
    menu_products_keyboard
)
from services.iiko_service import IikoService
import logging

router = Router()


async def show_menu(
        message: types.Message,
        iiko_service: IikoService,
        state: FSMContext
):
    """
    Отображает главное меню с категориями
    """
    try:
        # Получаем меню из iiko
        menu = await iiko_service.get_menu()

        if not menu or not menu.categories:
            await message.answer(
                "🍽 Меню временно недоступно. Попробуйте позже.",
                reply_markup=main_keyboard()
            )
            return

        # Сохраняем меню в состоянии
        await state.update_data(menu=menu.dict())

        # Отправляем клавиатуру с категориями
        await message.answer(
            "🍽 Выберите категорию:",
            reply_markup=menu_categories_keyboard(menu.categories)
        )

    except Exception as e:
        logging.error(f"Menu error: {e}", exc_info=True)
        await message.answer(
            "⚠️ Ошибка загрузки меню",
            reply_markup=main_keyboard()
        )


async def handle_category_selection(
        callback: types.CallbackQuery,
        iiko_service: IikoService,
        state: FSMContext,
        bot: Optional[Bot] = None
):
    """
    Обрабатывает выбор категории и показывает товары
    """
    try:
        category_id = callback.data.split('_')[1]
        data = await state.get_data()
        menu = data.get('menu')

        if not menu:
            await callback.answer("Меню устарело, запрашиваю новое...")
            menu = await iiko_service.get_menu()
            await state.update_data(menu=menu.dict())

        # Находим выбранную категорию
        category = next(
            (c for c in menu['categories'] if c['id'] == category_id),
            None
        )

        if not category:
            await callback.answer("Категория не найдена")
            return

        # Получаем товары категории
        products = [
            p for p in menu['products']
            if p['parentGroup'] == category_id
        ]

        if not products:
            await callback.message.edit_text(
                f"🍽 В категории '{category['name']}' пока нет позиций",
                reply_markup=menu_categories_keyboard(menu['categories'])
            )
            return

        # Отправляем товары с пагинацией
        await callback.message.edit_text(
            f"🍽 {category['name']}:\n\n" +
            "\n".join(f"• {p['name']} - {p['price']}₽" for p in products[:10]),
            reply_markup=menu_products_keyboard(products, category_id)
        )

    except Exception as e:
        logging.error(f"Category error: {e}", exc_info=True)
        await callback.message.edit_text(
            "⚠️ Ошибка загрузки категории",
            reply_markup=main_keyboard()
        )


async def handle_product_selection(
        callback: types.CallbackQuery,
        state: FSMContext
):
    """
    Обрабатывает выбор товара
    """
    try:
        product_id = callback.data.split('_')[1]
        data = await state.get_data()

        product = next(
            (p for p in data['menu']['products'] if p['id'] == product_id),
            None
        )

        if product:
            await callback.message.answer(
                f"🍕 {product['name']}\n\n"
                f"Цена: {product['price']}₽\n"
                f"Состав: {product.get('description', 'нет описания')}\n\n"
                "Добавить в корзину /add_{product_id}"
            )
        else:
            await callback.answer("Товар не найден")

    except Exception as e:
        logging.error(f"Product error: {e}", exc_info=True)
        await callback.answer("Ошибка загрузки товара")


def register_menu_handlers(dp: Dispatcher, iiko_service: IikoService):
    """
    Регистрирует обработчики меню
    """
    # Текстовая команда /menu и кнопка "Меню"
    dp.message.register(
        lambda message: show_menu(message, iiko_service, dp.fsm),
        Command("menu") | Text(text="🍽 Меню")
    )

    # Обработка выбора категории
    dp.callback_query.register(
        lambda callback: handle_category_selection(callback, iiko_service, dp.fsm, dp.bot),
        F.data.startswith("category_")
    )

    # Обработка выбора товара
    dp.callback_query.register(
        handle_product_selection,
        F.data.startswith("product_")
    )