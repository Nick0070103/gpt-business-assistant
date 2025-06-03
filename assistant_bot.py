import logging
import sqlite3
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)
db_path = "memory.db"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Ассистент готов! Используйте /addtask, /tasks, /event")

async def add_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        text = ' '.join(context.args)
        if not text:
            await update.message.reply_text("Укажите задачу после команды.")
            return
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("INSERT INTO tasks (description) VALUES (?)", (text,))
        conn.commit()
        conn.close()
        await update.message.reply_text("Задача добавлена.")
    except Exception as e:
        logging.error(e)
        await update.message.reply_text("Ошибка при добавлении задачи.")

async def list_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT id, description, status FROM tasks")
    rows = cur.fetchall()
    conn.close()
    if rows:
        text = "\n".join([f"{r[0]}. {r[1]} — {r[2]}" for r in rows])
    else:
        text = "Задач нет."
    await update.message.reply_text(text)

async def save_event(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = ' '.join(context.args)
    if not text:
        await update.message.reply_text("Укажите описание события.")
        return
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("INSERT INTO events (timestamp, event) VALUES (datetime('now'), ?)", (text,))
    conn.commit()
    conn.close()
    await update.message.reply_text("Событие сохранено.")

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("addtask", add_task))
    app.add_handler(CommandHandler("tasks", list_tasks))
    app.add_handler(CommandHandler("event", save_event))
    app.run_polling()
