from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from config import TIME_PLANS, DATA_PLANS


def main_menu_kb():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📦 خرید کانفیگ"), KeyboardButton(text="🎁 کانفیگ رایگان")],
            [KeyboardButton(text="👤 حساب کاربری"), KeyboardButton(text="📞 پشتیبانی")],
            [KeyboardButton(text="📢 کانال ما"), KeyboardButton(text="❓ راهنما")],
        ],
        resize_keyboard=True
    )
    return keyboard


def plan_type_kb():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⏱ نامحدود (بر اساس زمان)", callback_data="plantype_time")],
        [InlineKeyboardButton(text="📊 محدود (بر اساس حجم)", callback_data="plantype_data")],
        [InlineKeyboardButton(text="🔙 بازگشت", callback_data="back_main")],
    ])
    return keyboard


def time_plans_kb():
    buttons = []
    for key, plan in TIME_PLANS.items():
        buttons.append([
            InlineKeyboardButton(
                text=f"{plan['label']} — ${plan['price']}",
                callback_data=f"timeplan_{key}"
            )
        ])
    buttons.append([InlineKeyboardButton(text="🔙 بازگشت", callback_data="back_plantype")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def data_plans_kb():
    buttons = []
    for key, plan in DATA_PLANS.items():
        buttons.append([
            InlineKeyboardButton(
                text=f"{plan['label']} — ${plan['price']}",
                callback_data=f"dataplan_{key}"
            )
        ])
    buttons.append([InlineKeyboardButton(text="🔙 بازگشت", callback_data="back_plantype")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def confirm_payment_kb(payment_id: str):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ پرداخت کردم", callback_data=f"checkpay_{payment_id}")],
        [InlineKeyboardButton(text="❌ انصراف", callback_data="cancel_payment")],
    ])
    return keyboard


def my_account_kb(has_active: bool):
    if has_active:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔗 دریافت مجدد کانفیگ", callback_data="get_config")],
            [InlineKeyboardButton(text="🔄 تمدید اکانت", callback_data="renew_account")],
            [InlineKeyboardButton(text="➕ خرید پلن جدید", callback_data="new_plan")],
            [InlineKeyboardButton(text="📋 تاریخچه خریدها", callback_data="purchase_history")],
        ])
    else:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📦 خرید کانفیگ", callback_data="buy_config")],
        ])
    return keyboard
