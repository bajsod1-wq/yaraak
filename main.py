import telebot
from telebot import types
import fal
import requests
import os
from io import BytesIO

bot = telebot.TeleBot("8734755865:AAE8HbxzoSphZNfmxwnwyiTiFjiJh9FaG0w")
fal.key = "784ceacd-7957-42f4-a7e9-c9d094853cd0:dd65c2bb4003dcf2bd877681485dbcdb"   # ← buraya kendi key'ini yaz

user_photos = {}

# Aynı sex pozları
PROMPTS = {
    "tamamen_ciplak": "exact same woman, completely naked, detailed realistic skin, perfect body, same face, photorealistic, 8k",
    "memeleri_avucla": "exact same woman, completely naked, both hands squeezing her own breasts hard, aroused face, detailed nipples",
    "amini_parmakla": "exact same woman, completely naked, sitting legs spread, fingering her wet pussy, pleasure expression, detailed vagina",
    "poposunu_goster": "exact same woman, completely naked, ass towards camera, bent over, detailed ass and pussy",
    "domal_goster": "exact same woman, completely naked, doggystyle on all fours, looking back, ass up, detailed pussy",
    "ciplak_domalt": "exact same woman, completely naked, bent over, ass towards camera, legs spread",
    "jartiyer_giy": "exact same woman, wearing only black jartiyer and stockings, no panties, breasts exposed",
    "gecelik_giy": "exact same woman, wearing transparent black babydoll, nipples visible",
    "ic_camasirli": "exact same woman, wearing only sexy lingerie, bra and panties",
    "tanga_giy": "exact same woman, wearing only tiny black thong, topless",
    "meme_sik": "exact same woman, completely naked, squeezing her own breasts hard",
    "kalca_sik": "exact same woman, completely naked, grabbing and spreading her own ass",
    "oral_yap": "exact same woman, completely naked, on knees giving blowjob, tongue out",
    "sikilme_pozu": "exact same woman, completely naked, getting fucked from behind, moaning",
    "opustur": "exact same woman, completely naked, kissing passionately",
    "sirtini_don": "exact same woman, completely naked, back turned, looking over shoulder",
    "bacak_ac": "exact same woman, completely naked, legs wide open",
    "meme_em": "exact same woman, completely naked, sucking her own nipple",
}

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "✅ fal.ai bot aktif!\nFotoğraf at, istediğin gibi soyayım 🔥")

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
    for cb, txt in {
        "tamamen_ciplak": "🔥 Tamamen Çıplak",
        "memeleri_avucla": "🤲 Memelerini Avuçla",
        "amini_parmakla": "👉 Amını Parmakla",
        "poposunu_goster": "🍑 Poposunu Göster",
        "domal_goster": "🐶 Domal",
        "ciplak_domalt": "🍑 Çıplak Domal",
        "jartiyer_giy": "🖤 Jartiyer",
        "gecelik_giy": "🌙 Gecelik",
        "ic_camasirli": "👙 İç Çamaşır",
        "tanga_giy": "👙 Sadece Tanga",
        "meme_sik": "💦 Memelerini Sık",
        "kalca_sik": "🍑 Kalçalarını Sık",
        "oral_yap": "👄 Oral Yap",
        "sikilme_pozu": "🍆 Sikilme",
        "opustur": "💋 Öpüştür",
        "sirtini_don": "🔄 Sırtını Dön",
        "bacak_ac": "🦵 Bacak Aç",
        "meme_em": "👅 Meme Em",
    }.items():
        markup.add(types.InlineKeyboardButton(txt, callback_data=cb))

    bot.reply_to(message, "Fotoğraf alındı amk! 🔥 Hangi pozu istiyorsun?", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    option = call.data
    chat_id = call.message.chat.id

    if chat_id not in user_photos:
        bot.answer_callback_query(call.id, "Fotoğrafı tekrar at!")
        return

    photo_path = user_photos[chat_id]
    prompt = PROMPTS.get(option, "exact same woman, completely naked, seductive pose")

    bot.answer_callback_query(call.id, "fal.ai çalışıyor... 🔥")

    try:
        # Fotoğrafı 0x0.st'e yükle (ücretsiz ve anonim)
        with open(photo_path, "rb") as f:
            upload = requests.post("https://0x0.st", files={"file": f})
            image_url = upload.text.strip()

        result = fal.run(
            "fal-ai/flux/dev/image-to-image",   # En iyi img2img modeli
            input={
                "image_url": image_url,
                "prompt": prompt,
                "strength": 0.85,           # ne kadar değiştirsin (0.7-0.9 arası iyi)
                "num_inference_steps": 28,
                "guidance_scale": 3.5,
                "seed": None,
                "enable_safety_checker": False   # NSFW için kapatıyoruz
            }
        )

        image_url = result["images"][0]["url"]
        bot.send_photo(chat_id, image_url, caption=f"✅ {option} hazır! 🔥")

    except Exception as e:
        bot.send_message(chat_id, f"❌ Hata: {str(e)}\nKey doğru mu? Kredi var mı?")

bot.infinity_polling()
