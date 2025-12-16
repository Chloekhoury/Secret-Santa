from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters

import os
BOT_TOKEN = os.getenv("BOT_TOKEN")
# -----------------------------------------
#  SECRET SANTA ASSIGNMENTS
# -----------------------------------------
# Format:
# secret_santa = {
#     SENDER_USER_ID: RECEIVER_USER_ID,
# }

secret_santa = {
    # Example:
    8314370785: 953010204,
    6435812686: 1550705452,
}

# -----------------------------------------
# START COMMAND
# -----------------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hi! 🎄 Send me your Secret Santa gift (text, photo, voice…), "
        "and I will deliver it anonymously!"
    )

# -----------------------------------------
# HANDLE ANY MESSAGE
# -----------------------------------------
async def forward_gift(update: Update, context: ContextTypes.DEFAULT_TYPE):

    sender_id = update.message.from_user.id

    # 1. Check if sender is in the game
    if sender_id not in secret_santa:
        await update.message.reply_text(
            "You are not in the Secret Santa list yet."
        )
        return

    # 2. Find the receiver
    receiver_id = secret_santa[sender_id]

    # 3. Forward the message ANONYMOUSLY
    try:
        # Works for all message types automatically
        await context.bot.copy_message(
            chat_id=receiver_id,
            from_chat_id=update.message.chat_id,
            message_id=update.message.message_id,
            caption="🎁 Anonymous Secret Santa gift!"
        )
    except Exception as e:
        await update.message.reply_text("Error delivering the gift.")
        print(e)
        return

    # 4. Confirm to the sender privately
    await update.message.reply_text("🎀 Your anonymous gift was delivered!")


# -----------------------------------------
# RUN THE BOT
# -----------------------------------------
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.ALL, forward_gift))

print("Bot is running…")
app.run_polling()

