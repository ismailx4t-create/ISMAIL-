"""
بوت تيليجرام للدفع باستخدام Telegram Stars
يدعم بيع الخدمات للزبائن
"""

import logging
import os
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

BOT_TOKEN = os.environ.get("BOT_TOKEN")

SERVICES = {
    "service_1": {
        "name": "هاك ببجي يومي 🎮",
        "description": "هاك ببجي موبايل للآيفون — اشتراك يومي (24 ساعة)",
        "price_stars": 250,
        "emoji": "🔥",
    },
    "service_2": {
        "name": "هاك ببجي أسبوعي 🎮",
        "description": "هاك ببجي موبايل للآيفون — اشتراك أسبوعي (7 أيام)",
        "price_stars": 750,
        "emoji": "⚡",
    },
    "service_3": {
        "name": "هاك ببجي شهري 🎮",
        "description": "هاك ببجي موبايل للآيفون — اشتراك شهري (30 يوم)",
        "price_stars": 1900,
        "emoji": "👑",
    },
}

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    text = (
        f"👋 أهلاً {user.first_name}!\n\n"
        "🎮 مرحباً بك في متجر هاك ببجي للآيفون.\n"
        "اختر اشتراكك أدناه:"
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
    text = (
        "📖 *كيفية الشراء:*\n\n"
        "1️⃣ اضغط /start\n"
        "2️⃣ اختر الاشتراك\n"
        "3️⃣ ادفع بنجوم تيليجرام ⭐\n"
        "4️⃣ ستحصل على الهاك فوراً\n\n"
        "❓ للدعم: @YourSupportUsername"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "help":
        await query.message.reply_text("📖 اضغط /help للتعليمات.")
        return

    if data.startswith("buy_"):
        service_id = data[4:]
        service = SERVICES.get(service_id)
        if not service:
            await query.message.reply_text("❌ الخدمة غير موجودة.")
            return

        await context.bot.send_invoice(
            chat_id=query.message.chat_id,
            title=service["name"],
            description=service["description"],
            payload=service_id,
            currency="XTR",
            prices=[LabeledPrice(service["name"], service["price_stars"])],
        )


async def pre_checkout_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.pre_checkout_query
    if query.invoice_payload not in SERVICES:
        await query.answer(ok=False, error_message="❌ الخدمة غير متوفرة.")
        return
    await query.answer(ok=True)


async def successful_payment_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    payment = update.message.successful_payment
    service_id = payment.invoice_payload
    service = SERVICES.get(service_id, {})

    await update.message.reply_text(
        f"✅ *تم الدفع بنجاح!*\n\n"
        f"🎮 شكراً على شرائك *{service.get('name', '')}*\n"
        f"⭐ النجوم المدفوعة: {payment.total_amount}\n\n"
        f"سيتواصل معك فريقنا قريباً لتفعيل الهاك. 🙏",
        parse_mode="Markdown",
    )


def main() -> None:
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(PreCheckoutQueryHandler(pre_checkout_handler))
    app.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_handler))
    logger.info("✅ البوت يعمل...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
