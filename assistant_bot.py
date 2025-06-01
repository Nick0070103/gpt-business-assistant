# assistant_bot.py
import logging
import os
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from database import TaskDB
from logic import parse_task_message, task_summary
from prompts import chat_with_gpt

# Получаем переменные окружения
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
REMINDER_CHAT_ID = os.getenv("REMINDER_CHAT_ID") or ""

if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN is not set")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is not set")

# --- Инициализация ---
db = TaskDB("tasks.db")
scheduler = AsyncIOScheduler()
logging.basicConfig(level=logging.INFO)

# --- Команды ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я твой ИИ-компаньон. Просто пиши задачи, спрашивай, спорь — я здесь, чтобы помогать.")

async def list_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tasks = db.get_all_tasks()
    summary = task_summary(tasks)
    await update.message.reply_text(summary or "📭 Задач пока нет")

async def clear_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db.clear_tasks()
    await update.message.reply_text("🧹 Память очищена. Начинаем с чистого листа.")

# --- Напоминания ---
async def monday_reminder():
    tasks = db.get_all_tasks()
    summary = task_summary(tasks, monday_mode=True)
    if summary and REMINDER_CHAT_ID:
        await app.bot.send_message(chat_id=REMINDER_CHAT_ID, text=summary)

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

# --- Запуск ---
app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("tasks", list_tasks))
app.add_handler(CommandHandler("clear", clear_tasks))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

scheduler.add_job(monday_reminder, 'cron', day_of_week='mon', hour=9)
scheduler.start()

print("\n\U0001f680 Бот запущен...")
app.run_polling()
