from fastapi import FastAPI, HTTPException, status, Request
from contextlib import asynccontextmanager
from fastapi.exceptions import RequestValidationError
from config import database
from fastapi.responses import JSONResponse
from pydantic import BaseModel,Field
from typing import Optional
from datetime import datetime, timezone

class Task(BaseModel):
    id: int
    title: str 
    done : bool = False

class CreateTask(BaseModel):
    title: str = Field(...,min_length=1,description="title cannot empty")
    done: bool = False

class UpdateTask(BaseModel):
    title: Optional[str] = Field(None,description="title optional")
    done: Optional[bool] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    database.init_db()
    yield

app = FastAPI(lifespan=lifespan)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": "Bad Request",
        },
    )

@app.post("/tasks",status_code=201, summary="Create new task")
async def postTask(task: CreateTask):
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
            (task.title.strip(), bool(task.done), now, now)
        ).fetchone()
        conn.commit()

    return row

@app.get('/', summary="Retrieve information of the app")
async def root():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}

@app.get("/health", summary="Check health of the app")
async def health():
    return {"status": "ok"}

@app.get("/tasks", summary="Retrieve list of the tasks")
async def getTasks(done: str | None = None, search: str | None = None):
    with database.get_db() as conn:
        if done is not None:
            if done.lower() == "true":
                is_done = True
            elif done.lower() == "false":
                is_done = False
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Query 'done' must be 'true' or 'false'"
                )
            rows = conn.execute(
                "SELECT id, title, done, created_at, updated_at FROM tasks WHERE done = %s ORDER BY title",
                (is_done,)
            ).fetchall()
            return rows

        if search is not None:
            rows = conn.execute(
                "SELECT id, title, done, created_at, updated_at FROM tasks WHERE title ILIKE %s ORDER BY title",
                (f"%{search}%",)
            ).fetchall()
            return rows

        rows = conn.execute(
            "SELECT id, title, done, created_at, updated_at FROM tasks ORDER BY title"
        ).fetchall()
        return rows

@app.get("/tasks/{id}", summary="Retrieve task by id")
async def getTaskById(id : str):
    with database.get_db() as conn:
        row = conn.execute("SELECT * FROM tasks WHERE id = %s",(int(id),)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail=f"task {id} not found")
    return {"id": row["id"], "title": row["title"], "done": bool(row["done"]),"created_at": row["created_at"],
            "updated_at": row["updated_at"],} 

@app.put("/tasks/{id}",summary="Update task by id")
async def updateTasks(id: int, task: UpdateTask):
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
            (new_title, new_done, now, id)
        ).fetchone()
        conn.commit()

    return updated_row

@app.delete("/tasks/{id}",status_code=204, summary="Delete task by id")
async def deleteTask(id: str):
    with database.get_db() as conn:
        cursor = conn.execute("DELETE FROM tasks WHERE id = %s", (id,))
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail=f"task {id} not found")
    

@app.get("/stats")
async def getStats():
    conn = database.get_db()
    total = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
    done = conn.execute("SELECT COUNT(*) FROM tasks WHERE done = 1").fetchone()[0]
    open_tasks = conn.execute("SELECT COUNT(*) FROM tasks WHERE done = 0").fetchone()[0]
    conn.close()
    return {"total": total, "done": done, "open": open_tasks}

@app.post("/reset")
async def resetTask():
    conn = database.get_db()
    conn.execute("DELETE FROM tasks")
    conn.commit()
    conn.close()
    database.init_db()
    
    conn = database.get_db()
    rows = conn.execute("SELECT * FROM tasks").fetchall()
    conn.close()
    tasks_list = [{"id": r["id"], "title": r["title"], "done": bool(r["done"])} for r in rows]
    return {"message": "Tasks has been reset", "task": tasks_list}