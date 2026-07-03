import aiohttp
from config import MARZBAN_URL, MARZBAN_USERNAME, MARZBAN_PASSWORD


class MarzbanService:
    def __init__(self):
        self.base_url = MARZBAN_URL
        self.token = None

    async def get_token(self):
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/api/admin/token",
                data={
                    "username": MARZBAN_USERNAME,
                    "password": MARZBAN_PASSWORD
                }
            ) as resp:
                data = await resp.json()
                self.token = data.get("access_token")
                return self.token

    async def create_user(self, username: str, data_limit_gb: float = 0,
                          expire_hours: int = 0) -> dict:
        if not self.token:
            await self.get_token()

        import time
        expire_timestamp = 0
        if expire_hours > 0:
            expire_timestamp = int(time.time()) + (expire_hours * 3600)

        data_limit_bytes = int(data_limit_gb * 1024 ** 3) if data_limit_gb > 0 else 0

        payload = {
            "username": username,
            "proxies": {
                "vless": {"flow": "xtls-rprx-vision"}
            },
            "inbounds": {
                "vless": ["VLESS TCP REALITY"]
            },
            "expire": expire_timestamp,
            "data_limit": data_limit_bytes,
            "data_limit_reset_strategy": "no_reset"
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/api/user",
                json=payload,
                headers={"Authorization": f"Bearer {self.token}"}
            ) as resp:
                return await resp.json()

    async def get_user(self, username: str) -> dict:
        if not self.token:
            await self.get_token()

        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/api/user/{username}",
                headers={"Authorization": f"Bearer {self.token}"}
            ) as resp:
                return await resp.json()

    async def delete_user(self, username: str) -> bool:
        if not self.token:
            await self.get_token()

        async with aiohttp.ClientSession() as session:
            async with session.delete(
                f"{self.base_url}/api/user/{username}",
                headers={"Authorization": f"Bearer {self.token}"}
            ) as resp:
                return resp.status == 200

    async def get_user_config_link(self, username: str) -> str:
        user_data = await self.get_user(username)
        links = user_data.get("links", [])
        if links:
            return links[0]
        return ""

    async def get_user_usage(self, username: str) -> dict:
        user_data = await self.get_user(username)
        used_bytes = user_data.get("used_traffic", 0)
        total_bytes = user_data.get("data_limit", 0)
        expire = user_data.get("expire", 0)
        status = user_data.get("status", "unknown")

        used_gb = round(used_bytes / (1024 ** 3), 2)
        total_gb = round(total_bytes / (1024 ** 3), 2) if total_bytes > 0 else 0

        return {
            "used_gb": used_gb,
            "total_gb": total_gb,
            "expire": expire,
            "status": status
        }


marzban = MarzbanService()
