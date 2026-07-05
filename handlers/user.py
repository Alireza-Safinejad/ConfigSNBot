import uuid
from datetime import datetime, timedelta
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart

from config import TIME_PLANS, DATA_PLANS, ADMIN_ID
from database.db import (
    add_user, get_user, get_active_purchase, get_purchase_history,
    add_payment, add_purchase, get_payment, update_payment_status,
    add_referral, get_referral_count, add_referral_pending,
    get_referral_pending, update_referral_pending, complete_referral_pending
)
from keyboards.user_kb import (
    main_menu_kb, plan_type_kb, time_plans_kb, data_plans_kb,
    payment_method_kb, confirm_payment_kb, my_account_kb
)
from services.plisio import plisio
from scheduler.daily_config import get_next_config, collect_configs_from_channels

router = Router()
BOT_USERNAME = "ConfigSNBot"


async def deliver_config(bot, telegram_id: int, plan_type: str, plan_key: str,
                         price_usd: float, payment_id: str):
    if plan_type == "time":
        plan = TIME_PLANS.get(plan_key, {})
        plan_label = plan.get("label", plan_key)
        hours = plan.get("hours", 720)
        expire_info = f"مدت: {plan_label}"
    else:
        plan = DATA_PLANS.get(plan_key, {})
        plan_label = plan.get("label", plan_key)
        hours = 720
        expire_info = f"حجم: {plan.get('gb', 0)} گیگ — مدت ۳۰ روز"

    config_link = await get_next_config()

    if not config_link:
        await bot.send_message(
            telegram_id,
            "⏳ در حال آماده‌سازی کانفیگ...\n\n"
            "کانفیگ شما در کمتر از ۱ ساعت ارسال میشه.\n"
            "سوال داری؟ @ConfigSNB"
        )
        return False

    expires_at = datetime.now() + timedelta(hours=hours)

    await add_purchase(
        telegram_id, plan_type, plan_key, price_usd,
        "external", config_link, payment_id,
        expires_at.strftime("%Y-%m-%d %H:%M:%S")
    )

    text = (
        f"✅ کانفیگ VIP شما آماده است!\n\n"
        f"📦 پلن: {plan_label}\n"
        f"📅 {expire_info}\n\n"
        f"🔗 لینک کانفیگ:\n{config_link}\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"📱 راهنمای نصب:\n"
        f"اندروید: V2rayNG\n"
        f"iOS: Streisand\n"
        f"ویندوز: V2rayN\n\n"
        f"لینک بالا رو کپی کن و داخل نرم‌افزار Import کن.\n"
        f"━━━━━━━━━━━━━━━\n"
        f"مشکل داری؟ @ConfigSNB"
    )

    await bot.send_message(telegram_id, text)
    return True


@router.message(CommandStart())
async def cmd_start(message: Message):
    args = message.text.split()
    referred_by = None

    if len(args) > 1 and args[1].startswith("ref_"):
        try:
            referred_by = int(args[1].replace("ref_", ""))
            if referred_by == message.from_user.id:
                referred_by = None
        except:
            referred_by = None

    user = await get_user(message.from_user.id)
    await add_user(
        message.from_user.id,
        message.from_user.username or "",
        message.from_user.full_name or "",
        referred_by
    )

    if referred_by and not user:
        await add_referral(referred_by, message.from_user.id)
        pending = await get_referral_pending(referred_by)
        if pending:
            current_refs = pending[5] + 1
            required_refs = pending[4]
            await update_referral_pending(referred_by, current_refs)

            if current_refs >= required_refs:
                await complete_referral_pending(referred_by)
                plan_type = pending[2]
                plan_key = pending[3]
                success = await deliver_config(
                    message.bot, referred_by, plan_type, plan_key, 0, f"ref_{referred_by}"
                )
                if success:
                    await message.bot.send_message(
                        referred_by,
                        f"🎉 تبریک! {required_refs} نفر عضو شدن و کانفیگت ارسال شد!"
                    )
            else:
                remaining = required_refs - current_refs
                await message.bot.send_message(
                    referred_by,
                    f"یه نفر با لینک تو عضو شد!\n"
                    f"{current_refs} نفر از {required_refs} نفر\n"
                    f"{remaining} نفر دیگه تا دریافت کانفیگ"
                )

    await message.answer(
        f"سلام {message.from_user.first_name}!\n\n"
        "به ربات ConfigSN خوش اومدی.\n\n"
        "کانفیگ‌های VIP ما:\n"
        "سرعت بالا و پایدار\n"
        "مناسب برای قطعی‌های اینترنت\n"
        "پشتیبانی ۲۴ ساعته\n\n"
        "از منوی زیر انتخاب کن:",
        reply_markup=main_menu_kb()
    )


