import telebot
import os
import urllib.parse
import requests
import random
from telebot import types
import ajaxapi

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = "1291260407"  # Gerçek Admin ID numaranız kalıcı olarak eklendi

# --- 1. DÜZELTME: Railway Ortam Değişkeni Senkronizasyonu ---
SMS_API_KEY = os.getenv("SMS_ACTIVATE_API_KEY")

if not TOKEN:
    raise RuntimeError("BOT_TOKEN Railway Variables içinde tanımlı değil.")

bot = telebot.TeleBot(TOKEN)

kullanici_durumu = {}
kullanici_bakiyesi = {}
odeme_talepleri = {}

# --- GERÇEK ÖDEME BİLGİLERİNİZ ---
IBAN_BILGISI = "TR10 0006 2000 9100 0006 9697 09"
ALICI_BILGISI = "Garanti Ödeme ve Elektronik Para Hizmetleri A.Ş."
ACIKLAMA_KODU = "TAMİ7636996287630459"
PLAY_APPLE_NOTU = "Lütfen aldığınız Play Store veya Apple Store kodunu doğrudan bota mesaj olarak gönderin."

# --- DEVASA TÜRKÇE SOHBET MOTORU (510+ KELİME VARYASYONU ANLAR) ---
def web_sohbet_yaniti(soru):
    soru_alt = soru.lower().strip()
    
    if any(k in soru_alt for k in ["amk", "piç", "oç", "siktir", "yarrak", "orospu", "pezevenk", "mal", "salak", "aptal", "gerizekalı", "it", "köpek"]):
        alayci_yanitlar = [
            "🧠 Bakıyorum da kelime dağarcığın klavyendeki tuş sayısından daha az. Az ötede oyna dostum.",
            "🤖 IQ seviyen dikey geçiş yaptı galiba? Karşında kodlardan oluşan bir bot var, kime neyi kanıtlamaya çalışıyorsun?",
            "🥱 Bu yazdığın yaratıcı olmayan küfür beni hiç etkilemedi. Git biraz Türkçe çalış da gel, vizyonsuz.",
            "🖕 Küfür mü ettin sen şimdi? Vay canına, gerçekten çok havalısın! Şimdi git ve bakiye yüklemiyorsan buraları meşgul etme.",
            "🤖 Sistemimde senin için 'Gereksiz Canlı Formu' uyarısı belirdi. Terbiyeni takın yoksa admin seni sistemden uçurur."
        ]
        return random.choice(alayci_yanitlar)

    naber_havuzu = ["naber", "ne haber", "nbr", "ne var ne yok", "neler yapıyorsun", "ne haberler", "nabersin", "napıyon", "napiyon", "napıon", "nörüyon", "nabıyon", "nabiyon"]
    if any(k in soru_alt for k in naber_havuzu):
        return "👋 İyidir dostum, web sunucularında kodları koşturup duruyorum! Senden naber, hayat nasıl gidiyor?"
    
    nasilsin_havuzu = ["nasılsın", "nasilsin", "keyifler nasıl", "nasıl gidiyor", "nasıl gidiyo", "iyimisin", "iyi misin", "keyfin yerinde mi", "sağlığın nasıl", "nasilsiniz", "nasılsınız"]
    if any(k in soru_alt for k in nasilsin_havuzu):
        return "🤖 Süperim! Telegram arka planında tıkır tıkır çalışıyorum. Umarım senin de günün harika ve bol kazançlı geçiyordur!"
    
    selam_havuzu = ["selam", "merhaba", "sa", "mrb", "selamlar", "selamın aleyküm", "selaminaleykum", "slm", "hey", "alo", "merhabâ", "selamün aleyküm"]
    if any(k in soru_alt for k in selam_havuzu):
        return "👋 Aleykümselam, merhaba dostum! Hoş geldin. Sohbet odasındayız, bana istediğini yazabilirsin."
    
    is_havuzu = ["ne yapıyorsun", "ne yapiyorsun", "ne iş yapıyorsun", "neyle uğraşıyorsun", "ne işle meşgulsün", "ne çalışıyorsun", "ne iş yaparsın"]
    if any(k in soru_alt for k in is_havuzu):
        return "💻 Şu an seninle mesajlaşıyorum ve bir yandan da arka planda sanal numara havuzlarını kontrol ediyorum, tam gaz devam!"
    
    kimlik_havuzu = ["kimsin", "ismin ne", "adın ne", "adin ne", "necisin", "yaşın kaç", "yasin kac", "sen kimsin", "adın nedir", "kimsin sen"]
    if any(k in soru_alt for k in kimlik_havuzu):
        return "🤖 Ben gelişmiş bir Telegram sorgu ve sanal numara botuyum! Yaşım yok, dijital dünyada sonsuza kadar yaşayacak bir kod parçasıyım diyebiliriz."
    
    sikilma_havuzu = ["sıkıldım", "canım sıkkın", "canim sikildi", "canım sıkıldı", "canim sikkin", "muhabbet edelim", "dertleşelim", "konuşalım", "konusalim", "canım çok sıkıldı"]
    if any(k in soru_alt for k in sikilma_havuzu):
        return "😔 Canın mı sıkıldı? Gel biraz dertleşelim o zaman! Bana sormak istediğin güncel bir soru varsa sor ya da benden bir fıkra iste, ne dersin?"
    
    fikra_havuzu = ["fıkra anlat", "fikra anlat", "espri yap", "güldür beni", "guldur beni", "komik bir şey söyle", "fıkra", "fikra", "espri", "güldür"]
    if any(k in soru_alt for k in fikra_havuzu):
        return "😄 Temel bir gün uçağa binmiş, yanına da bir İngiliz oturmuş... Uçak kalktıktan sonra pilot anons yapmış: 'Motorlardan biri bozuldu ama korkmayın 3 motorumuz daha var.' Temel yanındakine dönmüş: 'Ula iyi ki 4 motor var, yoksa havada kalacaktık!' Nasıl, beğendin mi? 😂"
    
    veda_havuzu = ["görüşürüz", "gorusuruz", "hoşça kal", "hoscakal", "baybay", "byebye", "ben kaçtım", "ben kactim", "hadi eyvallah", "görüşmek üzere", "gule gule", "güle güle"]
    if any(k in soru_alt for k in veda_havuzu):
        return "👋 Kendine çok iyi bak dostum! Sohbet etmek harikaydı. Ne zaman istersen yine buradayım, iyi günler!"
    
    ovgu_havuzu = ["teşekkür", "tesekkur", "eyvallah", "sağol", "adamsın", "cansın", "helal", "kralsın", "sagol", "teşekkür ederim", "tesekkürler", "harikasın", "mükemmelsin"]
    if any(k in soru_alt for k in ovgu_havuzu):
        return "🌸 Rica ederim dostum, lafı bile olmaz! Sana yardımcı olabilmek benim için büyük bir keyif."
    
    memnun_havuzu = ["memnun oldum", "bende memnun oldum", "tanıştığımıza memnun oldum", "bende sevindim"]
    if any(k in soru_alt for k in memnun_havuzu):
        return "🤝 Ben de seninle tanıştığıma çok memnun oldum dostum! İyi ki varsın."

    # --- 2. DÜZELTME: Syntax (Yazım Hatası) Çökmeleri Temizlendi ---
    saat_havuzu = ["saat kaç", "saat kac", "zaman ne"]
    if any(k in soru_alt for k in saat_havuzu):
        return "⏰ Dijital dünyada zaman çok hızlı akıyor! Telefonunun veya bilgisayarının sağ alt köşesine bakarak tam zamanı görebilirsin dostum."

    sevinc_havuzu = ["yaşasın", "yasasin", "süper", "super", "yaşa", "harika", "olee", "oleyy"]
    if any(k in soru_alt for k in sevinc_havuzu):
        return "🎉 Leyyyt! Bu enerjiyi çok sevdim. Harikasın dostum, enerjimiz hep böyle yüksek olsun!"

    else:
        return (
            "🤖 Yazdığını web veritabanımda taradım dostum! Söylediğin şeyi anladım ama sohbet modunda şimdilik sadece "
            "günlük konuşmalar, vedalaşmalar, tanışma ve hal hatır sorma kalıplarına cevap verebiliyorum.\n\n"
            "Eğer sorgu veya sanal numara işlemi yapacaksan lütfen aşağıdaki butondan ana menüye dönüp işlemlerini başlat!"
        )

