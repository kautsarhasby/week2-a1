import os
from datetime import datetime, timezone
import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def get_db():
    return psycopg.connect(DATABASE_URL, row_factory=dict_row)

def init_db():
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id SERIAL PRIMARY KEY,
                    title TEXT NOT NULL,
                    done BOOLEAN NOT NULL DEFAULT FALSE,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)

            cursor.execute("SELECT COUNT(*) AS count FROM tasks")
            count = cursor.fetchone()["count"]

            if count == 0:
                now = datetime.now(timezone.utc).isoformat()
                sample_tasks = [
                    ("Clean up laptop", True, now, now),
                    ("Clean up house", False, now, now),
                    ("Learn Mandarin", True, now, now)
                ]
                cursor.executemany(
                    "INSERT INTO tasks (title, done, created_at, updated_at) VALUES (%s, %s, %s, %s)",
                    sample_tasks
                )
        conn.commit()