@router.message(F.text == "📦 خرید کانفیگ VIP")
async def buy_config(message: Message):
    await message.answer(
        "💎 کانفیگ‌های VIP ConfigSN\n\n"
        "چرا VIP بخری؟\n"
        "سرعت بالاتر از کانفیگ رایگان\n"
        "پایدار حتی در قطعی‌های اینترنت\n"
        "پشتیبانی مستقیم\n\n"
        "نوع پلن رو انتخاب کن:",
        reply_markup=plan_type_kb()
    )


@router.callback_query(F.data == "plantype_time")
async def show_time_plans(callback: CallbackQuery):
    await callback.message.edit_text(
        "پلن‌های نامحدود (بر اساس زمان)\n\nپلن مورد نظرت رو انتخاب کن:",
        reply_markup=time_plans_kb()
    )


@router.callback_query(F.data == "plantype_data")
async def show_data_plans(callback: CallbackQuery):
    await callback.message.edit_text(
        "پلن‌های محدود (بر اساس حجم)\n\nپلن مورد نظرت رو انتخاب کن:",
        reply_markup=data_plans_kb()
    )


@router.callback_query(F.data.startswith("timeplan_"))
async def select_time_plan(callback: CallbackQuery):
    plan_key = callback.data.replace("timeplan_", "")
    plan = TIME_PLANS.get(plan_key)
    if not plan:
        await callback.answer("پلن یافت نشد!", show_alert=True)
        return
    refs = plan["refs"]
    await callback.message.edit_text(
        f"پلن انتخابی: {plan['label']}\n\n"
        f"قیمت: {plan['price']} تتر (USDT)\n"
        f"یا دعوت {refs} نفر از دوستان\n\n"
        "روش پرداخت رو انتخاب کن:",
        reply_markup=payment_method_kb("time", plan_key, refs)
    )


@router.callback_query(F.data.startswith("dataplan_"))
async def select_data_plan(callback: CallbackQuery):
    plan_key = callback.data.replace("dataplan_", "")
    plan = DATA_PLANS.get(plan_key)
    if not plan:
        await callback.answer("پلن یافت نشد!", show_alert=True)
        return
    refs = plan["refs"]
    await callback.message.edit_text(
        f"پلن انتخابی: {plan['label']}\n\n"
        f"قیمت: {plan['price']} تتر (USDT)\n"
        f"یا دعوت {refs} نفر از دوستان\n\n"
        "روش پرداخت رو انتخاب کن:",
        reply_markup=payment_method_kb("data", plan_key, refs)
    )


