import os
import sys
import traceback
import json
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

print("[BOOT 1] main.py basladi", flush=True)

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    print("[BOOT 2] HATA: BOT_TOKEN yok", flush=True)
    raise RuntimeError("BOT_TOKEN Railway Variables içinde tanımlı değil.")

print("[BOOT 2] BOT_TOKEN mevcut", flush=True)

try:
    import telebot
    from telebot import types
    print("[BOOT 3] telebot import edildi", flush=True)
except Exception as exc:
    print(f"[BOOT 3] telebot import HATASI: {type(exc).__name__}: {exc}", flush=True)
    traceback.print_exc()
    sys.exit(1)

bot = telebot.TeleBot(TOKEN)

def ana_menu():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(
        types.KeyboardButton("📱 Sanal No"),
        types.KeyboardButton("💰 Bakiye"),
        types.KeyboardButton("💬 Sohbet"),
        types.KeyboardButton("👤 Telegram ID"),
        types.KeyboardButton("❓ Yardım"),
    )
    return markup

def smsvirtual_profile():
    api_key = os.getenv("SMSV_API_KEY")
    if not api_key:
        return None, "SMSV_API_KEY tanımlı değil."

    req = Request(
        "https://api.smsvirtual.io/v1/profile/",
        headers={"x-api-key": api_key, "Accept": "application/json"},
        method="GET",
    )
    try:
        with urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))
        return data, None
    except HTTPError as exc:
        return None, f"API HTTP hatası: {exc.code}"
    except (URLError, TimeoutError) as exc:
        return None, f"API bağlantı hatası: {type(exc).__name__}"
    except Exception as exc:
        return None, f"API hatası: {type(exc).__name__}"

def sohbet_yanit(metin):
    m = metin.lower().strip()
    if any(x in m for x in ("merhaba", "selam", "s.a", "sa")):
        return "👋 Selam kanka! Bot aktif. Ana menüden bir işlem seçebilirsin."
    if any(x in m for x in ("nasılsın", "nasilsin", "naber")):
        return "😄 İyiyim kanka, bot çalışıyor!"
    if any(x in m for x in ("teşekkür", "tesekkur", "sağol", "sagol")):
        return "Rica ederim kanka! 🙌"
    return "🤖 Mesajını aldım. Ana menüdeki seçeneklerden birini kullanabilirsin."

@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(
        message.chat.id,
        "🤖 *Bot aktif!*

"
        "Aşağıdaki güvenli özelliklerden birini seçebilirsin.",
        reply_markup=ana_menu(),
        parse_mode="Markdown",
    )

@bot.message_handler(commands=["id"])
def user_id(message):
    bot.reply_to(message, f"🆔 Telegram ID: {message.from_user.id}")

@bot.message_handler(commands=["help"])
def help_command(message):
    bot.send_message(
        message.chat.id,
        "❓ *Yardım*

"
        "📱 Sanal No — SMS Virtual hesabındaki bilgileri görüntüler.
"
        "💰 Bakiye — SMS Virtual hesap bakiyesini kontrol eder.
"
        "💬 Sohbet — Basit sohbet modu.
"
        "👤 Telegram ID — Telegram kullanıcı ID'nizi gösterir.

"
        "Komutlar: /start /id /help",
        parse_mode="Markdown",
        reply_markup=ana_menu(),
    )

@bot.message_handler(func=lambda message: message.text == "👤 Telegram ID")
def menu_id(message):
    user_id(message)

@bot.message_handler(func=lambda message: message.text == "❓ Yardım")
def menu_help(message):
    help_command(message)

@bot.message_handler(func=lambda message: message.text == "💰 Bakiye")
def balance(message):
    data, error = smsvirtual_profile()
    if error:
        bot.reply_to(message, f"⚠️ Bakiye alınamadı: {error}")
        return
    profile = data.get("profile", data) if isinstance(data, dict) else {}
    balance_value = profile.get("balance", data.get("balance", "bilinmiyor")) if isinstance(profile, dict) else "bilinmiyor"
    bot.reply_to(message, f"💰 SMS Virtual bakiye: {balance_value}")

@bot.message_handler(func=lambda message: message.text == "📱 Sanal No")
def virtual_number(message):
    bot.send_message(
        message.chat.id,
        "📱 *Sanal Numara*

"
        "Bu menü şu anda yalnızca hesabın durumunu kontrol eder. "
        "Numara satın alma veya doğrulama işlemi otomatikleştirilmemiştir.",
        parse_mode="Markdown",
    )

@bot.message_handler(func=lambda message: message.text == "💬 Sohbet")
def chat_mode(message):
    bot.reply_to(message, "💬 Sohbet moduna geçtik. Bana bir mesaj yaz.")

@bot.message_handler(func=lambda message: True)
def text_handler(message):
    bot.reply_to(message, sohbet_yanit(message.text or ""))

try:
    print("[BOOT 4] TeleBot olusturuldu", flush=True)
    me = bot.get_me()
    print(f"[BOOT 5] Telegram baglantisi OK: @{me.username}", flush=True)
    try:
        bot.delete_webhook(drop_pending_updates=False)
        print("[BOOT 6] Webhook temizlendi", flush=True)
    except Exception as exc:
        print(f"[BOOT 6] Webhook temizleme uyarisi: {type(exc).__name__}: {exc}", flush=True)

    print("[BOOT 7] Guvenli menu hazir", flush=True)
    print("[BOOT 8] Polling baslatiliyor...", flush=True)

    while True:
        try:
            bot.infinity_polling(skip_pending=True, timeout=30, long_polling_timeout=30)
        except Exception as exc:
            msg = str(exc)
            if "409" in msg and "getUpdates" in msg:
                print("[POLLING] 409 Conflict: baska bir getUpdates istemcisi var. 15 sn sonra tekrar denenecek.", flush=True)
                import time
                time.sleep(15)
                continue
            raise

except Exception as exc:
    print(f"[BOOT] UYGULAMA HATASI: {type(exc).__name__}: {exc}", flush=True)
    traceback.print_exc()
    sys.exit(1)
