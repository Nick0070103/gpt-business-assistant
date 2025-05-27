import logging
import os
import openai
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# --- НАСТРОЙКИ ---
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

logging.basicConfig(level=logging.INFO)
tasks = []  # Список задач в памяти

# --- Команды ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я твой ИИ-компаньон. Просто пиши свои задачи или вопросы, и я помогу.")

async def svodka(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if tasks:
        message = "\n".join([f"🔹 {t['text']} (до {t['due']})" for t in tasks])
    else:
        message = "Пока что задач нет."
    await update.message.reply_text("📅 Текущие задачи:\n" + message)

# --- Ответ на обычное сообщение ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    # Если есть слово "до" — попробуем сохранить как задачу
    if "до" in user_text:
        parts = user_text.split("до")
        task_text = parts[0].strip()
        try:
            due_date = parts[1].strip()
            tasks.append({"text": task_text, "due": due_date})
            await update.message.reply_text(f"✅ Задача добавлена: {task_text} (до {due_date})")
            return
        except:
            pass

    # Отправка в GPT-4
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Ты умный, вежливый, критически мыслящий бизнес-ассистент, помогаешь с управлением проектами, не забываешь задачи, общаешься тепло и по делу."},
            {"role": "user", "content": user_text}
        ]
    )
    reply = response.choices[0].message.content
    await update.message.reply_text(reply)

# --- Запуск ---
app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("svodka", svodka))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("Бот запущен...")
app.run_polling()
