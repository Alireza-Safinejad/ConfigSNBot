import uuid
from datetime import datetime, timedelta
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart

from config import TIME_PLANS, DATA_PLANS, ADMIN_ID
from database.db import (
    add_user, get_active_purchase, get_purchase_history,
    add_payment, add_purchase, get_payment, update_payment_status
)
from keyboards.user_kb import (
    main_menu_kb, plan_type_kb, time_plans_kb,
    data_plans_kb, confirm_payment_kb, my_account_kb
)
from services.marzban import marzban
from services.plisio import plisio

router = Router()


# ==================== استارت ====================

@router.message(CommandStart())
async def cmd_start(message: Message):
    await add_user(
        message.from_user.id,
        message.from_user.username or "",
        message.from_user.full_name or ""
    )
    await message.answer(
        f"👋 سلام {message.from_user.first_name}!\n\n"
        "🤖 به ربات فروش کانفیگ VPN خوش اومدی.\n\n"
        "از منوی زیر انتخاب کن:",
        reply_markup=main_menu_kb()
    )


# ==================== خرید کانفیگ ====================

@router.message(F.text == "📦 خرید کانفیگ")
async def buy_config(message: Message):
    await message.answer(
        "نوع پلن رو انتخاب کن:",
        reply_markup=plan_type_kb()
    )


@router.callback_query(F.data == "plantype_time")
async def show_time_plans(callback: CallbackQuery):
    await callback.message.edit_text(
        "⏱ پلن‌های نامحدود (بر اساس زمان):\n\n"
        "حجم مصرفی نامحدوده و فقط زمان محدودیت داره.",
        reply_markup=time_plans_kb()
    )


@router.callback_query(F.data == "plantype_data")
async def show_data_plans(callback: CallbackQuery):
    await callback.message.edit_text(
        "📊 پلن‌های محدود (بر اساس حجم):\n\n"
        "مدت ۳۰ روزه — هر کدوم زودتر تموم شد منقضی میشه.",
        reply_markup=data_plans_kb()
    )


@router.callback_query(F.data.startswith("timeplan_"))
async def select_time_plan(callback: CallbackQuery):
    plan_key = callback.data.replace("timeplan_", "")
    plan = TIME_PLANS.get(plan_key)
    if not plan:
        await callback.answer("پلن یافت نشد!", show_alert=True)
        return

    order_id = f"{callback.from_user.id}_{str(uuid.uuid4())[:8]}"
    invoice_data = await plisio.create_invoice(
        plan["price"],
        order_id,
        f"VPN Config - {plan['label']}"
    )

    if invoice_data.get("status") != "success":
        await callback.message.edit_text(
            "❌ خطا در ایجاد پرداخت. لطفاً دوباره تلاش کن یا با پشتیبانی تماس بگیر."
        )
        return

    data = invoice_data.get("data", {})
    invoice_id = data.get("txn_id", "")
    pay_address = data.get("wallet_hash", "")
    pay_amount = data.get("invoice_sum", plan["price"])
    pay_currency = data.get("currency", "USDT_TRX")

    await add_payment(
        callback.from_user.id,
        invoice_id,
        plan["price"],
        "time",
        plan_key
    )

    await callback.message.edit_text(
        f"💳 پرداخت پلن {plan['label']}\n\n"
        f"💰 مبلغ: ${plan['price']}\n"
        f"🪙 مقدار: {pay_amount} {pay_currency}\n\n"
        f"📋 آدرس واریز:\n"
        f"`{pay_address}`\n\n"
        "⚠️ دقیقاً همین مقدار رو واریز کن.\n"
        "بعد از واریز دکمه زیر رو بزن:",
        reply_markup=confirm_payment_kb(invoice_id),
        parse_mode="Markdown"
    )


@router.callback_query(F.data.startswith("dataplan_"))
async def select_data_plan(callback: CallbackQuery):
    plan_key = callback.data.replace("dataplan_", "")
    plan = DATA_PLANS.get(plan_key)
    if not plan:
        await callback.answer("پلن یافت نشد!", show_alert=True)
        return

    order_id = f"{callback.from_user.id}_{str(uuid.uuid4())[:8]}"
    invoice_data = await plisio.create_invoice(
        plan["price"],
        order_id,
        f"VPN Config - {plan['label']}"
    )

    if invoice_data.get("status") != "success":
        await callback.message.edit_text(
            "❌ خطا در ایجاد پرداخت. لطفاً دوباره تلاش کن یا با پشتیبانی تماس بگیر."
        )
        return

    data = invoice_data.get("data", {})
    invoice_id = data.get("txn_id", "")
    pay_address = data.get("wallet_hash", "")
    pay_amount = data.get("invoice_sum", plan["price"])
    pay_currency = data.get("currency", "USDT_TRX")

    await add_payment(
        callback.from_user.id,
        invoice_id,
        plan["price"],
        "data",
        plan_key
    )

    await callback.message.edit_text(
        f"💳 پرداخت پلن {plan['label']}\n\n"
        f"💰 مبلغ: ${plan['price']}\n"
        f"🪙 مقدار: {pay_amount} {pay_currency}\n\n"
        f"📋 آدرس واریز:\n"
        f"`{pay_address}`\n\n"
        "⚠️ دقیقاً همین مقدار رو واریز کن.\n"
        "بعد از واریز دکمه زیر رو بزن:",
        reply_markup=confirm_payment_kb(invoice_id),
        parse_mode="Markdown"
    )


