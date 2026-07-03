import aiohttp
from config import PLISIO_SECRET_KEY, USDT_WALLET


class PlisioService:
    def __init__(self):
        self.secret_key = PLISIO_SECRET_KEY
        self.base_url = "https://api.plisio.net/api/v1"

    async def create_invoice(self, amount_usd: float, order_id: str,
                             order_name: str) -> dict:
        params = {
            "api_key": self.secret_key,
            "currency": "USDT_TRX",
            "amount": amount_usd,
            "order_number": order_id,
            "order_name": order_name,
            "source_currency": "USD",
            "source_amount": amount_usd,
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/invoices/new",
                params=params
            ) as resp:
                return await resp.json()

    async def check_invoice(self, invoice_id: str) -> dict:
        params = {
            "api_key": self.secret_key,
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/operations/{invoice_id}",
                params=params
            ) as resp:
                return await resp.json()

    async def is_payment_completed(self, invoice_id: str) -> bool:
        data = await self.check_invoice(invoice_id)
        if data.get("status") == "success":
            status = data.get("data", {}).get("status", "")
            return status in ["completed", "mismatch"]
        return False


plisio = PlisioService()
