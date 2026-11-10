from fastapi import FastAPI, HTTPException

app = FastAPI()


tasks = [
    {"id" : "1", "title" : "Refactor code", "done" : True},
    {"id" : "2", "title" : "Learn Mandarin", "done" : True},
    {"id" : "3", "title" : "Clean up laptop", "done" : False},
]

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
        if id == task["id"]:
            return {"task" : task}
    raise HTTPException(status_code=404, detail=f"task {id} not found")