# ==================== تأیید پرداخت ====================

@router.callback_query(F.data.startswith("checkpay_"))
async def check_payment(callback: CallbackQuery):
    invoice_id = callback.data.replace("checkpay_", "")

    await callback.answer("در حال بررسی پرداخت...")

    is_paid = await plisio.is_payment_completed(invoice_id)

    if not is_paid:
        await callback.message.edit_text(
            "⏳ پرداخت هنوز تأیید نشده.\n\n"
            "لطفاً چند دقیقه صبر کن و دوباره امتحان کن.\n"
            "تراکنش‌های TRC20 معمولاً ۱-۳ دقیقه طول میکشه.",
            reply_markup=confirm_payment_kb(invoice_id)
        )
        return

    payment = await get_payment(invoice_id)
    if not payment:
        await callback.message.edit_text("❌ اطلاعات پرداخت یافت نشد.")
        return

    plan_type = payment[4]
    plan_key = payment[5]

    if plan_type == "time":
        plan = TIME_PLANS[plan_key]
        hours = plan["hours"]
        data_limit_gb = 0
        expires_at = datetime.now() + timedelta(hours=hours)
        plan_label = plan["label"]
    else:
        plan = DATA_PLANS[plan_key]
        data_limit_gb = plan["gb"]
        hours = 720
        expires_at = datetime.now() + timedelta(hours=720)
        plan_label = plan["label"]

    marzban_username = f"user_{callback.from_user.id}_{str(uuid.uuid4())[:6]}"
    user_data = await marzban.create_user(marzban_username, data_limit_gb, hours)

    if "username" not in user_data:
        await callback.message.edit_text(
            "❌ خطا در ساخت کانفیگ. با پشتیبانی تماس بگیر:\n@ConfigSNB"
        )
        return

    config_link = await marzban.get_user_config_link(marzban_username)

    await add_purchase(
        callback.from_user.id,
        plan_type,
        plan_key,
        payment[3],
        marzban_username,
        config_link,
        invoice_id,
        expires_at.strftime("%Y-%m-%d %H:%M:%S")
    )

    await update_payment_status(invoice_id, "completed")

    expire_str = expires_at.strftime("%Y/%m/%d")
    data_info = "نامحدود" if plan_type == "time" else f"{data_limit_gb} گیگ"

    await callback.message.edit_text(
        f"✅ کانفیگ شما آماده است!\n\n"
        f"📦 پلن: {plan_label}\n"
        f"📅 انقضا: {expire_str}\n"
        f"📊 حجم: {data_info}\n\n"
        f"🔗 لینک کانفیگ:\n"
        f"`{config_link}`\n\n"
        "━━━━━━━━━━━━━━━\n"
        "📱 راهنمای نصب:\n\n"
        "🤖 اندروید: V2rayNG\n"
        "🍎 iOS: Streisand\n"
        "💻 ویندوز: V2rayN\n\n"
        "لینک بالا رو کپی کن و داخل نرم‌افزار Import کن.\n"
        "━━━━━━━━━━━━━━━\n"
        "❓ مشکل داری؟ با پشتیبانی تماس بگیر:\n"
        "@ConfigSNB",
        parse_mode="Markdown"
    )


@router.callback_query(F.data == "cancel_payment")
async def cancel_payment(callback: CallbackQuery):
    await callback.message.edit_text(
        "❌ پرداخت لغو شد.\n\nهر وقت خواستی از منو اقدام کن."
    )


# ==================== حساب کاربری ====================

