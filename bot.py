
import os
import asyncio
import whisper
import nest_asyncio
from pydub import AudioSegment
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, CallbackContext

# 📌 פתרון לשגיאת event loop ב-Colab
nest_asyncio.apply()

# 📌 הכנס את ה-API Token שלך מה-BotFather
TELEGRAM_BOT_TOKEN = "your-bot-token-here"  # 🔹 הכנס את הטוקן שלך כאן

# 📌 בדיקה אם GPU זמין ושימוש ב-CUDA אם אפשרי
import torch
device = "cuda" if torch.cuda.is_available() else "cpu"

# 📌 טעינת מודל Whisper
model = whisper.load_model("small")

print(f"🚀 מודל Whisper נטען על {device.upper()}")

# 📌 פונקציה להורדת ההודעה הקולית, המרתה ותמלול
async def transcribe_voice(update: Update, context: CallbackContext):
    voice = update.message.voice or update.message.audio
    file_id = voice.file_id

    # 📌 הורדת הקובץ מהשרת של טלגרם
    new_file = await context.bot.get_file(file_id)
    file_path = "voice_note.ogg"
    await new_file.download_to_drive(file_path)

    # 📌 בדיקת הפורמט – אם הקובץ הוא OPUS (WhatsApp), נמיר אותו ל-WAV
    converted_file_path = "converted.wav"
    audio = AudioSegment.from_file(file_path, format="ogg")
    audio.export(converted_file_path, format="wav")

    # 📌 ביצוע תמלול עם Whisper
    result = model.transcribe(converted_file_path, language="he")
    transcript = result["text"]

    # 📌 שליחת התמלול בחזרה למשתמש
    await update.message.reply_text(f"🎤 תמלול: {transcript}")

    # 📌 ניקוי קבצים זמניים
    os.remove(file_path)
    os.remove(converted_file_path)

# 📌 יצירת הבוט והפעלתו
async def run_bot():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.VOICE | filters.AUDIO, transcribe_voice))
    print("🤖 הבוט מופעל! מחכה להודעות קוליות...")
    await app.run_polling()

# 📌 הפעלת הבוט ב-Colab בלי בעיות Event Loop
loop = asyncio.get_event_loop()
if loop.is_running():
    print("⚠️ Event loop כבר רץ, מפעיל את הבוט בתוך task...")
    task = loop.create_task(run_bot())
else:
    loop.run_until_complete(run_bot())
