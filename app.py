import os
import asyncio
import threading
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.getenv("PORT", 10000))

secret_santa = {
    8314370785: 953010204,
    6435812686: 1550705452,
}

# Build Telegram app (do NOT call start_polling)
telegram_app = ApplicationBuilder().token(BOT_TOKEN).build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎄 Send me your Secret Santa gift and I’ll deliver it anonymously!"
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

telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(MessageHandler(filters.ALL, forward_gift))

# Flask app
app = Flask(__name__)

@app.get("/")
def home():
    return "Secret Santa bot is running 🎄", 200

@app.post("/webhook")
def webhook():
    update = Update.de_json(request.get_json(force=True), telegram_app.bot)
    telegram_app.update_queue.put_nowait(update)
    return "OK", 200

# -------------------------
# Start Telegram app in background thread
# -------------------------
def run_async_loop():
    asyncio.run(telegram_app.initialize())
    asyncio.run(telegram_app.start())
    # Set webhook
    asyncio.run(telegram_app.bot.set_webhook(f"{WEBHOOK_URL}/webhook"))
    asyncio.get_event_loop().run_forever()

threading.Thread(target=run_async_loop, daemon=True).start()

# -------------------------
# Start Flask server
# -------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