@router.message(F.text == "👤 حساب کاربری")
async def my_account(message: Message):
    purchase = await get_active_purchase(message.from_user.id)

    if not purchase:
        await message.answer(
            "❌ شما هنوز اکانت فعالی ندارید.",
            reply_markup=my_account_kb(False)
        )
        return

    plan_type = purchase[2]
    plan_key = purchase[3]
    expires_at = purchase[10]
    marzban_username = purchase[5]

    if plan_type == "time":
        plan_label = TIME_PLANS[plan_key]["label"]
    else:
        plan_label = DATA_PLANS[plan_key]["label"]

    usage = await marzban.get_user_usage(marzban_username)
    used_gb = usage["used_gb"]
    status = usage["status"]

    expire_date = datetime.strptime(expires_at, "%Y-%m-%d %H:%M:%S")
    days_left = (expire_date - datetime.now()).days
    expire_str = expire_date.strftime("%Y/%m/%d")

    status_emoji = "🟢" if status == "active" else "🔴"
    status_text = "فعال" if status == "active" else "منقضی"

    if plan_type == "time":
        usage_text = f"📊 حجم مصرفی: {used_gb} گیگ"
    else:
        total_gb = DATA_PLANS[plan_key]["gb"]
        remaining = round(total_gb - used_gb, 2)
        usage_text = f"📊 حجم مصرفی: {used_gb} گیگ از {total_gb} گیگ ({remaining} گیگ مانده)"

    await message.answer(
        f"👤 حساب کاربری من\n\n"
        f"📦 پلن: {plan_label}\n"
        f"{status_emoji} وضعیت: {status_text}\n"
        f"📅 انقضا: {expire_str} ({days_left} روز مانده)\n"
        f"{usage_text}",
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
        f"🔗 لینک کانفیگ شما:\n\n"
        f"`{config_link}`\n\n"
        "این لینک رو کپی کن و داخل V2rayNG یا Streisand یا V2rayN وارد کن.",
        parse_mode="Markdown"
    )


@router.callback_query(F.data == "purchase_history")
async def purchase_history(callback: CallbackQuery):
    purchases = await get_purchase_history(callback.from_user.id)

    if not purchases:
        await callback.answer("تاریخچه‌ای وجود ندارد.", show_alert=True)
        return

    text = "📋 تاریخچه خریدها:\n\n"
    for p in purchases:
        plan_type = p[2]
        plan_key = p[3]
        status = p[9]
        created = p[10]

        if plan_type == "time":
            plan_label = TIME_PLANS.get(plan_key, {}).get("label", plan_key)
        else:
            plan_label = DATA_PLANS.get(plan_key, {}).get("label", plan_key)

        status_emoji = "🟢" if status == "active" else "⚫"
        text += f"{status_emoji} {plan_label} — {created[:10]}\n"

    await callback.message.answer(text)


@router.callback_query(F.data == "renew_account")
async def renew_account(callback: CallbackQuery):
    await callback.message.answer(
        "برای تمدید، یه پلن جدید انتخاب کن:",
        reply_markup=plan_type_kb()
    )


@router.callback_query(F.data == "new_plan")
async def new_plan(callback: CallbackQuery):
    await callback.message.answer(
        "نوع پلن رو انتخاب کن:",
        reply_markup=plan_type_kb()
    )


@router.callback_query(F.data == "buy_config")
async def buy_config_cb(callback: CallbackQuery):
    await callback.message.answer(
        "نوع پلن رو انتخاب کن:",
        reply_markup=plan_type_kb()
    )


# ==================== بازگشت ====================

@router.callback_query(F.data == "back_main")
async def back_main(callback: CallbackQuery):
    await callback.message.edit_text("از منوی زیر انتخاب کن:")


@router.callback_query(F.data == "back_plantype")
async def back_plantype(callback: CallbackQuery):
    await callback.message.edit_text(
        "نوع پلن رو انتخاب کن:",
        reply_markup=plan_type_kb()
    )


# ==================== سایر دکمه‌ها ====================

@router.message(F.text == "🎁 کانفیگ رایگان")
async def free_config(message: Message):
    await message.answer(
        "🎁 کانفیگ رایگان هر روز چندین بار در کانال ما ارسال میشه.\n\n"
        "📢 برای دریافت عضو کانال بشو:\n"
        "@ConfigSN_free"
    )


@router.message(F.text == "📞 پشتیبانی")
async def support(message: Message):
    await message.answer(
        "📞 پشتیبانی:\n\n"
        "برای ارتباط با پشتیبانی پیام بده:\n"
        "@ConfigSNB\n\n"
        "⏰ ساعات پاسخگویی: ۹ صبح تا ۱۲ شب"
    )


@router.message(F.text == "📢 کانال ما")
async def our_channel(message: Message):
    await message.answer(
        "📢 کانال ما:\n\n"
        "برای دریافت کانفیگ رایگان روزانه عضو بشو:\n"
        "@ConfigSN_free"
    )


@router.message(F.text == "❓ راهنما")
async def help_msg(message: Message):
    await message.answer(
        "❓ راهنمای استفاده:\n\n"
        "۱. روی 📦 خرید کانفیگ بزن\n"
        "۲. نوع پلن رو انتخاب کن\n"
        "۳. مبلغ رو به آدرس USDT واریز کن\n"
        "۴. دکمه ✅ پرداخت کردم رو بزن\n"
        "۵. کانفیگ رو دریافت کن و داخل نرم‌افزار وارد کن\n\n"
        "📱 نرم‌افزارهای پیشنهادی:\n"
        "🤖 اندروید: V2rayNG\n"
        "🍎 iOS: Streisand\n"
        "💻 ویندوز: V2rayN"
    )