@router.callback_query(F.data.startswith("pay_usdt_"))
async def pay_with_usdt(callback: CallbackQuery):
    parts = callback.data.replace("pay_usdt_", "").split("_", 1)
    plan_type = parts[0]
    plan_key = parts[1] if len(parts) > 1 else ""
    plan = TIME_PLANS.get(plan_key) or DATA_PLANS.get(plan_key)
    if not plan:
        await callback.answer("خطا!", show_alert=True)
        return

    order_id = f"{callback.from_user.id}_{str(uuid.uuid4())[:8]}"
    invoice_data = await plisio.create_invoice(plan["price"], order_id, f"VPN - {plan['label']}")

    if invoice_data.get("status") != "success":
        await callback.message.edit_text(
            "خطا در ایجاد پرداخت. دوباره تلاش کن یا با پشتیبانی تماس بگیر.\n@ConfigSNB"
        )
        return

    data = invoice_data.get("data", {})
    invoice_id = data.get("txn_id", "")
    invoice_url = data.get("invoice_url", "")

    await add_payment(callback.from_user.id, invoice_id, plan["price"], plan_type, plan_key)

    await callback.message.edit_text(
        f"پرداخت پلن {plan['label']}\n\n"
        f"مبلغ: {plan['price']} تتر (USDT TRC20)\n\n"
        f"لینک پرداخت:\n{invoice_url}\n\n"
        "بعد از پرداخت دکمه زیر رو بزن:",
        reply_markup=confirm_payment_kb(invoice_id)
    )


@router.callback_query(F.data.startswith("pay_ref_"))
async def pay_with_referral(callback: CallbackQuery):
    parts = callback.data.replace("pay_ref_", "").split("_", 1)
    plan_type = parts[0]
    plan_key = parts[1] if len(parts) > 1 else ""
    plan = TIME_PLANS.get(plan_key) or DATA_PLANS.get(plan_key)
    if not plan:
        await callback.answer("خطا!", show_alert=True)
        return

    refs = plan["refs"]
    user_id = callback.from_user.id
    ref_link = f"https://t.me/{BOT_USERNAME}?start=ref_{user_id}"

    await add_referral_pending(user_id, plan_type, plan_key, refs)

    await callback.message.edit_text(
        f"دعوت از دوستان برای {plan['label']}\n\n"
        f"تعداد مورد نیاز: {refs} نفر\n\n"
        f"لینک اختصاصی تو:\n{ref_link}\n\n"
        "این لینک رو برای دوستات بفرست.\n"
        "هر وقت تعداد لازم عضو شدن، کانفیگت خودکار ارسال میشه!"
    )


@router.callback_query(F.data.startswith("checkpay_"))
async def check_payment(callback: CallbackQuery):
    invoice_id = callback.data.replace("checkpay_", "")
    await callback.answer("در حال بررسی پرداخت...")

    is_paid = await plisio.is_payment_completed(invoice_id)

    if not is_paid:
        await callback.message.edit_text(
            "پرداخت هنوز تأیید نشده.\n\n"
            "چند دقیقه صبر کن و دوباره امتحان کن.",
            reply_markup=confirm_payment_kb(invoice_id)
        )
        return

    payment = await get_payment(invoice_id)
    if not payment:
        await callback.message.edit_text("اطلاعات پرداخت یافت نشد.")
        return

    await update_payment_status(invoice_id, "completed")
    await callback.message.edit_text("پرداخت تأیید شد! در حال آماده‌سازی کانفیگ...")

    await deliver_config(
        callback.bot, callback.from_user.id,
        payment[4], payment[5], payment[3], invoice_id
    )


@router.callback_query(F.data == "cancel_payment")
async def cancel_payment(callback: CallbackQuery):
    await callback.message.edit_text("پرداخت لغو شد.")


@router.message(F.text == "👤 حساب کاربری")
async def my_account(message: Message):
    purchase = await get_active_purchase(message.from_user.id)

    if not purchase:
        await message.answer("شما هنوز اکانت فعالی ندارید.", reply_markup=my_account_kb(False))
        return

    plan_key = purchase[3]
    expires_at = purchase[10]
    config_link = purchase[6]

    plan_label = (TIME_PLANS.get(plan_key) or DATA_PLANS.get(plan_key, {})).get("label", plan_key)
    expire_date = datetime.strptime(expires_at, "%Y-%m-%d %H:%M:%S")
    days_left = (expire_date - datetime.now()).days
    expire_str = expire_date.strftime("%Y/%m/%d")

    ref_count = await get_referral_count(message.from_user.id)
    ref_link = f"https://t.me/{BOT_USERNAME}?start=ref_{message.from_user.id}"

    await message.answer(
        f"حساب کاربری من\n\n"
        f"پلن: {plan_label}\n"
        f"وضعیت: فعال\n"
        f"انقضا: {expire_str} ({days_left} روز مانده)\n\n"
        f"تعداد دعوت شده‌ها: {ref_count} نفر\n"
        f"لینک دعوت من:\n{ref_link}",
        reply_markup=my_account_kb(True)
    )


