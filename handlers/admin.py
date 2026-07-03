from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import ADMIN_ID
from database.db import (
    get_all_users_count, get_active_users_count,
    get_monthly_revenue, get_today_sales
)
from keyboards.admin_kb import admin_menu_kb, confirm_broadcast_kb
from keyboards.user_kb import main_menu_kb

router = Router()


class BroadcastState(StatesGroup):
    waiting_for_message = State()
    confirm = State()


def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID


# ==================== ورود به پنل ادمین ====================

@router.message(Command("admin"))
async def admin_panel(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("❌ شما دسترسی ندارید.")
        return

    await message.answer(
        "👨‍💼 پنل مدیریت\n\nخوش اومدی ادمین!",
        reply_markup=admin_menu_kb()
    )


@router.message(F.text == "🔙 خروج از پنل ادمین")
async def exit_admin(message: Message):
    if not is_admin(message.from_user.id):
        return
    await message.answer(
        "از پنل ادمین خارج شدی.",
        reply_markup=main_menu_kb()
    )


# ==================== آمار کلی ====================

@router.message(F.text == "📊 آمار کلی")
async def stats(message: Message):
    if not is_admin(message.from_user.id):
        return

    total_users = await get_all_users_count()
    active_users = await get_active_users_count()
    monthly_revenue = await get_monthly_revenue()
    today_sales = await get_today_sales()

    await message.answer(
        f"📊 آمار سیستم\n\n"
        f"👥 کل کاربران: {total_users}\n"
        f"🟢 کاربران فعال: {active_users}\n"
        f"💰 درآمد این ماه: ${monthly_revenue:.2f}\n"
        f"📦 فروش امروز: {today_sales} کانفیگ"
    )


# ==================== گزارش درآمد ====================

@router.message(F.text == "💰 گزارش درآمد")
async def revenue_report(message: Message):
    if not is_admin(message.from_user.id):
        return

    monthly = await get_monthly_revenue()
    today = await get_today_sales()

    await message.answer(
        f"💰 گزارش درآمد\n\n"
        f"📅 درآمد این ماه: ${monthly:.2f}\n"
        f"📦 فروش امروز: {today} کانفیگ"
    )


# ==================== پیام همگانی ====================

@router.message(F.text == "📢 پیام همگانی")
async def broadcast_start(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return

    await message.answer("✍️ متن پیام همگانی رو بنویس:")
    await state.set_state(BroadcastState.waiting_for_message)


@router.message(BroadcastState.waiting_for_message)
async def broadcast_preview(message: Message, state: FSMContext):
    await state.update_data(broadcast_text=message.text)
    await message.answer(
        f"📢 پیش‌نمایش پیام:\n\n{message.text}\n\n"
        "آیا ارسال شود؟",
        reply_markup=confirm_broadcast_kb()
    )
    await state.set_state(BroadcastState.confirm)


@router.callback_query(F.data == "confirm_broadcast")
async def do_broadcast(callback: CallbackQuery, state: FSMContext, bot=None):
    if not is_admin(callback.from_user.id):
        return

    data = await state.get_data()
    text = data.get("broadcast_text", "")

    import aiosqlite
    import os
    DB_PATH = os.path.join(os.path.dirname(__file__), "../database/bot.db")

    sent = 0
    failed = 0

    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT telegram_id FROM users") as cursor:
            users = await cursor.fetchall()

    for user in users:
        try:
            await callback.bot.send_message(user[0], text)
            sent += 1
        except Exception:
            failed += 1

    await state.clear()
    await callback.message.edit_text(
        f"✅ پیام همگانی ارسال شد.\n\n"
        f"✅ موفق: {sent}\n"
        f"❌ ناموفق: {failed}"
    )


@router.callback_query(F.data == "cancel_broadcast")
async def cancel_broadcast(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ ارسال همگانی لغو شد.")


# ==================== ارسال دستی کانفیگ رایگان ====================

@router.message(F.text == "🔄 ارسال کانفیگ رایگان")
async def manual_free_config(message: Message):
    if not is_admin(message.from_user.id):
        return

    from scheduler.daily_config import send_free_config
    await send_free_config(message.bot)
    await message.answer("✅ کانفیگ رایگان به کانال ارسال شد.")
