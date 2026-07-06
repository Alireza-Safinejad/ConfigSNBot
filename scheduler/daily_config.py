import re
import aiohttp
from aiogram import Bot
from config import CHANNEL_ID
from database.db import save_config, get_unused_config, get_configs_count, delete_old_configs

SOURCE_CHANNELS = [
    "mitivpn",
    "irantweety",
    "drmobileiir"
]

MAX_CONFIGS_PER_DAY = 10
configs_sent_today = 0

HEADERS = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15",
    "Accept-Language": "fa-IR,fa;q=0.9,en;q=0.8",
}


def extract_configs(text: str) -> list:
    patterns = [
        r'vless://[A-Za-z0-9+/=@:.\-_?#&%]+',
        r'vmess://[A-Za-z0-9+/=]+',
        r'trojan://[A-Za-z0-9+/=@:.\-_?#&%]+',
        r'ss://[A-Za-z0-9+/=@:.\-_?#&%]+',
        r'hy2://[A-Za-z0-9+/=@:.\-_?#&%]+',
        r'hysteria2://[A-Za-z0-9+/=@:.\-_?#&%]+',
    ]
    configs = []
    for pattern in patterns:
        found = re.findall(pattern, text)
        configs.extend(found)
    return list(set(configs))


async def collect_configs_from_channels(bot: Bot = None):
    total_new = 0
    for channel in SOURCE_CHANNELS:
        try:
            url = f"https://t.me/s/{channel}"
            async with aiohttp.ClientSession(headers=HEADERS) as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=20)) as resp:
                    if resp.status == 200:
                        html = await resp.text()
                        configs = extract_configs(html)
                        for config in configs:
                            await save_config(config, channel)
                        total_new += len(configs)
                        print(f"✅ {len(configs)} کانفیگ از {channel} دریافت شد.")
        except Exception as e:
            print(f"❌ خطا در دریافت از {channel}: {e}")

    count = await get_configs_count()
    print(f"✅ کل کانفیگ‌های موجود: {count}")


async def get_next_config() -> str:
    config = await get_unused_config()
    if not config:
        await collect_configs_from_channels()
        config = await get_unused_config()
    return config


async def send_free_config(bot: Bot):
    global configs_sent_today

    if configs_sent_today >= MAX_CONFIGS_PER_DAY:
        print("⚠️ حداکثر کانفیگ روزانه ارسال شده.")
        return

    config_link = await get_next_config()

    if not config_link:
        print("⚠️ کانفیگی برای ارسال وجود ندارد.")
        return

    text = (
        "🎁 کانفیگ رایگان\n\n"
        "👇 روی لینک زیر بزن و کپی کن:\n\n"
        f"`{config_link}`\n\n"
        "داخل V2rayNG یا Streisand یا V2rayN وارد کن.\n\n"
        "━━━━━━━━━━━━━━━\n"
        "💎 کانفیگ VIP پایدار و سریع:\n"
        "👉 @ConfigSNBot\n"
        "📢 @ConfigSN_free"
    )

    try:
        await bot.send_message(chat_id=CHANNEL_ID, text=text, parse_mode="Markdown")
        configs_sent_today += 1
        print(f"✅ کانفیگ رایگان ارسال شد. امروز: {configs_sent_today}")
    except Exception as e:
        print(f"❌ خطا در ارسال کانفیگ: {e}")


async def reset_daily_counter():
    global configs_sent_today
    configs_sent_today = 0
    await delete_old_configs()
    print("✅ شمارنده ریست و کانفیگ‌های قدیمی حذف شدن.")
