import aiohttp
import os


PLISIO_SECRET_KEY = os.getenv("PLISIO_SECRET_KEY")
USDT_WALLET = os.getenv("USDT_WALLET")


class PlisioService:
    def __init__(self):
        self.secret_key = PLISIO_SECRET_KEY
        self.base_url = "https://api.plisio.net/api/v1"

    async def create_invoice(self, amount_usd: float, order_id: str, order_name: str) -> dict:
        params = {
            "api_key": self.secret_key,
            "currency": "USDT_TRX",
            "amount": str(amount_usd),
            "order_number": order_id,
            "order_name": order_name,
            "source_currency": "USD",
            "source_amount": str(amount_usd),
            "email": "noreply@configsn.com",
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/invoices/new",
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=15)
                ) as resp:
                    data = await resp.json()
                    print(f"Plisio response: {data}")
                    return data
        except Exception as e:
            print(f"❌ خطا در Plisio: {e}")
            return {"status": "error", "message": str(e)}

    async def check_invoice(self, invoice_id: str) -> dict:
        params = {"api_key": self.secret_key}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/operations/{invoice_id}",
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=15)
                ) as resp:
                    return await resp.json()
        except Exception as e:
            print(f"❌ خطا در check_invoice: {e}")
            return {}

    async def is_payment_completed(self, invoice_id: str) -> bool:
        data = await self.check_invoice(invoice_id)
        if data.get("status") == "success":
            status = data.get("data", {}).get("status", "")
            return status in ["completed", "mismatch"]
        return False


plisio = PlisioService()
