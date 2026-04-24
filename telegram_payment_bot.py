"""
بوت تيليجرام للدفع باستخدام Telegram Stars
يدعم بيع الخدمات للزبائن
"""

import logging
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    LabeledPrice,
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    PreCheckoutQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# ─────────────────────────────────────────
#  ⚙️  الإعدادات – عدّلها حسب احتياجك
# ─────────────────────────────────────────
import os
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# قائمة الخدمات  {id: {name, description, price_stars, emoji}}
SERVICES = {
    "service_1": {
        "name": "خدمة أساسية",
        "description": "وصف مختصر للخدمة الأساسية",
        "price_stars": 50,          # السعر بعدد النجوم
        "emoji": "⭐",
    },
    "service_2": {
        "name": "خدمة احترافية",
        "description": "وصف مختصر للخدمة الاحترافية",
        "price_stars": 150,
        "emoji": "🚀",
    },
    "service_3": {
        "name": "خدمة VIP",
        "description": "وصف مختصر لخدمة VIP المميزة",
        "price_stars": 300,
        "emoji": "👑",
    },
}

# ─────────────────────────────────────────
#  🪵  السجلات
# ─────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


# ─────────────────────────────────────────
#  🤖  أوامر البوت
# ─────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """رسالة الترحيب + عرض قائمة الخدمات"""
    user = update.effective_user
    text = (
        f"👋 أهلاً {user.first_name}!\n\n"
        "🛍️ مرحباً بك في متجرنا.\n"
        "اختر إحدى الخدمات المتاحة أدناه:"
    )
    keyboard = [
        [InlineKeyboardButton(
            f"{s['emoji']} {s['name']} — {s['price_stars']} ⭐",
            callback_data=f"buy_{sid}"
        )]
        for sid, s in SERVICES.items()
    ]
    keyboard.append([InlineKeyboardButton("ℹ️ مساعدة", callback_data="help")])
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """شرح طريقة الاستخدام"""
    text = (
        "📖 *كيفية الشراء:*\n\n"
        "1️⃣ اضغط /start لعرض الخدمات\n"
        "2️⃣ اختر الخدمة التي تريدها\n"
        "3️⃣ أكمل عملية الدفع بنجوم تيليجرام ⭐\n"
        "4️⃣ ستحصل على الخدمة فوراً بعد الدفع\n\n"
        "❓ للتواصل مع الدعم: @YourSupportUsername"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


# ─────────────────────────────────────────
#  🛒  منطق الشراء
# ─────────────────────────────────────────

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة أزرار الإنلاين"""
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "help":
        await query.message.reply_text(
            "📖 اضغط /help لقراءة تعليمات الشراء."
        )
        return

    if data.startswith("buy_"):
        service_id = data[4:]
        service = SERVICES.get(service_id)
        if not service:
            await query.message.reply_text("❌ الخدمة غير موجودة.")
            return

        # إرسال فاتورة الدفع
        await context.bot.send_invoice(
            chat_id=query.message.chat_id,
            title=service["name"],
            description=service["description"],
            payload=service_id,           # يُستخدم للتحقق لاحقاً
            currency="XTR",               # XTR = Telegram Stars
            prices=[LabeledPrice(service["name"], service["price_stars"])],
            # لا تحتاج provider_token مع Stars
        )


async def pre_checkout_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """التحقق من الطلب قبل إتمام الدفع"""
    query = update.pre_checkout_query
    service_id = query.invoice_payload

    if service_id not in SERVICES:
        await query.answer(ok=False, error_message="❌ الخدمة غير متوفرة حالياً.")
        return

    # يمكنك هنا إضافة أي تحقق إضافي (مخزون، صلاحية المستخدم، إلخ)
    await query.answer(ok=True)


async def successful_payment_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """تنفيذ الخدمة بعد الدفع الناجح"""
    payment = update.message.successful_payment
    service_id = payment.invoice_payload
    service = SERVICES.get(service_id, {})
    stars_paid = payment.total_amount

    logger.info(
        "دفع ناجح | المستخدم: %s | الخدمة: %s | النجوم: %s",
        update.effective_user.id,
        service_id,
        stars_paid,
    )

    # ─── أرسل هنا ما يحصل عليه الزبون بعد الشراء ───
    await update.message.reply_text(
        f"✅ *تم الدفع بنجاح!*\n\n"
        f"🎉 شكراً على شرائك *{service.get('name', '')}*\n"
        f"⭐ النجوم المدفوعة: {stars_paid}\n\n"
        f"📦 *تفاصيل خدمتك:*\n"
        f"{service.get('description', '')}\n\n"
        f"سيتواصل معك فريقنا قريباً. 🙏",
        parse_mode="Markdown",
    )

    # ─── مثال: أرسل إشعاراً لصاحب البوت ───
    # ADMIN_CHAT_ID = 123456789
    # await context.bot.send_message(
    #     ADMIN_CHAT_ID,
    #     f"💰 طلب جديد!\nالمستخدم: {update.effective_user.id}\nالخدمة: {service_id}"
    # )


# ─────────────────────────────────────────
#  🚀  تشغيل البوت
# ─────────────────────────────────────────

def main() -> None:
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(PreCheckoutQueryHandler(pre_checkout_handler))
    app.add_handler(
        MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_handler)
    )

    logger.info("✅ البوت يعمل...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
