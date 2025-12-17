import os
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import asyncio

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = "https://secret-santa-yzga.onrender.com/webhook"

# -----------------------------------------
# SECRET SANTA
# -----------------------------------------
secret_santa = {
    8314370785: 953010204,
    6435812686: 1550705452,
}

# -----------------------------------------
# FLASK SERVER
# -----------------------------------------
app = Flask(__name__)

@app.get("/")
def home():
    return "Bot is online!", 200

# Telegram webhook endpoint
@app.post("/webhook")
def webhook():
    update = Update.de_json(request.get_json(force=True), bot.application.bot)
    bot.application.create_task(bot.application.process_update(update))
    return "OK", 200


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


# -----------------------------------------
# STARTUP (WEBHOOK MODE)
# -----------------------------------------
async def start_bot():
    global bot
    bot = ApplicationBuilder().token(BOT_TOKEN).build()

    bot.add_handler(CommandHandler("start", start))
    bot.add_handler(MessageHandler(filters.ALL, forward_gift))

    # remove old webhook
    await bot.bot.delete_webhook(drop_pending_updates=True)

    # set new webhook
    await bot.bot.set_webhook(url=WEBHOOK_URL)

    print("Webhook set ✓")


if __name__ == "__main__":
    # Start telegram bot loop in background
    asyncio.get_event_loop().create_task(start_bot())

    # Run Flask (Render sets PORT automatically)
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
