# database.py
import sqlite3
from datetime import datetime

class TaskDB:
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._create()

    def _create(self):
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT,
            due_date TEXT,
            status TEXT
        )
        """)

    def add_task(self, text, due_date):
        self.conn.execute(
            "INSERT INTO tasks (text, due_date, status) VALUES (?, ?, ?)",
            (text, due_date, "в работе")
        )
        self.conn.commit()

    def get_all_tasks(self):
        return self.conn.execute("SELECT id, text, due_date, status FROM tasks").fetchall()

    def clear_tasks(self):
        self.conn.execute("DELETE FROM tasks")
        self.conn.commit()