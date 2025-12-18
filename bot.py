import os
from flask import Flask, request
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = os.environ["BOT_TOKEN"]
PUBLIC_URL = os.environ["PUBLIC_URL"]  # e.g. https://secret-santa.fly.dev

# -----------------------------------------
# SECRET SANTA MAPPING
# -----------------------------------------
secret_santa = {
    8314370785: 953010204,
    6435812686: 1550705452,
}

# -----------------------------------------
# TELEGRAM HANDLERS
# -----------------------------------------
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

    await context.bot.copy_message(
        chat_id=receiver_id,
        from_chat_id=update.message.chat_id,
        message_id=update.message.message_id,
        caption="🎁 Anonymous Secret Santa gift!",
    )

    await update.message.reply_text("🎀 Your anonymous gift was delivered!")

# -----------------------------------------
# FLASK + TELEGRAM APP
# -----------------------------------------
flask_app = Flask(__name__)

telegram_app = (
    ApplicationBuilder()
    .token(BOT_TOKEN)
    .build()
)

telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(MessageHandler(filters.ALL, forward_gift))

@flask_app.route("/")
def home():
    return "Secret Santa bot is running 🎄", 200

@flask_app.route("/webhook", methods=["POST"])
async def webhook():
    update = Update.de_json(request.get_json(force=True), telegram_app.bot)
    await telegram_app.process_update(update)
    return "OK", 200

# -----------------------------------------
# STARTUP
# -----------------------------------------
if __name__ == "__main__":
    import asyncio

    async def main():
        await telegram_app.bot.set_webhook(f"{PUBLIC_URL}/webhook")
        print("Webhook set!")

    asyncio.run(main())

    port = int(os.environ.get("PORT", 8080))
    flask_app.run(host="0.0.0.0", port=port)