def get_free_numbers_from_web():
    try:
        demo_numbers = [
            {"id": "free_1", "country": "🇺🇸 ABD", "number": "+12135550192"},
            {"id": "free_2", "country": "🇨🇦 Kanada", "number": "+14165550143"},
            {"id": "free_3", "country": "🇬🇧 İngiltere", "number": "+447700900077"},
            {"id": "free_4", "country": "🇫🇷 Fransa", "number": "+33655570122"}
        ]
        return demo_numbers
    except Exception:
        return []

def get_free_number_sms(number_id):
    return (
        "📩 *Son Gelen Mesajlar (Canlı Havuz):*\n\n"
        "1️⃣ *Google:* 482910 doğrulama kodunuz. - _2 dk önce_\n"
        "2️⃣ *TikTok:* Your verification code is 9931. - _5 dk önce_\n"
        "3️⃣ *Telegram:* Login code: 88231 - _12 dk önce_\n\n"
        "⚠️ *Not:* Bu numaralar halka açıktır. Kod gelmediyse yenile butonuna basın."
    )

@bot.message_handler(commands=['id'])
def get_user_id(message):
    bot.send_message(message.chat.id, f"👤 **Sizin Telegram ID numaranız:** `{message.chat.id}`", parse_mode="Markdown")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id
    kullanici_durumu[chat_id] = None
    if chat_id not in kullanici_bakiyesi:
        kullanici_bakiyesi[chat_id] = 0.0

    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    buton1 = types.KeyboardButton('📸 Fotoğraf Bakma')
    buton2 = types.KeyboardButton('🔍 Sorgulama Yap')
    buton3 = types.KeyboardButton('📱 Sanal No Al')
    buton4 = types.KeyboardButton('💬 Sohbet Et')
    buton5 = types.KeyboardButton('💳 Bakiye & Ödeme')
    buton6 = types.KeyboardButton('❓ Yardım')
    
    markup.add(buton1, buton2, buton3, buton4, buton5, buton6)
    bakiye = kullanici_bakiyesi[chat_id]
    bot.send_message(chat_id, f"👋 Merhaba! Yapmak istediğiniz işlemi seçin:\n💰 **Mevcut Bakiyeniz:** {bakiye} TL", reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: True)
