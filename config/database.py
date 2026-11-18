import sqlite3
from datetime import datetime, timezone

DB_NAME = "tasks.db"

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            done INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)

    cursor.execute("SELECT COUNT(*) FROM tasks")
    count = cursor.fetchone()[0]

    if count == 0:
        now = datetime.now(timezone.utc).isoformat()
        sample_tasks = [
            ("Clean up laptop", 1, now, now),
            ("Clean up house", 0, now, now),
            ("Learn Mandarin", 1, now, now)
        ]
        cursor.executemany(
            "INSERT INTO tasks (title, done, created_at, updated_at) VALUES (?, ?, ?, ?)",
            sample_tasks
        )
    conn.commit()
    conn.close()