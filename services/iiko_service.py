from dataclasses import dataclass
from typing import List, Dict
import aiohttp


@dataclass
class MenuCategory:
    id: str
    name: str
    description: str


@dataclass
class MenuProduct:
    id: str
    name: str
    price: float
    description: str
    parentGroup: str


class IikoService:
    def __init__(self, api_login: str, organization_id: str):
        self.api_login = api_login
        self.org_id = organization_id

    async def get_menu(self) -> Dict:
        """Получает меню из iiko"""
        async with aiohttp.ClientSession() as session:
            # Реализация API-запроса
            pass