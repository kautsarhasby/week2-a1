from datetime import datetime, timezone
from fastapi import HTTPException, status
from config import database
from models import task_model


def create_task(task: task_model.CreateTask):
    if not task.title or not task.title.strip():
        raise HTTPException(status_code=400, detail="Title cannot be empty")

    now = datetime.now(timezone.utc).isoformat()
    with database.get_db() as conn:
        row = conn.execute(
            """
            INSERT INTO tasks (title, done, created_at, updated_at)
            VALUES (%s, %s, %s, %s)
            RETURNING id, title, done, created_at, updated_at
            """,
            (task.title.strip(), bool(task.done), now, now),
        ).fetchone()
        conn.commit()

    return row


def get_tasks(done: str | None = None, search: str | None = None):
    with database.get_db() as conn:
        if done is not None:
            if done.lower() == "true":
                is_done = True
            elif done.lower() == "false":
                is_done = False
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Query 'done' must be 'true' or 'false'",
                )
            return conn.execute(
                "SELECT id, title, done, created_at, updated_at FROM tasks WHERE done = %s ORDER BY title",
                (is_done,),
            ).fetchall()

        if search is not None:
            return conn.execute(
                "SELECT id, title, done, created_at, updated_at FROM tasks WHERE title ILIKE %s ORDER BY title",
                (f"%{search}%",),
            ).fetchall()

        return conn.execute(
            "SELECT id, title, done, created_at, updated_at FROM tasks ORDER BY title"
        ).fetchall()


def get_task_by_id(id: str):
    with database.get_db() as conn:
        row = conn.execute("SELECT * FROM tasks WHERE id = %s", (int(id),)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail=f"task {id} not found")
    return {
        "id": row["id"],
        "title": row["title"],
        "done": bool(row["done"]),
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def update_task(id: int, task: task_model.UpdateTask):
    if task.title is not None and not task.title.strip():
        raise HTTPException(status_code=400, detail="Title cannot be empty")

    with database.get_db() as conn:
        row = conn.execute("SELECT * FROM tasks WHERE id = %s", (id,)).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail=f"task {id} not found")

        new_title = task.title.strip() if task.title is not None else row["title"]
        new_done = bool(task.done) if task.done is not None else row["done"]
        now = datetime.now(timezone.utc).isoformat()

        updated_row = conn.execute(
            """
            UPDATE tasks
            SET title = %s, done = %s, updated_at = %s
            WHERE id = %s
            RETURNING id, title, done, created_at, updated_at
            """,
            (new_title, new_done, now, id),
        ).fetchone()
        conn.commit()

    return updated_row


def delete_task(id: str):
    with database.get_db() as conn:
        cursor = conn.execute("DELETE FROM tasks WHERE id = %s", (id,))
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail=f"task {id} not found")


def get_stats():
    with database.get_db() as conn:
        total = conn.execute("SELECT COUNT(*) AS count FROM tasks").fetchone()["count"]
        done = conn.execute("SELECT COUNT(*) AS count FROM tasks WHERE done = TRUE").fetchone()["count"]
        open_tasks = conn.execute("SELECT COUNT(*) AS count FROM tasks WHERE done = FALSE").fetchone()["count"]
    return {"total": total, "done": done, "open": open_tasks}


def reset_tasks():
    with database.get_db() as conn:
        conn.execute("DELETE FROM tasks")
        conn.commit()

    database.init_db()

    with database.get_db() as conn:
        rows = conn.execute("SELECT id, title, done FROM tasks").fetchall()

    tasks_list = [{"id": r["id"], "title": r["title"], "done": bool(r["done"])} for r in rows]
    return {"message": "Tasks has been reset", "task": tasks_list}