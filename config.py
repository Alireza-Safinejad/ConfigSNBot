from dotenv import load_dotenv
import os

load_dotenv()

# تنظیمات ربات
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
CHANNEL_ID = os.getenv("CHANNEL_ID")

# تنظیمات Marzban
MARZBAN_URL = os.getenv("MARZBAN_URL")
MARZBAN_USERNAME = os.getenv("MARZBAN_USERNAME")
MARZBAN_PASSWORD = os.getenv("MARZBAN_PASSWORD")

# کلید API سایت Plisio
PLISIO_SECRET_KEY = os.getenv("PLISIO_SECRET_KEY")

# آدرس کیف پول
USDT_WALLET = os.getenv("USDT_WALLET")

# پلن‌های زمانی (نامحدود)
TIME_PLANS = {
    "1h":   {"label": "⏱ ۱ ساعته",   "hours": 1,    "price": 0.5},
    "1d":   {"label": "📅 ۱ روزه",    "hours": 24,   "price": 1.0},
    "1w":   {"label": "📅 ۱ هفته",    "hours": 168,  "price": 4.0},
    "15d":  {"label": "📅 ۱۵ روزه",   "hours": 360,  "price": 7.0},
    "30d":  {"label": "📅 ۱ ماهه",    "hours": 720,  "price": 12.0},
    "60d":  {"label": "📅 ۲ ماهه",    "hours": 1440, "price": 20.0},
    "90d":  {"label": "📅 ۳ ماهه",    "hours": 2160, "price": 27.0},
    "120d": {"label": "📅 ۴ ماهه",    "hours": 2880, "price": 33.0},
}

# پلن‌های حجمی
DATA_PLANS = {
    "1gb":   {"label": "📦 ۱ گیگ",    "gb": 1,   "price": 1.0},
    "5gb":   {"label": "📦 ۵ گیگ",    "gb": 5,   "price": 4.0},
    "10gb":  {"label": "📦 ۱۰ گیگ",   "gb": 10,  "price": 7.0},
    "20gb":  {"label": "📦 ۲۰ گیگ",   "gb": 20,  "price": 12.0},
    "50gb":  {"label": "📦 ۵۰ گیگ",   "gb": 50,  "price": 25.0},
    "100gb": {"label": "📦 ۱۰۰ گیگ",  "gb": 100, "price": 45.0},
    "150gb": {"label": "📦 ۱۵۰ گیگ",  "gb": 150, "price": 60.0},
    "200gb": {"label": "📦 ۲۰۰ گیگ",  "gb": 200, "price": 75.0},
}

# زمان‌بندی ارسال کانفیگ رایگان (ساعت)
FREE_CONFIG_SCHEDULE = [8, 12, 16, 20, 23]

# مشخصات کانفیگ رایگان
FREE_CONFIG_HOURS = 24
FREE_CONFIG_GB = 1
