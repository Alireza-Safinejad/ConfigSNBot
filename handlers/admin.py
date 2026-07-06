from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import ADMIN_ID, TIME_PLANS, DATA_PLANS
from database.db import (
    get_all_users_count, get_active_users_count,
    get_monthly_revenue, get_today_sales, get_configs_count
)
from keyboards.admin_kb import admin_menu_kb, confirm_broadcast_kb, back_to_admin_kb
from keyboards.user_kb import main_menu_kb

router = Router()


class BroadcastState(StatesGroup):
    waiting_for_message = State()
    confirm = State()


class SettingsState(StatesGroup):
    waiting = State()


def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID


@router.message(Command("admin"))
async def admin_panel(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("دسترسی ندارید.")
        return
    await message.answer("پنل مدیریت", reply_markup=admin_menu_kb())


@router.message(F.text == "🔙 خروج از پنل ادمین")
async def exit_admin(message: Message):
    if not is_admin(message.from_user.id):
        return
    await message.answer("از پنل ادمین خارج شدی.", reply_markup=main_menu_kb())


@router.message(F.text == "📊 آمار کلی")
async def stats(message: Message):
    if not is_admin(message.from_user.id):
        return
    total = await get_all_users_count()
    active = await get_active_users_count()
    revenue = await get_monthly_revenue()
    today = await get_today_sales()
    configs = await get_configs_count()

    await message.answer(
        f"آمار سیستم\n\n"
        f"کل کاربران: {total}\n"
        f"کاربران فعال: {active}\n"
        f"درآمد این ماه: ${revenue:.2f}\n"
        f"فروش امروز: {today}\n"
        f"کانفیگ‌های موجود: {configs}"
    )


@router.message(F.text == "💰 گزارش درآمد")
async def revenue_report(message: Message):
    if not is_admin(message.from_user.id):
        return
    monthly = await get_monthly_revenue()
    today = await get_today_sales()
    await message.answer(
        f"گزارش درآمد\n\n"
        f"درآمد این ماه: ${monthly:.2f}\n"
        f"فروش امروز: {today} کانفیگ"
    )


@router.message(F.text == "📢 پیام همگانی")
async def broadcast_start(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await message.answer("متن پیام همگانی رو بنویس:")
    await state.set_state(BroadcastState.waiting_for_message)


@router.message(BroadcastState.waiting_for_message)
async def broadcast_preview(message: Message, state: FSMContext):
    await state.update_data(broadcast_text=message.text)
    await message.answer(
        f"پیش‌نمایش:\n\n{message.text}\n\nارسال شود؟",
        reply_markup=confirm_broadcast_kb()
    )
    await state.set_state(BroadcastState.confirm)


@router.callback_query(F.data == "confirm_broadcast")
async def do_broadcast(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
    data = await state.get_data()
    text = data.get("broadcast_text", "")

    import aiosqlite, os
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
    await callback.message.edit_text(f"پیام ارسال شد.\nموفق: {sent}\nناموفق: {failed}")


@router.callback_query(F.data == "cancel_broadcast")
async def cancel_broadcast(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("ارسال لغو شد.")


@router.message(F.text == "🔄 ارسال کانفیگ رایگان")
async def manual_free_config(message: Message):
    if not is_admin(message.from_user.id):
        return
    from scheduler.daily_config import send_free_config
    await send_free_config(message.bot)
    await message.answer("کانفیگ رایگان به کانال ارسال شد.")


@router.message(F.text == "🔃 جمع‌آوری کانفیگ")
async def manual_collect(message: Message):
    if not is_admin(message.from_user.id):
        return
    from scheduler.daily_config import collect_configs_from_channels
    await collect_configs_from_channels(message.bot)
    count = await get_configs_count()
    await message.answer(f"جمع‌آوری انجام شد.\nکانفیگ‌های موجود: {count}")


@router.message(F.text == "⚙️ تنظیمات")
async def settings_menu(message: Message):
    if not is_admin(message.from_user.id):
        return

    from scheduler.daily_config import MAX_CONFIGS_PER_DAY, configs_sent_today

    await message.answer(
        f"تنظیمات فعلی ربات\n\n"
        f"حداکثر کانفیگ روزانه: {MAX_CONFIGS_PER_DAY}\n"
        f"ارسال شده امروز: {configs_sent_today}\n\n"
        f"کانال‌های منبع:\n"
        f"@mitivpn\n"
        f"@irantweety\n"
        f"@drmobileiir\n\n"
        f"ساعت‌های ارسال: ۸، ۱۲، ۱۶، ۲۰، ۲۳\n\n"
        f"پلن‌های زمانی: {len(TIME_PLANS)} پلن\n"
        f"پلن‌های حجمی: {len(DATA_PLANS)} پلن",
        reply_markup=back_to_admin_kb()
    )


@router.callback_query(F.data == "admin_back")
async def admin_back(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    await callback.message.edit_text("پنل مدیریت")
