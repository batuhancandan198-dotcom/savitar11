import os
import telebot

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("BOT_TOKEN Railway Variables içinde tanımlı değil.")

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(
        message,
        "🤖 Bot aktif.\n\n"
        "/id — Telegram kullanıcı ID'nizi gösterir\n"
        "/help — Yardım"
    )

@bot.message_handler(commands=["id"])
def user_id(message):
    bot.reply_to(message, f"🆔 Telegram ID: {message.from_user.id}")

@bot.message_handler(commands=["help"])
def help_command(message):
    bot.reply_to(
        message,
        "Komutlar:\n"
        "/start — Botu başlat\n"
        "/id — Kullanıcı ID'sini göster\n"
        "/help — Yardım"
    )

@bot.message_handler(func=lambda message: True)
def text_handler(message):
    bot.reply_to(message, "Mesajın alındı. Güvenli bot modu aktif.")

print("Telegram bot güvenli modda aktif. Mesajlar bekleniyor...")
bot.infinity_polling(skip_pending=True, timeout=30, long_polling_timeout=30)
