import os
import io
import json
import urllib.request
import telebot
from telebot import types
from telebot import apihelper
import ajaxapi

TOKEN = os.getenv("BOT_TOKEN")
SMSV_API_KEY = os.getenv("SMSV_API_KEY")
if not TOKEN:
    raise RuntimeError("BOT_TOKEN Railway Variables içinde tanımlı değil.")

# Railway/egress proxy katmanlarında biriken Session header/cookie durumunun
# Telegram API isteklerini 431 ile bozmasını önlemek için her Telegram isteğinde
# yeni HTTP session kullan.
apihelper.SESSION_TIME_TO_LIVE = 0

bot = telebot.TeleBot(TOKEN)
kullanici_durumu = {}

def send_result_file(chat_id, sonuc):
    icerik = f"📊 Sorgu Sonucu:\n\n{str(sonuc)}"
    dosya = io.BytesIO(icerik.encode("utf-8"))
    dosya.name = "sorgu_sonucu.txt"
    bot.send_document(
        chat_id,
        dosya,
        caption="📄 Sorgu sonucu dosya olarak hazır."
    )

def sms_api_get(path):
    if not SMSV_API_KEY:
        raise RuntimeError("SMS Virtual API anahtarı Railway'de bulunamadı.")
    req = urllib.request.Request(
        "https://api.smsvirtual.io/v1" + path,
        headers={"x-api-key": SMSV_API_KEY, "Accept": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=15) as response:
        return json.loads(response.read().decode("utf-8"))


def sms_menu(message):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(
        types.KeyboardButton("💰 SMS Bakiye"),
        types.KeyboardButton("🌍 SMS Ülkeleri"),
        types.KeyboardButton("📋 SMS Servisleri"),
        types.KeyboardButton("📦 Aktif Numaralar"),
        types.KeyboardButton("🔙 Ana Menüye Dön")
    )
    bot.send_message(
        message.chat.id,
        "📱 Sanal Numara Menüsü\n\nSMS Virtual hesabındaki bakiye, ülke/servis seçenekleri ve aktif numaralarını buradan görüntüleyebilirsin.",
        reply_markup=markup
    )


def send_json_list(chat_id, title, data):
    payload = data.get("data") if isinstance(data, dict) else data
    text = title + "\n\n"
    if isinstance(payload, list):
        if not payload:
            text += "Kayıt bulunamadı."
        for item in payload[:40]:
            if isinstance(item, dict):
                parts = []
                for key in ("id", "serviceId", "name", "code", "country", "countryCode"):
                    if key in item and item[key] not in (None, ""):
                        parts.append(f"{key}: {item[key]}")
                text += "• " + (" | ".join(parts) if parts else str(item)) + "\n"
            else:
                text += "• " + str(item) + "\n"
    elif isinstance(payload, dict):
        for key, value in list(payload.items())[:40]:
            text += f"• {key}: {value}\n"
    else:
        text += str(payload)
    bot.send_message(chat_id, text[:4000])


@bot.message_handler(commands=['start'])
def send_welcome(message):
    kullanici_durumu[message.chat.id] = None
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(
        types.KeyboardButton('📸 Fotoğraf Bakma'),
        types.KeyboardButton('🔍 Sorgulama Yap'),
        types.KeyboardButton('📱 Sanal Numara'),
        types.KeyboardButton('❓ Yardım')
    )
    bot.send_message(chat_id=message.chat.id, text="👋 Merhaba! Yapmak istediğiniz işlemi seçin:", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    chat_id = message.chat.id
    text = message.text

    if text == '📸 Fotoğraf Bakma':
        bot.send_message(chat_id, "📸 Fotoğraf bakma menüsündesiniz. Lütfen bir görsel gönderin.")

    elif text == '📱 Sanal Numara':
        sms_menu(message)

    elif text == '💰 SMS Bakiye':
        try:
            data = sms_api_get("/profile/")
            if data.get("status") is True:
                profile = data.get("data") or {}
                bot.send_message(chat_id, "💰 SMS Virtual Bakiye: $" + str(profile.get("balance", "bilinmiyor")))
            else:
                bot.send_message(chat_id, "❌ API hatası: " + str(data.get("code", "UNKNOWN")))
        except Exception as e:
            bot.send_message(chat_id, "❌ SMS Virtual bağlantı hatası: " + type(e).__name__)

    elif text == '🌍 SMS Ülkeleri':
        try:
            data = sms_api_get("/country")
            if data.get("status") is True:
                send_json_list(chat_id, "🌍 SMS Virtual Ülkeleri", data)
            else:
                bot.send_message(chat_id, "❌ API hatası: " + str(data.get("code", "UNKNOWN")))
        except Exception as e:
            bot.send_message(chat_id, "❌ Ülke listesi alınamadı: " + type(e).__name__)

    elif text == '📋 SMS Servisleri':
        try:
            data = sms_api_get("/services")
            if data.get("status") is True:
                send_json_list(chat_id, "📋 SMS Virtual Servisleri", data)
            else:
                bot.send_message(chat_id, "❌ API hatası: " + str(data.get("code", "UNKNOWN")))
        except Exception as e:
            bot.send_message(chat_id, "❌ Servis listesi alınamadı: " + type(e).__name__)

    elif text == '📦 Aktif Numaralar':
        try:
            data = sms_api_get("/order/active")
            if data.get("status") is True:
                send_json_list(chat_id, "📦 Aktif SMS Virtual Numaraları", data)
            else:
                bot.send_message(chat_id, "❌ API hatası: " + str(data.get("code", "UNKNOWN")))
        except Exception as e:
            bot.send_message(chat_id, "❌ Aktif numaralar alınamadı: " + type(e).__name__)
    elif text == '🔍 Sorgulama Yap' or text == '🔙 Sorgu Menüsüne Dön':
        markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        markup.add(
            types.KeyboardButton('🆔 TC Sorgu'), types.KeyboardButton('💎 TC Pro Sorgu'),
            types.KeyboardButton('👤 Ad Soyad Sorgu'), types.KeyboardButton('👨‍👩‍👧‍👦 Aile Sorgu'),
            types.KeyboardButton('🌳 Sülale Sorgu'), types.KeyboardButton('📱 TC -> GSM Sorgu'),
            types.KeyboardButton('📞 GSM -> TC Sorgu'), types.KeyboardButton('🏫 E-Okul Sorgu'),
            types.KeyboardButton('🏠 Adres Sorgu'), types.KeyboardButton('📜 Tapu Sorgu'),
            types.KeyboardButton('🗺️ Ada Parsel Sorgu'), types.KeyboardButton('🔙 Ana Menüye Dön')
        )
        bot.send_message(chat_id, "🔍 Lütfen yapmak istediğiniz detaylı sorgu türünü seçin:", reply_markup=markup)
    elif text == '❓ Yardım':
        bot.send_message(chat_id, "ℹ️ Yardım Menüsü\n\nİstediğiniz sorgu butonuna tıkladıktan sonra botun sizden istediği bilgileri doğru formatta yazmanız yeterlidir.")
    elif text == '🔙 Ana Menüye Dön':
        send_welcome(message)
    elif text in ['🆔 TC Sorgu', '💎 TC Pro Sorgu', '👨‍👩‍👧‍👦 Aile Sorgu', '🌳 Sülale Sorgu', '📱 TC -> GSM Sorgu', '🏫 E-Okul Sorgu', '🏠 Adres Sorgu', '📜 Tapu Sorgu']:
        kullanici_durumu[chat_id] = text
        bot.send_message(chat_id, "📝 Lütfen sorgulanacak 11 haneli TC Kimlik Numarasını yazın:")
    elif text == '👤 Ad Soyad Sorgu':
        kullanici_durumu[chat_id] = text
        bot.send_message(chat_id, "📝 Lütfen aralarında bir boşluk bırakarak AD SOYAD yazın\n(Örn: ROKET ATAR):")
    elif text == '📞 GSM -> TC Sorgu':
        kullanici_durumu[chat_id] = text
        bot.send_message(chat_id, "📝 Lütfen sorgulanacak GSM Numarasını yazın\n(Örn: 5550000000):")
    elif text == '🗺️ Ada Parsel Sorgu':
        kullanici_durumu[chat_id] = text
        bot.send_message(chat_id, "📝 Lütfen İl ve İlçe bilgisini virgülle ayırarak yazın\n(Örn: İSTANBUL, KADIKÖY):")
    else:
        durum = kullanici_durumu.get(chat_id)
        if durum is None:
            bot.send_message(chat_id, "⚠️ Lütfen önce menüden bir işlem seçin veya /start yazın.")
            return
        bot.send_message(chat_id, "⏳ Sorgulanıyor, lütfen bekleyin...")
        try:
            if durum == '🆔 TC Sorgu': sonuc = ajaxapi.tc(text)
            elif durum == '💎 TC Pro Sorgu': sonuc = ajaxapi.tc_pro(text)
            elif durum == '👨‍👩‍👧‍👦 Aile Sorgu': sonuc = ajaxapi.aile(text)
            elif durum == '🌳 Sülale Sorgu': sonuc = ajaxapi.sulale(text)
            elif durum == '📱 TC -> GSM Sorgu': sonuc = ajaxapi.tc_gsm(text)
            elif durum == '🏫 E-Okul Sorgu': sonuc = ajaxapi.eokul(text)
            elif durum == '🏠 Adres Sorgu': sonuc = ajaxapi.adres(text)
            elif durum == '📜 Tapu Sorgu': sonuc = ajaxapi.tapu(text)
            elif durum == '📞 GSM -> TC Sorgu': sonuc = ajaxapi.gsm_tc(text)
            elif durum == '👤 Ad Soyad Sorgu':
                parcalar = text.split(" ", 1)
                sonuc = ajaxapi.ad_soyad(parcalar[0], parcalar[1] if len(parcalar) > 1 else "")
            elif durum == '🗺️ Ada Parsel Sorgu':
                parcalar = text.split(",", 1)
                sonuc = ajaxapi.ada_parsel(parcalar[0].strip(), parcalar[1].strip() if len(parcalar) > 1 else "")
            send_result_file(chat_id, sonuc)
        except Exception as e:
            bot.send_message(chat_id, f"❌ Sorgu sırasında bir hata oluştu veya kütüphane yanıt vermedi.\nHata: {str(e)}")
        kullanici_durumu[chat_id] = None

print("Telegram Gelişmiş Sorgu Botu Aktif! Mesajlar bekleniyor...")
bot.infinity_polling()
