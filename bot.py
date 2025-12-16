from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")

# -----------------------------------------
# SECRET SANTA
# -----------------------------------------
secret_santa = {
    8314370785: 953010204,
    6435812686: 1550705452,
}

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
# RUN (PTB 20+ syntax)
# -----------------------------------------
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.ALL, forward_gift))

    print("Bot is running...")
    app.run_polling()   # ✔️ This is valid in PTB20

if __name__ == "__main__":
    main()
