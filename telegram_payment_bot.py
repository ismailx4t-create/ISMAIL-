"""
بوت ذكي للرد التلقائي على الزبائن
خاص بمبيعات هاك ببجي موبايل
"""

import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
)

# ─────────────────────────────────────────
#  ⚙️  الإعدادات
# ─────────────────────────────────────────
BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_USERNAME = "@rocksx44"

# مراحل المحادثة
DEVICE, COUNTRY, PLAN = range(3)

# الأسعار بالدولار
PRICES_USD = {
    "daily":   {"label": "يومي",    "price": 5},
    "weekly":  {"label": "أسبوعي",  "price": 15},
    "monthly": {"label": "شهري",    "price": 30},
}

# أسعار الصرف التقريبية
COUNTRIES = {
    "🇲🇦 المغرب":       {"currency": "درهم",  "rate": 10.0},
    "🇩🇿 الجزائر":      {"currency": "دينار", "rate": 135.0},
    "🇸🇦 السعودية":     {"currency": "ريال",  "rate": 3.75},
    "🇮🇶 العراق":       {"currency": "دينار", "rate": 1310.0},
    "🇾🇪 اليمن":        {"currency": "ريال",  "rate": 250.0},
    "🇯🇴 الأردن":       {"currency": "دينار", "rate": 0.71},
    "🇱🇧 لبنان":        {"currency": "دولار", "rate": 1.0},
    "🇶🇦 قطر":          {"currency": "ريال",  "rate": 3.64},
    "🇰🇼 الكويت":       {"currency": "دينار", "rate": 0.31},
    "🇪🇬 مصر":          {"currency": "جنيه",  "rate": 48.0},
    "🇦🇪 الإمارات":     {"currency": "درهم",  "rate": 3.67},
    "🌍 دولة أخرى":     {"currency": "دولار", "rate": 1.0},
}

# مميزات الهاك
FEATURES = """
🎮 *مميزات أوزيس للآيفون* 🔥
بدون جلبريك ✅

👇 مواصفات الهاك:
• 📡 رادار سلس جداً ✅
• ⚡ بدون تقطيع وبدون لاق ✅
• 🎯 ايم بوت ذكي وآمن ✅
• ✨ خالي من المشاكل حرفياً ✅
"""

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


# ─────────────────────────────────────────
#  🤖  ردود ذكية على الرسائل
# ─────────────────────────────────────────

GREETINGS = ["السلام", "سلام", "هلا", "مرحبا", "مرحباً", "اهلا", "أهلاً", "هاي", "hi", "hello", "ص"]
SUBSCRIPTION_WORDS = ["اشتراك", "اشترك", "شراء", "اشتري", "سعر", "كم", "باكج", "باقة"]

