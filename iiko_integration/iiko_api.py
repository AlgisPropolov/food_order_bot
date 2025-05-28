import requests
from config.config import Config
from config.logging_config import logger

class IikoAPI:
    def __init__(self):
        self.base_url = "https://api-ru.iiko.services"
        self.token = None

    async def _get_auth_token(self):
        """Получение токена авторизации iiko."""
        try:
            response = requests.post(
                f"{self.base_url}/api/1/access_token",
                json={
                    "apiLogin": Config.IIKO_CREDENTIALS["login"]
                }
            )
            response.raise_for_status()
            self.token = response.json().get("token")
            return self.token
        except Exception as e:
            logger.error(f"Ошибка авторизации в iiko: {e}")
            raise

    async def get_menu(self):
        """Получение меню из iiko."""
        if not self.token:
            await self._get_auth_token()

        try:
            response = requests.post(
                f"{self.base_url}/api/1/nomenclature",
                headers={"Authorization": f"Bearer {self.token}"},
                json={
                    "organizationId": Config.IIKO_CREDENTIALS["org_id"]
                }
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Ошибка получения меню: {e}")
            return None

    async def create_order(self, order_data: dict):
        """Отправка заказа в iiko."""
        if not self.token:
            await self._get_auth_token()

        try:
            response = requests.post(
                f"{self.base_url}/api/1/orders/create",
                headers={"Authorization": f"Bearer {self.token}"},
                json={
                    "organizationId": Config.IIKO_CREDENTIALS["org_id"],
                    "order": order_data
                }
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Ошибка создания заказа: {e}")
            return None