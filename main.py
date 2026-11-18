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
async def postTask(task : CreateTask):
    if not task.title.strip():
        raise HTTPException(status_code=400, detail="Title cannot be empty")
    conn = database.get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tasks (title, done) VALUES (?, ?)",
        (task.title.strip(), int(task.done)) 
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return {"id": new_id, "title": task.title.strip(), "done": task.done}

@app.get('/', summary="Retrieve information of the app")
async def root():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}

@app.get("/health", summary="Check health of the app")
async def health():
    return {"status": "ok"}

@app.get("/tasks", summary="Retrieve list of the tasks")
async def getTasks(done: str | None = None, search: str | None = None):
    conn = database.get_db()
    if done is None and search is None:
        rows = conn.execute("SELECT * FROM tasks ORDER BY title").fetchall()
        conn.close()
        return [{"id": r["id"], "title": r["title"], "done": bool(r["done"]),"created_at": r["created_at"],
                "updated_at": r["updated_at"],} for r in rows]
    if done is not None:
            rows = conn.execute("SELECT * FROM tasks WHERE done = ? ORDER BY title",(int(bool(done)),)).fetchall()
            conn.close()
            return [{"id": r["id"], "title": r["title"], "done": bool(r["done"]),"created_at": r["created_at"],
        "updated_at": r["updated_at"],} for r in rows]
    if search is not None:
        rows = conn.execute("SELECT * FROM tasks WHERE LOWER(title) LIKE ? ORDER BY title", (f"%{search.lower()}%",)).fetchall()
        conn.close()
        return [{"id": r["id"], "title": r["title"], "done": bool(r["done"]),"created_at": r["created_at"],
                "updated_at": r["updated_at"],} for r in rows]
    conn.close()
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Query not valid"
    )


@app.get("/tasks/{id}", summary="Retrieve task by id")
async def getTaskById(id : str):
    conn = database.get_db()
    row = conn.execute("SELECT * FROM tasks WHERE id = ?",(id)).fetchone()
    conn.close()
    if row is None:
        raise HTTPException(status_code=404, detail=f"task {id} not found")
    return [{"id": r["id"], "title": r["title"], "done": bool(r["done"]),"created_at": r["created_at"],
            "updated_at": r["updated_at"],} for r in row]

@app.put("/tasks/{id}",summary="Update task by id")
async def updateTasks(id: str,task : UpdateTask):
    conn = database.get_db()
    row = conn.execute("SELECT * FROM tasks WHERE id = ?", [id]).fetchone()

    if row is None:
        conn.close()
        raise HTTPException(status_code=404, detail=f"task {id} not found")

    if task.title is not None and not task.title.strip():
        conn.close()
        raise HTTPException(status_code=400, detail="Title cannot be empty")

    new_title = task.title.strip() if task.title is not None else row["title"]
    new_done = int(task.done) if task.done is not None else row["done"]
    conn.execute(
        "UPDATE tasks SET title = ?, done = ? WHERE id = ?",
        [new_title, new_done, id]
    )
    conn.commit()
    conn.close()

    return {
        "task": {"id": id, "title": new_title, "done": bool(new_done)},
        "message": "updated task"
    }

@app.delete("/tasks/{id}",status_code=204, summary="Delete task by id")
async def deleteTask(id: str):
    conn = database.get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = ?",(int(id),))
    conn.commit()
    conn.close()
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