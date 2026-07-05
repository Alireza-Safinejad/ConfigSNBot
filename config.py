from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
CHANNEL_ID = os.getenv("CHANNEL_ID")
MARZBAN_URL = os.getenv("MARZBAN_URL")
MARZBAN_USERNAME = os.getenv("MARZBAN_USERNAME")
MARZBAN_PASSWORD = os.getenv("MARZBAN_PASSWORD")
PLISIO_SECRET_KEY = os.getenv("PLISIO_SECRET_KEY")
USDT_WALLET = os.getenv("USDT_WALLET")

# پلن‌های زمانی با تعداد دعوت مورد نیاز
TIME_PLANS = {
    "1h":   {"label": "⏱ ۱ ساعته",  "hours": 1,    "price": 0.5,  "refs": 1},
    "1d":   {"label": "📅 ۱ روزه",   "hours": 24,   "price": 1.0,  "refs": 1},
    "1w":   {"label": "📅 ۱ هفته",   "hours": 168,  "price": 4.0,  "refs": 4},
    "15d":  {"label": "📅 ۱۵ روزه",  "hours": 360,  "price": 7.0,  "refs": 7},
    "30d":  {"label": "📅 ۱ ماهه",   "hours": 720,  "price": 12.0, "refs": 12},
    "60d":  {"label": "📅 ۲ ماهه",   "hours": 1440, "price": 20.0, "refs": 20},
    "90d":  {"label": "📅 ۳ ماهه",   "hours": 2160, "price": 27.0, "refs": 27},
    "120d": {"label": "📅 ۴ ماهه",   "hours": 2880, "price": 33.0, "refs": 33},
}

# پلن‌های حجمی با تعداد دعوت مورد نیاز
DATA_PLANS = {
    "1gb":   {"label": "📦 ۱ گیگ",   "gb": 1,   "price": 1.0,  "refs": 1},
    "5gb":   {"label": "📦 ۵ گیگ",   "gb": 5,   "price": 4.0,  "refs": 5},
    "10gb":  {"label": "📦 ۱۰ گیگ",  "gb": 10,  "price": 7.0,  "refs": 10},
    "20gb":  {"label": "📦 ۲۰ گیگ",  "gb": 20,  "price": 12.0, "refs": 20},
    "50gb":  {"label": "📦 ۵۰ گیگ",  "gb": 50,  "price": 25.0, "refs": 50},
    "100gb": {"label": "📦 ۱۰۰ گیگ", "gb": 100, "price": 45.0, "refs": 100},
    "150gb": {"label": "📦 ۱۵۰ گیگ", "gb": 150, "price": 60.0, "refs": 150},
    "200gb": {"label": "📦 ۲۰۰ گیگ", "gb": 200, "price": 75.0, "refs": 200},
}

FREE_CONFIG_SCHEDULE = [8, 12, 16, 20, 23]
FREE_CONFIG_HOURS = 24
FREE_CONFIG_GB = 1
