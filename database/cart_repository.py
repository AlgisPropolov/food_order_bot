from typing import Optional, List, Dict
from dataclasses import dataclass


@dataclass
class Cart:
    user_id: int
    items: List[Dict]


class CartRepository:
    async def get_cart(self, user_id: int) -> Optional[Cart]:
        """Получает корзину пользователя"""
        pass

    async def add_item(self, user_id: int, product_id: str, name: str, price: float, quantity: int):
        """Добавляет товар в корзину"""
        pass

    async def remove_item(self, user_id: int, item_id: str):
        """Удаляет товар из корзины"""
        pass

    async def clear_cart(self, user_id: int):
        """Очищает корзину"""
        pass