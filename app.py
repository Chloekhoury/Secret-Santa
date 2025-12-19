from flask import Flask, request
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.getenv("PORT", 10000))

app = Flask(__name__)

secret_santa = {
    8314370785: 953010204,
    6435812686: 1550705452,
}

# Telegram bot
telegram_app = ApplicationBuilder().token(BOT_TOKEN).build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎄 Send me your Secret Santa gift and I’ll deliver it anonymously!")

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

telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(MessageHandler(filters.ALL, forward_gift))

@app.route("/", methods=["GET"])
def home():
    return "Secret Santa bot is running 🎄", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), telegram_app.bot)
    asyncio.create_task(telegram_app.update_queue.put(update))
    return "OK", 200

# -------------------------
# Only run on local dev
# -------------------------
if __name__ == "__main__":
    asyncio.run(telegram_app.initialize())
    asyncio.run(telegram_app.bot.set_webhook(f"{WEBHOOK_URL}/webhook"))
    app.run(host="0.0.0.0", port=PORT)