@router.callback_query(F.data == "get_config")
async def get_config_again(callback: CallbackQuery):
    purchase = await get_active_purchase(callback.from_user.id)
    if not purchase:
        await callback.answer("اکانت فعالی ندارید!", show_alert=True)
        return
    config_link = purchase[6]
    await callback.message.answer(
        f"لینک کانفیگ VIP شما:\n\n{config_link}\n\n"
        "این لینک رو کپی کن و داخل V2rayNG یا Streisand یا V2rayN وارد کن."
    )


@router.callback_query(F.data == "purchase_history")
async def purchase_history(callback: CallbackQuery):
    purchases = await get_purchase_history(callback.from_user.id)
    if not purchases:
        await callback.answer("تاریخچه‌ای وجود ندارد.", show_alert=True)
        return
    text = "تاریخچه خریدها:\n\n"
    for p in purchases:
        plan_key = p[3]
        status = p[9]
        created = p[10]
        plan_label = (TIME_PLANS.get(plan_key) or DATA_PLANS.get(plan_key, {})).get("label", plan_key)
        status_emoji = "🟢" if status == "active" else "⚫"
        text += f"{status_emoji} {plan_label} — {created[:10]}\n"
    await callback.message.answer(text)


@router.callback_query(F.data == "renew_account")
async def renew_account(callback: CallbackQuery):
    await callback.message.answer("برای تمدید، یه پلن جدید انتخاب کن:", reply_markup=plan_type_kb())


@router.callback_query(F.data == "new_plan")
async def new_plan(callback: CallbackQuery):
    await callback.message.answer("نوع پلن رو انتخاب کن:", reply_markup=plan_type_kb())


@router.callback_query(F.data == "buy_config")
async def buy_config_cb(callback: CallbackQuery):
    await callback.message.answer("نوع پلن رو انتخاب کن:", reply_markup=plan_type_kb())


@router.callback_query(F.data == "back_main")
async def back_main(callback: CallbackQuery):
    await callback.message.edit_text("از منوی زیر انتخاب کن:")


@router.callback_query(F.data == "back_plantype")
async def back_plantype(callback: CallbackQuery):
    await callback.message.edit_text("نوع پلن رو انتخاب کن:", reply_markup=plan_type_kb())


@router.message(F.text == "🎁 کانفیگ رایگان")
async def free_config(message: Message):
    await message.answer(
        "کانفیگ رایگان هر روز چندین بار در کانال ما ارسال میشه.\n\n"
        "عضو کانال بشو:\n@ConfigSN_free\n\n"
        "برای کانفیگ VIP پایدار:\nروی خرید کانفیگ VIP بزن"
    )


@router.message(F.text == "📞 پشتیبانی")
async def support(message: Message):
    await message.answer("پشتیبانی:\n\n@ConfigSNB\n\nساعات پاسخگویی: ۹ صبح تا ۱۲ شب")


@router.message(F.text == "📢 کانال ما")
async def our_channel(message: Message):
    await message.answer("کانال ما:\n\n@ConfigSN_free")


@router.message(F.text == "❓ راهنما")
async def help_msg(message: Message):
    await message.answer(
        "راهنمای استفاده:\n\n"
        "1. روی خرید کانفیگ VIP بزن\n"
        "2. نوع پلن رو انتخاب کن\n"
        "3. روش پرداخت رو انتخاب کن:\n"
        "   پرداخت با تتر\n"
        "   دعوت دوستان (رایگان)\n"
        "4. کانفیگ رو دریافت کن\n\n"
        "نرم‌افزارهای پیشنهادی:\n"
        "اندروید: V2rayNG\n"
        "iOS: Streisand\n"
        "ویندوز: V2rayN"
    )
