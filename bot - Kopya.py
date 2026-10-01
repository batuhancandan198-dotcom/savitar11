import telebot
import os
from telebot import types
import io
import ajaxapi  # Orijinal sorgu kütüphaneniz

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise RuntimeError("BOT_TOKEN Railway Variables içinde tanımlı değil.")

bot = telebot.TeleBot(TOKEN)

# Kullanıcının hangi sorgu aşamasında olduğunu takip etmek için geçici hafıza
kullanici_durumu = {}

# 1. ANA MENÜ (/start)
@bot.message_handler(commands=['start'])
def send_welcome(message):
    kullanici_durumu[message.chat.id] = None  # Durumu sıfırla
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    
    buton1 = types.KeyboardButton('📸 Fotoğraf Bakma')
    buton2 = types.KeyboardButton('🔍 Sorgulama Yap')
    buton3 = types.KeyboardButton('❓ Yardım')
    
    markup.add(buton1, buton2, buton3)
    bot.send_message(message.chat.id, "👋 Merhaba! Yapmak istediğiniz işlemi seçin:", reply_markup=markup)

# TXT gönderme mekanizmasının güvenli test komutu.
# Hassas kişisel veri içermeyen sabit test çıktısı gönderir.
@bot.message_handler(commands=['txttest'])
def txt_test(message):
    icerik = "TXT test çıktısı\n\nDosya gönderimi çalışıyor.\n"
    dosya = io.BytesIO(icerik.encode("utf-8"))
    dosya.name = "txt_test.txt"
    bot.send_document(message.chat.id, dosya, caption="📄 TXT test dosyası")