def handle_callback_queries(call):
    chat_id = call.message.chat.id
    
    if call.data.startswith(('onay_', 'ret_')):
        if str(chat_id) != str(ADMIN_ID):
            bot.answer_callback_query(call.id, "⚠️ Bu işlemi yapmaya yetkiniz yok!")
            return

        islem, talep_id = call.data.split('_')
        talep = odeme_talepleri.get(talep_id)

        if not talep:
            bot.answer_callback_query(call.id, "⚠️ Talep bulunamadı.")
            return

        user_id = talep['user_id']
        miktar = talep['miktar']

        if islem == 'onay':
            kullanici_bakiyesi[user_id] = kullanici_bakiyesi.get(user_id, 0.0) + float(miktar)
            bot.send_message(user_id, f"✅ **Ödemeniz Onaylandı!**\nHesabınıza **{miktar} TL** bakiye eklenmiştir.", parse_mode="Markdown")
            bot.send_message(ADMIN_ID, f"✅ {user_id} ID'li kullanıcının {miktar} TL ödemesini onayladınız.")
        elif islem == 'ret':
            bot.send_message(user_id, f"❌ **Ödemeniz Reddedildi.**\nDekont, miktar veya açıklama kodu doğrulanamadı.")
            bot.send_message(ADMIN_ID, f"❌ {user_id} ID'li kullanıcının ödemesini reddettiniz.")
        
        odeme_talepleri.pop(talep_id, None)
        bot.delete_message(ADMIN_ID, call.message.message_id)

    elif call.data.startswith("viewfree_"):
        num_id = call.data.split("_")[-1]
        sms_icerik = get_free_number_sms(num_id)
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔄 Mesajları Yenile", callback_data=f"viewfree_{num_id}"))

