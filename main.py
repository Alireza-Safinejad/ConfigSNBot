import asyncio
import logging
import ssl
import certifi
import aiohttp
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import BOT_TOKEN, FREE_CONFIG_SCHEDULE
from database.db import init_db
from handlers.user import router as user_router
from handlers.admin import router as admin_router
from scheduler.daily_config import send_free_config, reset_daily_counter, collect_configs_from_channels

logging.basicConfig(level=logging.INFO)

ssl_context = ssl.create_default_context(cafile=certifi.where())
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

session = AiohttpSession()
session._connector_type = aiohttp.TCPConnector
session._connector_init = {"ssl": ssl_context}

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    session=session
)

dp = Dispatcher()
dp.include_router(user_router)
dp.include_router(admin_router)


async def main():
    await init_db()
    print("✅ دیتابیس آماده شد.")

    scheduler = AsyncIOScheduler(timezone="Asia/Tehran")

    # جمع‌آوری کانفیگ از کانال‌ها — هر ۲ ساعت یکبار
    scheduler.add_job(
        collect_configs_from_channels,
        trigger="interval",
        hours=2,
        args=[bot]
    )

    # ارسال کانفیگ رایگان طبق ساعات تعیین شده
    send_hours = [8, 12, 16, 20, 23]
    for hour in send_hours:
        scheduler.add_job(
            send_free_config,
            trigger="cron",
            hour=hour,
            minute=0,
            args=[bot]
        )

    # ریست شمارنده روزانه — هر شب ساعت ۰۰:۰۰
    scheduler.add_job(
        reset_daily_counter,
        trigger="cron",
        hour=0,
        minute=0
    )

    scheduler.start()
    print("✅ زمان‌بندی فعال شد.")

    # جمع‌آوری اولیه کانفیگ‌ها
    await collect_configs_from_channels(bot)

    print("✅ ربات شروع به کار کرد!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
