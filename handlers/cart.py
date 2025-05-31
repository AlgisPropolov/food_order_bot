from aiogram import Router, types, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram import Dispatcher
from typing import Optional, Dict, List
from database.cart_repository import CartRepository
from services.iiko_service import IikoService
from keyboards import (
    main_keyboard,
    cart_keyboard,
    confirmation_keyboard
)
import logging

logger = logging.getLogger(__name__)
router = Router()


class CartStates(StatesGroup):
    viewing_cart = State()
    checkout = State()


async def show_cart(
        message: types.Message,
        cart_repo: CartRepository,
        state: FSMContext
):
    """Показывает содержимое корзины пользователя"""
    try:
        user_id = message.from_user.id
        cart = await cart_repo.get_cart(user_id)

        if not cart or not cart.items:
            await message.answer(
                "🛒 Ваша корзина пуста",
                reply_markup=main_keyboard()
            )
            return

        total = sum(item['price'] * item['quantity'] for item in cart.items)

        cart_text = "🛒 Ваша корзина:\n\n" + "\n".join(
            f"{i + 1}. {item['name']} - {item['quantity']} x {item['price']}₽"
            for i, item in enumerate(cart.items)
        ) + f"\n\n💳 Итого: {total}₽"

        await state.set_state(CartStates.viewing_cart)
        await message.answer(
            cart_text,
            reply_markup=cart_keyboard()
        )

    except Exception as e:
        logger.error(f"Cart error: {e}", exc_info=True)
        await message.answer(
            "⚠️ Ошибка загрузки корзины",
            reply_markup=main_keyboard()
        )


async def add_to_cart(
        message: types.Message,
        cart_repo: CartRepository,
        state: FSMContext,
        product_id: str
):
    """Добавляет товар в корзину"""
    try:
        user_id = message.from_user.id
        data = await state.get_data()

        product = next(
            (p for p in data['menu']['products'] if p['id'] == product_id),
            None
        )

        if not product:
            await message.answer("Товар не найден")
            return

        await cart_repo.add_item(
            user_id=user_id,
            product_id=product_id,
            name=product['name'],
            price=product['price'],
            quantity=1
        )

        await message.answer(
            f"✅ {product['name']} добавлен в корзину",
            reply_markup=main_keyboard()
        )

    except Exception as e:
        logger.error(f"Add to cart error: {e}", exc_info=True)
        await message.answer(
            "⚠️ Ошибка добавления в корзину",
            reply_markup=main_keyboard()
        )


async def remove_from_cart(
        callback: types.CallbackQuery,
        cart_repo: CartRepository
):
    """Удаляет товар из корзины"""
    try:
        item_id = callback.data.split('_')[1]
        await cart_repo.remove_item(callback.from_user.id, item_id)

        await callback.message.edit_text(
            "✅ Товар удален из корзины",
            reply_markup=main_keyboard()
        )

    except Exception as e:
        logger.error(f"Remove from cart error: {e}", exc_info=True)
        await callback.answer("Ошибка удаления товара")


async def checkout_cart(
        message: types.Message,
        cart_repo: CartRepository,
        iiko_service: IikoService,
        state: FSMContext
):
    """Оформляет заказ из корзины"""
    try:
        user_id = message.from_user.id
        cart = await cart_repo.get_cart(user_id)

        if not cart or not cart.items:
            await message.answer("Корзина пуста")
            return

        total = sum(item['price'] * item['quantity'] for item in cart.items)

        await state.set_state(CartStates.checkout)
        await message.answer(
            f"Подтвердите заказ на сумму {total}₽:\n\n" +
            "\n".join(f"- {item['name']} x{item['quantity']}" for item in cart.items),
            reply_markup=confirmation_keyboard()
        )

    except Exception as e:
        logger.error(f"Checkout error: {e}", exc_info=True)
        await message.answer(
            "⚠️ Ошибка оформления заказа",
            reply_markup=main_keyboard()
        )


async def confirm_order(
        callback: types.CallbackQuery,
        cart_repo: CartRepository,
        iiko_service: IikoService,
        state: FSMContext
):
    """Подтверждает и отправляет заказ в iiko"""
    try:
        user_id = callback.from_user.id
        cart = await cart_repo.get_cart(user_id)

        # Отправка заказа в iiko
        order_id = await iiko_service.create_order(
            user_id=user_id,
            items=cart.items
        )

        # Очистка корзины
        await cart_repo.clear_cart(user_id)
        await state.clear()

        await callback.message.edit_text(
            f"✅ Заказ #{order_id} оформлен!\n"
            f"Статус можно проверить в /orders",
            reply_markup=main_keyboard()
        )

    except Exception as e:
        logger.error(f"Order confirmation error: {e}", exc_info=True)
        await callback.message.edit_text(
            "⚠️ Ошибка оформления заказа",
            reply_markup=main_keyboard()
        )


def register_cart_handlers(dp: Dispatcher, cart_repo: CartRepository, iiko_service: IikoService):
    """Регистрирует обработчики корзины"""
    # Просмотр корзины
    dp.message.register(
        lambda message: show_cart(message, cart_repo, dp.fsm),
        Command("cart") | F.text == "🛒 Корзина"
    )

    # Добавление в корзину
    dp.message.register(
        lambda message: add_to_cart(message, cart_repo, dp.fsm, message.text.split('_')[1]),
        Command(startswith="add_")
    )

    # Удаление из корзины
    dp.callback_query.register(
        lambda callback: remove_from_cart(callback, cart_repo),
        F.data.startswith("remove_")
    )

    # Оформление заказа
    dp.message.register(
        lambda message: checkout_cart(message, cart_repo, iiko_service, dp.fsm),
        F.text == "💳 Оформить заказ"
    )

    # Подтверждение заказа
    dp.callback_query.register(
        lambda callback: confirm_order(callback, cart_repo, iiko_service, dp.fsm),
        F.data == "confirm_order"
    )