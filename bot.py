import os
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import asyncio

# Telegram bot token from Render environment
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # you will set this in Render

# -----------------------------
# SECRET SANTA PAIRS
# -----------------------------
secret_santa = {
    8314370785: 953010204,
    6435812686: 1550705452,
}

# -----------------------------
# TELEGRAM BOT HANDLERS
# -----------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hi! 🎄 Send me your Secret Santa gift and I’ll deliver it anonymously!"
    )

async def forward_gift(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sender_id = update.message.from_user.id

    if sender_id not in secret_santa:
        await update.message.reply_text("You’re not in the Secret Santa list.")
        return

    receiver_id = secret_santa[sender_id]

    try:
        await context.bot.copy_message(
            chat_id=receiver_id,
            from_chat_id=update.message.chat_id,
            message_id=update.message.message_id,
            caption="🎁 Anonymous Secret Santa gift!",
        )
    except Exception as e:
        print("Error:", e)
        await update.message.reply_text("Error delivering the gift.")
        return

    await update.message.reply_text("🎀 Your anonymous gift was delivered!")


# -----------------------------
# FLASK APP (WEBHOOK ENDPOINT)
# -----------------------------
flask_app = Flask(__name__)
bot_app = None  # Telegram application (initialized later)

@flask_app.route("/webhook", methods=["POST"])
def webhook():
    """Receives Telegram updates."""
    data = request.get_json()

    if bot_app is not None:
        asyncio.run(bot_app.process_update(Update.de_json(data, bot_app.bot)))

    return "OK", 200


# -----------------------------
# RUN BOTH: FLASK + WEBHOOK
# -----------------------------
async def init_bot():
    global bot_app

    bot_app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Add handlers
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(MessageHandler(filters.ALL, forward_gift))

    # Set webhook
    await bot_app.bot.set_webhook(url=f"{WEBHOOK_URL}/webhook")

    print("Webhook set at:", f"{WEBHOOK_URL}/webhook")


def main():
    # Start Telegram bot (async)
    asyncio.get_event_loop().run_until_complete(init_bot())

    # Start Flask server
    port = int(os.environ.get("PORT", 5000))
    flask_app.run(host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
