from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import os
from flask import Flask, request
import threading

BOT_TOKEN = os.getenv("BOT_TOKEN")
BASE_URL = "https://secret-santa-2-6ah3.onrender.com"   # ⚠️ Replace if your URL changes

# -----------------------------------------
# SECRET SANTA
# -----------------------------------------
secret_santa = {
    8314370785: 953010204,
    6435812686: 1550705452,
}

# -----------------------------------------
# FLASK SERVER FOR WEBHOOK
# -----------------------------------------
app_web = Flask(__name__)
application = None   # global PTB application object

@app_web.get("/")
def home():
    return "Bot is running!", 200

@app_web.post("/webhook")
def webhook():
    global application
    update_data = request.get_json(force=True)
    update = Update.de_json(update_data, application.bot)
    application.create_update(update)
    return "OK", 200

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app_web.run(host="0.0.0.0", port=port)

# -----------------------------------------
# TELEGRAM BOT HANDLERS
# -----------------------------------------
async def start(update, context):
    await update.message.reply_text(
        "Hi! 🎄 Send me your Secret Santa gift and I’ll deliver it anonymously!"
    )

async def forward_gift(update, context):
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
# RUN (Webhook mode)
# -----------------------------------------
def main():
    global application

    # Start Flask server for webhook
    threading.Thread(target=run_flask, daemon=True).start()

    # Build telegram bot application
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.ALL, forward_gift))

    # Set webhook
    webhook_url = f"{BASE_URL}/webhook"
    application.bot.set_webhook(webhook_url)
    print("Webhook set at:", webhook_url)

    # PTB idle loop
    application.run_polling(stop_signals=None)

if __name__ == "__main__":
    main()

