from fastapi import FastAPI, HTTPException, status, Request
from contextlib import asynccontextmanager
from fastapi.exceptions import RequestValidationError
from config import database
from fastapi.responses import JSONResponse
from pydantic import BaseModel,Field
from typing import Optional
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
async def getTasks(done : str | None = None, search: str | None = None ):
    conn = database.get_db()
    if done is None and search is None:
        rows = conn.execute("SELECT * FROM tasks").fetchall()
        conn.close()
        return [{"id": r["id"], "title": r["title"], "done": bool(r["done"])} for r in rows]
    if done:
        if done == "true":
            return [task for task in tasks if task["done"] is True]
        elif done == "false":
            return [task for task in tasks if task["done"] is False]
    if search:
        return [task for task in tasks if search.lower() in task["title"].lower()]
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
        detail="Query not valid")


@app.get("/tasks/{id}", summary="Retrieve task by id")
async def getTaskById(id : str):
    conn = database.get_db()
    row = conn.execute("SELECT * FROM tasks WHERE id = ?",(id)).fetchone()
    conn.close()
    if row is None:
        raise HTTPException(status_code=404, detail=f"task {id} not found")
    return {"task": {"id": int(row["id"]), "title": row["title"], "done": bool(row["done"])}}

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
    done = []
    open = []
    for task in tasks:
        if task["done"] == True:
            done.append(task)
        else:
            open.append(task)
    return {"total" : len(tasks), "done" : len(done), "open" : len(open)}


@app.post("/reset")
async def resetTask():
    global tasks
    tasks= [
    {"id" : 1, "title" : "Refactor code", "done" : True},
    {"id" : 2, "title" : "Learn Mandarin", "done" : True},
    {"id" : 3, "title" : "Clean up laptop", "done" : False},
]
    return { "message" : "Tasks has been reset", "task" : tasks}