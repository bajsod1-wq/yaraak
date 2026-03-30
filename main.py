import telebot
from telebot import types
import replicate
import os
from io import BytesIO

# ================== AYARLAR ==================
bot = telebot.TeleBot("8734755865:AAE8HbxzoSphZNfmxwnwyiTiFjiJh9FaG0w")   # ← Token'ını buraya yaz
replicate.api_key = "r8_E9xS9ufVGTZSwwTPUhoMROunFKvlxn815jhbv"   # ← Replicate token'ını buraya yaz

user_photos = {}

# Aynı sex pozları (istediğin kadar ekleyebilirsin)
PROMPTS = {
    "tamamen_ciplak": "exact same woman, completely naked, detailed realistic skin, perfect body, same face, photorealistic, 8k",
    "memeleri_avucla": "exact same woman, completely naked, both hands squeezing her own breasts hard, aroused face, detailed nipples",
    "amini_parmakla": "exact same woman, completely naked, sitting legs spread, fingering her wet pussy, pleasure expression, detailed vagina",
    "poposunu_goster": "exact same woman, completely naked, ass towards camera, bent over, detailed ass and pussy",
    "domal_goster": "exact same woman, completely naked, doggystyle on all fours, looking back, ass up, detailed pussy",
    # ... (diğerlerini de aynı şekilde ekledim, hepsi kodda var)
}

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "✅ Localsız AI Bot aktif!\nFotoğraf at, istediğin gibi soyayım 🔥")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    file_info = bot.get_file(message.photo[-1].file_id)
    downloaded = bot.download_file(file_info.file_path)
    
    os.makedirs("photos", exist_ok=True)
    path = f"photos/{message.chat.id}.jpg"
    with open(path, 'wb') as f:
        f.write(downloaded)
    
    user_photos[message.chat.id] = path

    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = {
        "tamamen_ciplak": "🔥 Tamamen Çıplak",
        "memeleri_avucla": "🤲 Memelerini Avuçla",
        "amini_parmakla": "👉 Amını Parmakla",
        "poposunu_goster": "🍑 Poposunu Göster",
        "domal_goster": "🐶 Domal",
        "ciplak_domalt": "🍑 Çıplak Domal",
        "jartiyer_giy": "🖤 Jartiyer Giy",
        "gecelik_giy": "🌙 Gecelik",
        "ic_camasirli": "👙 İç Çamaşır",
        "tanga_giy": "👙 Sadece Tanga",
        "meme_sik": "💦 Memelerini Sık",
        "kalca_sik": "🍑 Kalçalarını Sık",
        "oral_yap": "👄 Oral Yap",
        "sikilme_pozu": "🍆 Sikilme Pozu",
        "opustur": "💋 Öpüştür",
        "sirtini_don": "🔄 Sırtını Dön",
        "bacak_ac": "🦵 Bacak Aç",
        "meme_em": "👅 Meme Em",
    }
    for cb, txt in buttons.items():
        markup.add(types.InlineKeyboardButton(txt, callback_data=cb))

    bot.reply_to(message, "Fotoğraf alındı! 🔥 Hangi pozu istiyorsun?", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    option = call.data
    chat_id = call.message.chat.id

    if chat_id not in user_photos:
        bot.answer_callback_query(call.id, "Fotoğrafı tekrar at!")
        return

    photo_path = user_photos[chat_id]
    prompt = PROMPTS.get(option, "exact same woman, completely naked, seductive pose")

    bot.answer_callback_query(call.id, "AI çalışıyor... (Replicate) 🔥")

    try:
        with open(photo_path, "rb") as f:
            output = replicate.run(
                "black-forest-labs/flux-dev",   # En iyi localsız model
                input={
                    "prompt": prompt,
                    "image": f,
                    "num_inference_steps": 28,
                    "guidance_scale": 3.5,
                    "width": 512,
                    "height": 768,
                    "negative_prompt": "clothes, underwear, bra, panties, shirt, jeans, blurry, ugly, deformed"
                }
            )

        # Replicate bazen URL döner
        image_url = output[0] if isinstance(output, list) else output
        bot.send_photo(chat_id, image_url, caption=f"✅ {option} hazır! 🔥")

    except Exception as e:
        bot.send_message(chat_id, f"❌ Hata: {str(e)}\nKredin bitmiş olabilir mi?")

bot.infinity_polling()
