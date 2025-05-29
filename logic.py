# logic.py
from datetime import datetime, timedelta

def parse_task_message(text):
    if "до" in text:
        parts = text.split("до")
        task_text = parts[0].strip()
        due_str = parts[1].strip()
        try:
            due_date = datetime.strptime(due_str, "%d.%m.%Y").strftime("%Y-%m-%d")
            return {"text": task_text, "due_date": due_date}
        except:
            return None
    return None

def task_summary(tasks, monday_mode=False):
    if not tasks:
        return "Нет текущих задач."
    summary = """📝 Текущие задачи:
              - Задача 1
              - Задача 2
              """

    now = datetime.now()
    for tid, text, due, status in tasks:
        due_dt = datetime.strptime(due, "%Y-%m-%d")
        overdue = due_dt < now
        if monday_mode and not overdue:
            continue
        status_note = "🔴 Просрочена" if overdue else "🟢 В работе"
        summary += f"- {text} (до {due}) [{status_note}]"
    return summary