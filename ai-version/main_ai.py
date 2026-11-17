from typing import Optional
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

app = FastAPI(
    title="Task Management API",
    description="A lightweight in-memory task management backend built with FastAPI.",
    version="1.0.0"
)

# In-memory storage (temporary database)
tasks = [
    {"id": 1, "title": "Clean House", "done": True},
    {"id": 2, "title": "Learn English", "done": True},
    {"id": 3, "title": "Wash dish", "done": False},
]

# Pydantic Models for Request Validation
class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, description="Task title cannot be empty")

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, description="Optional task title")
    done: Optional[bool] = Field(None, description="Optional done status")


# 1. Get project information / root
@app.get("/", summary="Retrieve application information", status_code=status.HTTP_200_OK)
async def root():
    return {
        "name": "Task API",
        "version": "1.0.0",
        "description": "Backend API for managing tasks with FastAPI",
        "endpoints": ["/tasks", "/health", "/stats", "/reset"]
    }


# 2. Get application health status
@app.get("/health", summary="Check application health", status_code=status.HTTP_200_OK)
async def health():
    return {"status": "ok"}


# 3. Get total task statistics
@app.get("/stats", summary="Get task statistics", status_code=status.HTTP_200_OK)
async def get_stats():
    total = len(tasks)
    done_count = sum(1 for task in tasks if task["done"] is True)
    open_count = total - done_count
    return {
        "total": total,
        "done": done_count,
        "open": open_count
    }


# 4. Get all tasks (with optional search & filtering)
@app.get("/tasks", summary="Retrieve list of tasks with optional filters", status_code=status.HTTP_200_OK)
async def get_tasks(done: Optional[str] = None, search: Optional[str] = None):
    result = tasks

    # Filter by 'done' status (true/false)
    if done is not None:
        if done.lower() == "true":
            result = [t for t in result if t["done"] is True]
        elif done.lower() == "false":
            result = [t for t in result if t["done"] is False]
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Query parameter 'done' must be either 'true' or 'false'."
            )

    # Filter by search keyword in title
    if search is not None:
        result = [t for t in result if search.lower() in t["title"].lower()]

    return result


# 5. Get a specific task by ID
@app.get("/tasks/{id}", summary="Retrieve task by ID", status_code=status.HTTP_200_OK)
async def get_task_by_id(id: int):
    for task in tasks:
        if task["id"] == id:
            return {"task": task}
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Task with ID {id} not found."
    )


# 6. Create a new task
@app.post("/tasks", summary="Create a new task", status_code=status.HTTP_201_CREATED)
async def create_task(body: TaskCreate):
    new_id = max((t["id"] for t in tasks), default=0) + 1
    new_task = {
        "id": new_id,
        "title": body.title,
        "done": False
    }
    tasks.append(new_task)
    return {"message": "Task successfully created", "task": new_task}


# 7. Update an existing task (supports partial updates)
@app.put("/tasks/{id}", summary="Update task by ID", status_code=status.HTTP_200_OK)
async def update_task(id: int, body: TaskUpdate):
    for task in tasks:
        if task["id"] == id:
            if body.title is not None:
                task["title"] = body.title
            if body.done is not None:
                task["done"] = body.done
            return {"message": "Task successfully updated", "task": task}
            
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Task with ID {id} not found."
    )


# 8. Delete a task
@app.delete("/tasks/{id}", summary="Delete task by ID", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(id: int):
    for index, task in enumerate(tasks):
        if task["id"] == id:
            tasks.pop(index)
            return
            
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Task with ID {id} not found."
    )


# Bonus: Reset/Seed data for testing & demonstrations
@app.post("/reset", summary="Reset tasks to initial seed data", status_code=status.HTTP_200_OK)
async def reset_tasks():
    global tasks
    tasks = [
        {"id": 1, "title": "Refactor code", "done": True},
        {"id": 2, "title": "Learn Mandarin", "done": True},
        {"id": 3, "title": "Clean up laptop", "done": False},
    ]
    return {"message": "Tasks have been reset to initial state", "tasks": tasks}