# 2. BUTON TIKLAMALARINI VE MENÜLERİ YÖNETEN KISIM
@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    chat_id = message.chat.id
    text = message.text

    # Ana Menü Butonları
    if text == '📸 Fotoğraf Bakma':
        bot.send_message(chat_id, "📸 Fotoğraf bakma menüsündesiniz. Lütfen bir görsel gönderin.")
        
    elif text == '🔍 Sorgulama Yap' or text == '🔙 Sorgu Menüsüne Dön':
        # Detaylı Sorgu Alt Menüsü
        markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        
        markup.add(
            types.KeyboardButton('🆔 TC Sorgu'),
            types.KeyboardButton('💎 TC Pro Sorgu'),
            types.KeyboardButton('👤 Ad Soyad Sorgu'),
            types.KeyboardButton('👨‍👩‍👧‍👦 Aile Sorgu'),
            types.KeyboardButton('🌳 Sülale Sorgu'),
            types.KeyboardButton('📱 TC -> GSM Sorgu'),
            types.KeyboardButton('📞 GSM -> TC Sorgu'),
            types.KeyboardButton('🏫 E-Okul Sorgu'),
            types.KeyboardButton('🏠 Adres Sorgu'),
            types.KeyboardButton('📜 Tapu Sorgu'),
            types.KeyboardButton('🗺️ Ada Parsel Sorgu'),
            types.KeyboardButton('🔙 Ana Menüye Dön')
        )
        bot.send_message(chat_id, "🔍 Lütfen yapmak istediğiniz detaylı sorgu türünü seçin:", reply_markup=markup)

    elif text == '❓ Yardım':
        bot.send_message(chat_id, "ℹ️ *Yardım Menüsü*\n\nİstediğiniz sorgu butonuna tıkladıktan sonra botun sizden istediği bilgileri (TC, GSM veya Ad Soyad) doğru formatta yazmanız yeterlidir.", parse_mode="Markdown")

    elif text == '🔙 Ana Menüye Dön':
        send_welcome(message)

    # --- ALT SORGU SEÇENEKLERİNİN TETİKLENMESİ ---
    elif text in ['🆔 TC Sorgu', '💎 TC Pro Sorgu', '👨‍👩‍👧‍👦 Aile Sorgu', '🌳 Sülale Sorgu', '📱 TC -> GSM Sorgu', '🏫 E-Okul Sorgu', '🏠 Adres Sorgu', '📜 Tapu Sorgu']:
        kullanici_durumu[chat_id] = text
        bot.send_message(chat_id, f"📝 Lütfen sorgulanacak **11 haneli TC Kimlik Numarasını** yazın:", parse_mode="Markdown")

    elif text == '👤 Ad Soyad Sorgu':
        kullanici_durumu[chat_id] = text
        bot.send_message(chat_id, "📝 Lütfen aralarında bir boşluk bırakarak **AD SOYAD** yazın\n_(Örn: ROKET ATAR)_:", parse_mode="Markdown")

    elif text == '📞 GSM -> TC Sorgu':
        kullanici_durumu[chat_id] = text
        bot.send_message(chat_id, "📝 Lütfen sorgulanacak **GSM Numarasını** yazın\n_(Örn: 5550000000)_:", parse_mode="Markdown")

    elif text == '🗺️ Ada Parsel Sorgu':
        kullanici_durumu[chat_id] = text
        bot.send_message(chat_id, "📝 Lütfen İl ve İlçe bilgisini aralarında virgül bırakarak yazın\n_(Örn: İSTANBUL, KADIKÖY)_:")

    # --- KULLANICI METİN YAZDIĞINDA ---
    else:
        durum = kullanici_durumu.get(chat_id)
        
        if durum is None:
            bot.send_message(chat_id, "⚠️ Lütfen önce menüden bir işlem seçin veya /start yazın.")
            return

        bot.send_message(chat_id, "⏳ Sorgulanıyor, lütfen bekleyin...")
        
        try:
            # Seçilen duruma göre ajaxapi kütüphanesindeki ilgili fonksiyonu çağırıyoruz
            if durum == '🆔 TC Sorgu':
                sonuc = ajaxapi.tc(text)
            elif durum == '💎 TC Pro Sorgu':
                sonuc = ajaxapi.tc_pro(text)
            elif durum == '👨‍👩‍👧‍👦 Aile Sorgu':
                sonuc = ajaxapi.aile(text)
            elif durum == '🌳 Sülale Sorgu':
                sonuc = ajaxapi.sulale(text)
            elif durum == '📱 TC -> GSM Sorgu':
                sonuc = ajaxapi.tc_gsm(text)
            elif durum == '🏫 E-Okul Sorgu':
                sonuc = ajaxapi.eokul(text)
            elif durum == '🏠 Adres Sorgu':
                sonuc = ajaxapi.adres(text)
            elif durum == '📜 Tapu Sorgu':
                sonuc = ajaxapi.tapu(text)
            elif durum == '📞 GSM -> TC Sorgu':
                sonuc = ajaxapi.gsm_tc(text)
            elif durum == '👤 Ad Soyad Sorgu':
                parcalar = text.split(" ", 1)
                ad = parcalar[0]
                soyad = parcalar[1] if len(parcalar) > 1 else ""
                sonuc = ajaxapi.ad_soyad(ad, soyad)
            elif durum == '🗺️ Ada Parsel Sorgu':
                parcalar = text.split(",", 1)
                il = parcalar[0].strip()
                ilce = parcalar[1].strip() if len(parcalar) > 1 else ""
                sonuc = ajaxapi.ada_parsel(il, ilce)

            # Mevcut sorgu sonucu gönderim davranışı korunuyor.
            bot.send_message(chat_id, f"📊 *Sorgu Sonucu:* \n\n{str(sonuc)}", parse_mode="Markdown")
            
        except Exception as e:
            bot.send_message(chat_id, f"❌ Sorgu sırasında bir hata oluştu veya kütüphane yanıt vermedi.\nHata: {str(e)}")
        
        kullanici_durumu[chat_id] = None

# Kesintisiz çalışma döngüsü
print("Telegram Gelişmiş Sorgu Botu Aktif! Mesajlar bekleniyor...")
bot.infinity_polling()
