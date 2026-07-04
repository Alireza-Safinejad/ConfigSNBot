import re
import asyncio
import aiohttp
from aiogram import Bot
from aiogram.enums import ParseMode
from config import CHANNEL_ID

# کانال‌های منبع کانفیگ رایگان
SOURCE_CHANNELS = [
    "mitivpn",
    "irantweety",
    "drmobileiir"
]

# حداکثر کانفیگ در روز
MAX_CONFIGS_PER_DAY = 20

# ذخیره کانفیگ‌های جمع‌آوری شده
collected_configs = []
configs_sent_today = 0


def extract_configs(text: str) -> list:
    patterns = [
        r'vless://[^\s\n]+',
        r'vmess://[^\s\n]+',
        r'trojan://[^\s\n]+',
        r'ss://[^\s\n]+',
        r'hy2://[^\s\n]+',
        r'hysteria2://[^\s\n]+',
    ]
    configs = []
    for pattern in patterns:
        found = re.findall(pattern, text)
        configs.extend(found)
    return configs


async def collect_configs_from_channels(bot: Bot):
    global collected_configs
    new_configs = []

    for channel in SOURCE_CHANNELS:
        try:
            # استفاده از API عمومی تلگرام برای خواندن کانال
            url = f"https://t.me/s/{channel}"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status == 200:
                        html = await resp.text()
                        configs = extract_configs(html)
                        new_configs.extend(configs)
                        print(f"✅ {len(configs)} کانفیگ از {channel} دریافت شد.")
        except Exception as e:
            print(f"❌ خطا در دریافت از {channel}: {e}")

    for config in new_configs:
        if config not in collected_configs:
            collected_configs.append(config)

    print(f"✅ {len(new_configs)} کانفیگ جدید. کل: {len(collected_configs)}")


async def send_free_config(bot: Bot):
    global collected_configs, configs_sent_today

    if configs_sent_today >= MAX_CONFIGS_PER_DAY:
        print("⚠️ حداکثر کانفیگ روزانه ارسال شده.")
        return

    if not collected_configs:
        await collect_configs_from_channels(bot)
        if not collected_configs:
            print("⚠️ کانفیگی برای ارسال وجود ندارد.")
            return

    config_link = collected_configs.pop(0)

    text = (
        "🎁 کانفیگ رایگان\n\n"
        "⏰ مدت: ۲۴ ساعت\n"
        "📊 حجم: محدود\n\n"
        f"`{config_link}`\n\n"
        "لینک رو کپی کن و داخل V2rayNG یا Streisand یا V2rayN وارد کن.\n\n"
        "━━━━━━━━━━━━━━━\n"
        "💎 برای کانفیگ VIP با سرعت بالا:\n"
        "👉 @ConfigSNBot\n"
        "📢 کانال ما: @ConfigSN_free"
    )

    try:
        await bot.send_message(
            chat_id=CHANNEL_ID,
            text=text,
            parse_mode=ParseMode.MARKDOWN
        )
        configs_sent_today += 1
        print(f"✅ کانفیگ ارسال شد. تعداد امروز: {configs_sent_today}")
    except Exception as e:
        print(f"❌ خطا در ارسال کانفیگ: {e}")


async def reset_daily_counter():
    global configs_sent_today
    configs_sent_today = 0
    print("✅ شمارنده روزانه ریست شد.")
