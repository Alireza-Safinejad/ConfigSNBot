from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton


def admin_menu_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📊 آمار کلی"), KeyboardButton(text="💰 گزارش درآمد")],
            [KeyboardButton(text="📢 پیام همگانی"), KeyboardButton(text="🔄 ارسال کانفیگ رایگان")],
            [KeyboardButton(text="🔃 جمع‌آوری کانفیگ"), KeyboardButton(text="⚙️ تنظیمات")],
            [KeyboardButton(text="🔙 خروج از پنل ادمین")],
        ],
        resize_keyboard=True
    )


def back_to_admin_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 بازگشت", callback_data="admin_back")],
    ])


def confirm_broadcast_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ تأیید و ارسال", callback_data="confirm_broadcast")],
        [InlineKeyboardButton(text="❌ انصراف", callback_data="cancel_broadcast")],
    ])
