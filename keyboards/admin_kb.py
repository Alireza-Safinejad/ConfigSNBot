from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton


def admin_menu_kb():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📊 آمار کلی"), KeyboardButton(text="👥 لیست کاربران")],
            [KeyboardButton(text="📢 پیام همگانی"), KeyboardButton(text="💰 گزارش درآمد")],
            [KeyboardButton(text="🔄 ارسال کانفیگ رایگان"), KeyboardButton(text="⚙️ تنظیمات")],
            [KeyboardButton(text="🔙 خروج از پنل ادمین")],
        ],
        resize_keyboard=True
    )
    return keyboard


def back_to_admin_kb():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 بازگشت به پنل ادمین", callback_data="admin_back")],
    ])
    return keyboard


def confirm_broadcast_kb():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ تأیید و ارسال", callback_data="confirm_broadcast")],
        [InlineKeyboardButton(text="❌ انصراف", callback_data="cancel_broadcast")],
    ])
    return keyboard
