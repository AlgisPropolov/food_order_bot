from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def cart_keyboard() -> ReplyKeyboardMarkup:
    """
    Создает клавиатуру для управления корзиной
    с использованием современного ReplyKeyboardBuilder
    """
    builder = ReplyKeyboardBuilder()
    builder.button(text="💳 Оформить заказ")
    builder.button(text="❌ Очистить корзину")
    builder.button(text="⬅️ Назад")
    builder.adjust(2)  # Первые две кнопки в одном ряду
    return builder.as_markup(
        resize_keyboard=True,
        input_field_placeholder="Выберите действие"
    )


def create_cart_keyboard(items: list) -> ReplyKeyboardMarkup:
    """
    Создает интерактивную клавиатуру для элементов корзины
    (если нужна в вашем проекте)
    """
    builder = ReplyKeyboardBuilder()

    # Добавляем кнопки для каждого товара
    for item in items:
        builder.button(text=f"❌ {item['name']}")

    # Добавляем управляющие кнопки
    builder.button(text="💳 Оформить заказ")
    builder.button(text="⬅️ Назад")
    builder.adjust(1, 2)  # Товары по одному, управляющие кнопки вместе

    return builder.as_markup(
        resize_keyboard=True,
        input_field_placeholder="Выберите товар для удаления"
    )