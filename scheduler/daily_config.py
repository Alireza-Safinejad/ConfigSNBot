import re
import asyncio
from aiogram import Bot
from aiogram.enums import ParseMode
from config import CHANNEL_ID

# کانال‌های منبع کانفیگ رایگان
SOURCE_CHANNELS = [
    "@mitivpn",
    "@irantweety", 
    "@drmobileiir"
]

# حداکثر کانفیگ در روز
MAX_CONFIGS_PER_DAY = 20

# ساعت‌های ارسال
SEND_HOURS = [8, 12, 16, 20, 23]

# ذخیره کانفیگ‌های جمع‌آوری شده
collected_configs = []
configs_sent_today = 0


def extract_configs(text: str) -> list:
    """استخراج لینک‌های کانفیگ از متن"""
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
    """جمع‌آوری کانفیگ از کانال‌های منبع"""
    global collected_configs
    new_configs = []

    for channel in SOURCE_CHANNELS:
        try:
            # دریافت آخرین پیام‌های کانال
            messages = await bot.get_chat(channel)
            # چک کردن آخرین پیام‌ها
            async for message in bot.get_updates():
                if hasattr(message, 'channel_post') and message.channel_post:
                    post = message.channel_post
                    if post.chat.username == channel.replace('@', ''):
                        if post.text:
                            configs = extract_configs(post.text)
                            new_configs.extend(configs)
        except Exception as e:
            print(f"❌ خطا در دریافت از {channel}: {e}")

    # اضافه کردن به لیست و حذف تکراری‌ها
    for config in new_configs:
        if config not in collected_configs:
            collected_configs.append(config)

    print(f"✅ {len(new_configs)} کانفیگ جدید جمع‌آوری شد. کل: {len(collected_configs)}")


async def send_free_config(bot: Bot):
    """ارسال یک کانفیگ رایگان به کانال"""
    global collected_configs, configs_sent_today

    if configs_sent_today >= MAX_CONFIGS_PER_DAY:
        print("⚠️ حداکثر کانفیگ روزانه ارسال شده.")
        return

    if not collected_configs:
        print("⚠️ کانفیگی برای ارسال وجود ندارد.")
        return

    # برداشتن اولین کانفیگ از لیست
    config_link = collected_configs.pop(0)

    text = (
        "🎁 کانفیگ رایگان\n\n"
        "⏰ مدت: ۲۴ ساعت\n"
        "📊 حجم: محدود\n\n"
        f"`{config_link}`\n\n"
        "لینک رو کپی کن و داخل V2rayNG یا Streisand یا V2rayN وارد کن.\n\n"
        "━━━━━━━━━━━━━━━\n"
        "💎 برای کانفیگ دائمی و با کیفیت:\n"
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
    """ریست کردن شمارنده روزانه"""
    global configs_sent_today
    configs_sent_today = 0
    print("✅ شمارنده روزانه ریست شد.")
