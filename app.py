import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from aiohttp import web

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.getenv("PORT", 10000))

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

# aiohttp server for webhook
async def handle(request):
    update = Update.de_json(await request.json(), telegram_app.bot)
    await telegram_app.update_queue.put(update)
    return web.Response(text="OK")

app = web.Application()
app.router.add_post("/webhook", handle)
app.router.add_get("/", lambda request: web.Response(text="Secret Santa bot is running 🎄"))

async def on_startup(app):
    await telegram_app.initialize()
    await telegram_app.bot.set_webhook(f"{WEBHOOK_URL}/webhook")
    print("Webhook set!")

app.on_startup.append(on_startup)

if __name__ == "__main__":
    web.run_app(app, port=PORT)