async def smart_reply(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text.lower()
    user = update.effective_user

    # رد على التحية
    if any(g in text for g in GREETINGS):
        await update.message.reply_text(
            f"وعليكم السلام ورحمة الله 👋\n"
            f"أهلاً {user.first_name}! كيف يمكنني مساعدتك؟ 😊\n\n"
            f"اكتب *اشتراك* إذا أردت معرفة باقاتنا 🎮",
            parse_mode="Markdown"
        )
        return ConversationHandler.END

    # رد على طلب الاشتراك
    if any(w in text for w in SUBSCRIPTION_WORDS):
        keyboard = [
            [InlineKeyboardButton("📱 آيفون (iOS)", callback_data="device_ios")],
            [InlineKeyboardButton("🤖 أندرويد", callback_data="device_android")],
        ]
        await update.message.reply_text(
            "🎮 أهلاً بك في متجر هاك ببجي!\n\n"
            "ما نوع جهازك؟",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return DEVICE

    return ConversationHandler.END


async def device_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    if query.data == "device_android":
        await query.message.reply_text(
            "⚠️ عذراً، الهاك متاح للآيفون فقط حالياً.\n"
            "للاستفسار تواصل مع الدعم: " + ADMIN_USERNAME
        )
        return ConversationHandler.END

    # آيفون — عرض المميزات
    keyboard = [[InlineKeyboardButton("✅ عرض الأسعار", callback_data="show_countries")]]
    await query.message.reply_text(
        FEATURES,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return COUNTRY


async def show_countries(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    keyboard = []
    row = []
    for i, country in enumerate(COUNTRIES.keys()):
        row.append(InlineKeyboardButton(country, callback_data=f"country_{country}"))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)

    await query.message.reply_text(
        "🌍 من أي دولة أنت؟\n(لعرض الأسعار بعملتك)",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return COUNTRY


async def country_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    country = query.data.replace("country_", "")
    info = COUNTRIES.get(country, {"currency": "دولار", "rate": 1.0})
    context.user_data["country"] = country
    context.user_data["currency"] = info["currency"]
    context.user_data["rate"] = info["rate"]

    rate = info["rate"]
    currency = info["currency"]

    keyboard = []
    for plan_id, plan in PRICES_USD.items():
        local_price = round(plan["price"] * rate, 2)
        if currency == "دولار":
            price_text = f"{plan['price']}$"
        else:
            price_text = f"{local_price} {currency} (~{plan['price']}$)"
        keyboard.append([InlineKeyboardButton(
            f"{'🔥' if plan_id=='daily' else '⚡' if plan_id=='weekly' else '👑'} {plan['label']} — {price_text}",
            callback_data=f"plan_{plan_id}"
        )])

    await query.message.reply_text(
        f"💰 *الأسعار لـ {country}:*",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return PLAN


async def plan_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    plan_id = query.data.replace("plan_", "")
    plan = PRICES_USD[plan_id]
    country = context.user_data.get("country", "")
    currency = context.user_data.get("currency", "دولار")
    rate = context.user_data.get("rate", 1.0)

    local_price = round(plan["price"] * rate, 2)
    if currency == "دولار":
        price_text = f"{plan['price']}$"
    else:
        price_text = f"{local_price} {currency}"

    await query.message.reply_text(
        f"✅ *اخترت الاشتراك {plan['label']}*\n\n"
        f"💵 السعر: {price_text}\n\n"
        f"للإتمام الشراء تواصل مع:\n"
        f"👤 {ADMIN_USERNAME}\n\n"
        f"أرسل له:\n"
        f"• نوع الاشتراك: {plan['label']}\n"
        f"• بلدك: {country}",
        parse_mode="Markdown"
    )
    return ConversationHandler.END


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    keyboard = [
        [InlineKeyboardButton("🎮 عرض الباقات", callback_data="device_ios")],
        [InlineKeyboardButton("💬 تواصل مع الدعم", url=f"https://t.me/rocksx44")],
    ]
    await update.message.reply_text(
        f"👋 أهلاً {user.first_name}!\n\n"
        f"🎮 *متجر هاك ببجي للآيفون*\n\n"
        f"• بدون جلبريك ✅\n"
        f"• رادار + ايم بوت ✅\n"
        f"• بدون لاق ✅\n\n"
        f"اضغط عرض الباقات للبدء 👇",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("تم الإلغاء. اكتب /start للبدء من جديد.")
    return ConversationHandler.END


# ─────────────────────────────────────────
#  🚀  تشغيل البوت
# ─────────────────────────────────────────

def main() -> None:
    app = Application.builder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[
            MessageHandler(filters.TEXT & ~filters.COMMAND, smart_reply),
            CallbackQueryHandler(device_handler, pattern="^device_"),
        ],
        states={
            DEVICE: [CallbackQueryHandler(device_handler, pattern="^device_")],
            COUNTRY: [
                CallbackQueryHandler(show_countries, pattern="^show_countries$"),
                CallbackQueryHandler(country_handler, pattern="^country_"),
            ],
            PLAN: [CallbackQueryHandler(plan_handler, pattern="^plan_")],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_handler)

    logger.info("✅ البوت الذكي يعمل...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
