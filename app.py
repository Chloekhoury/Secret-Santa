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
    8314370785: 7621440955,
    7621440955: 6435812686,
    1200358737: 8314370785,
    1102178295: 7701779702,
    6090615056: 1127250559,
    7701779702: 1550705452,
    6788861481: 6260588359,
    953010204: 8093046225,
    1127250559: 6090615056,
    8238617588: 7570345391,
    6435812686: 1590029129,
    7892946294: 1637299594,
    7938290661: 8238617588,
    8093046225: 6041436567,
    7570345391: 6788861481,
    6787987399: 1745552363,
    6260588359: 953010204,
    1550705452: 7892946294,
    1590029129: 355568598,
    1745552363: 6787987399,
    355568598: 6529739470,
    6041436567: 1200358737,
    1637299594: 1102178295,
    6529739470: 7938290661,
}

# -----------------------------------------
# USERS (Telegram user_id -> first name)
# -----------------------------------------
users = {
    1102178295: "Hari / @haryssa",
    1200358737: "Horsy / @horsyy22",
    1127250559: "Iron Clutch / @GEOO33",
    6787987399: "Zaynab / @Arabloca",
    8238617588: "Georges / @joujou213",
    1745552363: "M K / @mhk99999",
    355568598: "Mr. / @maslamat",
    6435812686: "Katniss / @straykitt",
    6260588359: "SilentHypothesis / @Habi_so5ni_habi_bardi",
    953010204: "Baja / @httpsaday",
    6041436567: "Znoos / @Abdulthaqalayn_35",
    1550705452: "J' / @Spiirts",
    7621440955: "Vehpe",
    7570345391: "X",
    8314370785: "Valentina",
    6529739470: "Summer",
    1637299594: "Bodvar",
    6090615056: "J'' / @alloushi316",
    6788861481: "Mary Jane",
    7938290661: "Sunshine / @sunsi4",
    8093046225: "Hussein / @husseinniessuh0",
    7701779702: "Youssef",
    7892946294: "CauliflourProMax / @Cauliflur",
    1590029129: "Wael Wardi / @waelw93y",
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
    user_name = update.effective_user.first_name  # Get the user's first name
    user_id = update.effective_user.id
    receiver_id = secret_santa[user_id]
    receiver_name = users.get(receiver_id, "your Secret Santa person")

    welcome_message = (
        f"Welcome {user_name} to Secret Santa! 🎁🎄\n"
        f"✨ You are the Secret Santa for **{receiver_name}** ✨\n\n"

        "Send me your gift (text, image, video, audio...) and I’ll deliver it anonymously to him/her :)\n\n"
        "🎁 And when your Secret Santa sends you a gift, I’ll send it to you safely!\n\n"
        "You can check the suggested gifts in the group, and contact an admin if you need help.\n"
        "Have fun spreading holiday cheer! 🎅"
    )
    await update.message.reply_text(welcome_message)

async def forward_gift(update, context):
    sender_id = update.message.from_user.id

    if sender_id not in secret_santa:
        await update.message.reply_text("You’re not in the Secret Santa list! Please Contact an Admin to join :)")
        return

    receiver_id = secret_santa[sender_id]

    try:
        await context.bot.copy_message(
            chat_id=receiver_id,
            from_chat_id=update.message.chat_id,
            message_id=update.message.message_id,
            caption="🎁 You've just received a gift from your Secret Santa!",
        )
    except Exception as e:
        print("Error:", e)
        await update.message.reply_text("Error delivering the gift.")
        return

    await update.message.reply_text("Your anonymous gift was delivered! 🎀")

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







