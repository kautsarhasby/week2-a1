from fastapi import FastAPI, HTTPException, status, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel,Field

app = FastAPI()


class Task(BaseModel):
    id: int
    title: str 
    done : bool = False

class CreateTask(BaseModel):
    title: str = Field(...,min_length=1,description="title cannot empty")

class UpdateTask(BaseModel):
    title: str = Field(...,min_length=1,description="title cannot empty")
    done: bool = Field(...,description="done cannot empty")

tasks: Task = [
    {"id" : 1, "title" : "Refactor code", "done" : True},
    {"id" : 2, "title" : "Learn Mandarin", "done" : True},
    {"id" : 3, "title" : "Clean up laptop", "done" : False},
]

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": "Bad Request",
        },
    )

@app.post("/tasks",status_code=201)
async def postTask(body : CreateTask):
    tasks.append({
        "id" : len(tasks)+1,
        "title" : body.title,
        "done" : False
    })
    return tasks

@app.get('/')
async def root():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/tasks")
async def getTasks():
    return tasks

@app.get("/tasks/{id}")
async def getTasks(id : str):
    for task in tasks:
        if int(id) == task["id"]:
            return {"task" : task}
    raise HTTPException(status_code=404, detail=f"task {id} not found")

@app.put("/tasks/{id}")
async def updateTasks(id: str,body : UpdateTask):
    for task in tasks:
        if int(id) == task["id"]:
            task["title"] = body.title
            task["done"] = body.done
            return {"task" : task, "message":"updated task"}
    raise HTTPException(status_code=404, detail=f"Unknown {id}")

@app.delete("/tasks/{id}",status_code=204)
async def deleteTasks(id: str):
    for index, task in enumerate(tasks):
        if int(id) == task["id"]:
            tasks.pop(index)
            return
    raise HTTPException(status_code=404, detail=f"Unknown {id}")