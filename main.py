from fastapi import FastAPI, status, Request, Response
from contextlib import asynccontextmanager
from fastapi.exceptions import RequestValidationError
from config import database
from fastapi.responses import JSONResponse
from models import task_model, auth_model
from services import auth_service, task_service, system_service
import os
import redis

@asynccontextmanager
async def lifespan(app: FastAPI):
    database.init_db()
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    r = redis.from_url(redis_url)
    if r.ping():
        print(f"Redis connected: PING -> PONG ({redis_url})")
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
# System
@app.get("/", summary="Retrieve information of the app")
def root():
    return system_service.get_root()

@app.get("/health", summary="Check application and database health")
def healthCheck(response: Response):
    return system_service.check_health(response)

# Auth
@app.post("/auth/signup", status_code=status.HTTP_201_CREATED)
def signup(payload: auth_model.AuthRequest):
    return auth_service.signup(payload)

@app.post("/auth/login", status_code=status.HTTP_200_OK)
def login(payload: auth_model.AuthRequest):
    return auth_service.login(payload)

# Tasks
@app.post("/tasks", status_code=201, summary="Create new task")
def postTask(task: task_model.CreateTask):
    return task_service.create_task(task)

@app.get("/tasks", summary="Retrieve list of the tasks")
def getTasks(done: str | None = None, search: str | None = None):
    return task_service.get_tasks(done, search)

@app.get("/tasks/{id}", summary="Retrieve task by id")
def getTaskById(id: str):
    return task_service.get_task_by_id(id)

@app.put("/tasks/{id}", summary="Update task by id")
def updateTasks(id: int, task: task_model.UpdateTask):
    return task_service.update_task(id, task)

@app.delete("/tasks/{id}", status_code=204, summary="Delete task by id")
def deleteTask(id: str):
    return task_service.delete_task(id)

@app.get("/stats", summary="Retrieve task statistics")
def getStats():
    return task_service.get_stats()

@app.post("/reset", summary="Reset all tasks")
def resetTask():
    return task_service.reset_tasks()