import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler,
    MessageHandler, filters, ContextTypes
)
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from logic import parse_task_message, task_summary
from database import TaskDB
from prompts import chat_with_gpt
from config import TELEGRAM_TOKEN, OPENAI_API_KEY

db = TaskDB()
scheduler = AsyncIOScheduler()

# --- Задачи ---
async def list_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    summary = task_summary(db.get_all_tasks())
    await update.message.reply_text(summary or "Задач пока НЕТ 🥲")

async def clear_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db.clear_tasks()
    await update.message.reply_text("🧹 Память очищена. Начинаем с чистого листа.")

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

# --- Напоминания ---
async def monday_reminder():
    print("🔔 Напоминание: проверь задачи на неделю!")

# --- Запуск бота ---
app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app.add_handler(CommandHandler("tasks", list_tasks))
app.add_handler(CommandHandler("clear", clear_tasks))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

scheduler.add_job(monday_reminder, 'cron', day_of_week='mon', hour=9)
scheduler.start()

print("🚀 Бот запущен...")
app.run_polling()