import os
import sys
import traceback
import telebot

print("[BOOT] main.py basladi", flush=True)

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    print("[BOOT] HATA: BOT_TOKEN bulunamadi", flush=True)
    raise RuntimeError("BOT_TOKEN Railway Variables içinde tanımlı değil.")

print("[BOOT] BOT_TOKEN mevcut", flush=True)

try:
    bot = telebot.TeleBot(TOKEN)
    print("[BOOT] TeleBot olusturuldu", flush=True)

    @bot.message_handler(commands=["start"])
    def start(message):
        bot.reply_to(message, "🤖 Bot aktif.\n\n/id — Telegram kullanıcı ID'nizi gösterir\n/help — Yardım")

    @bot.message_handler(commands=["id"])
    def user_id(message):
        bot.reply_to(message, f"🆔 Telegram ID: {message.from_user.id}")

    @bot.message_handler(commands=["help"])
    def help_command(message):
        bot.reply_to(message, "Komutlar:\n/start — Botu başlat\n/id — Kullanıcı ID'sini göster\n/help — Yardım")

    @bot.message_handler(func=lambda message: True)
    def text_handler(message):
        bot.reply_to(message, "Mesajın alındı. Güvenli bot modu aktif.")

    print("[BOOT] Telegram polling baslatiliyor...", flush=True)
    bot.infinity_polling(skip_pending=True, timeout=30, long_polling_timeout=30)

except Exception as exc:
    print(f"[BOOT] UYGULAMA HATASI: {type(exc).__name__}: {exc}", flush=True)
    traceback.print_exc()
    sys.exit(1)
