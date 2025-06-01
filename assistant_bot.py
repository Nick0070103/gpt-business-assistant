
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, filters
)
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from database import TaskDB
from logic import parse_task_message, task_summary
from prompts import chat_with_gpt
import os

# --- Инициализация ---
TOKEN = os.environ.get("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
REMINDER_CHAT_ID = os.environ.get("REMINDER_CHAT_ID")

app = ApplicationBuilder().token(TOKEN).build()
scheduler = AsyncIOScheduler()
db = TaskDB()

# --- Команды ---
async def list_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    summary = task_summary(db.get_tasks())
    await update.message.reply_text(summary or "Задач пока нет 💤")

async def clear_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db.clear_tasks()
    await update.message.reply_text("🧽 Память очищена. Начинаем с чистого листа.")

# --- Напоминалка ---
async def monday_reminder():
    text = task_summary(db.get_tasks()) or "Задач нет."
    await app.bot.send_message(chat_id=REMINDER_CHAT_ID, text=f"📌 Напоминание на понедельник:\n\n{text}")

# --- Сообщения ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    try:
        task = parse_task_message(user_text)
        if task:
            db.add_task(**task)
            await update.message.reply_text(f"✅ Задача добавлена: {task['text']} (до {task['due_date']})")
        else:
            reply = chat_with_gpt(user_text, OPENAI_API_KEY, db)
            await update.message.reply_text(reply)
    except Exception as e:
        logging.exception("Ошибка обработки сообщения")
        await update.message.reply_text("🤖 Не смог придумать ответ. Попробуй ещё раз.")

# --- Регистрация ---
app.add_handler(CommandHandler("start", list_tasks))
app.add_handler(CommandHandler("tasks", list_tasks))
app.add_handler(CommandHandler("clear", clear_tasks))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

scheduler.add_job(monday_reminder, 'cron', day_of_week='mon', hour=9)
scheduler.start()

print("\n🚀 Бот запущен...\n")
app.run_polling()
