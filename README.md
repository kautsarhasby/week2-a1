# FastAPI Task Manager Backend

A lightweight, robust in-memory task management API built with **FastAPI**, designed for speed, clean validation, and seamless developer experience.

## How to Install & Run It

Make sure you have Python and `uv` installed, then run this single command sequence to set up the environment and launch the server:

```bash
uvicorn main:app --reload
```

_(Server will start live at `http://127.0.0.1:8000`)_

---

## Table of All Endpoints

| Method     | Endpoint      | Description                               | Status Codes                                 |
| :--------- | :------------ | :---------------------------------------- | :------------------------------------------- |
| **GET**    | `/`           | Retrieve information of the app           | `200 OK`                                     |
| **GET**    | `/health`     | Check health of the app                   | `200 OK`                                     |
| **GET**    | `/tasks`      | Retrieve all tasks from memory            | `200 OK`                                     |
| **GET**    | `/tasks/{id}` | Retrieve task by id                       | `200 OK` , `404 Not Found`                   |
| **POST**   | `/tasks`      | Create a new task item                    | `201 Created`, `400 Bad Request`             |
| **PUT**    | `/tasks/{id}` | Update an existing task (partial or full) | `200 OK`, `400 Bad Request`, `404 Not Found` |
| **DELETE** | `/tasks/{id}` | Delete a task by its ID                   | `200 OK`, `404 Not Found`                    |

<img width="1463" height="573" alt="image" src="https://github.com/user-attachments/assets/287c80b1-9ba8-4630-a69d-c7e39e1c462a" />

---

## Sample `curl -i` Output

**Request:**

```bash
curl -i -X POST http://127.0.0.1:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"Buy milk"}'
```

**Response:**

```http
HTTP/1.1 201 Created
date: Tue, 10 Nov 2026 11:00:00 GMT
server: uvicorn
content-type: application/json
content-length: 34

{"id":1,"title":"Buy milk","done":false}
```

---

## Swagger UI Documentation

Access the built-in interactive documentation instantly in your browser:
🔗 **[http://localhost:8000/docs](http://localhost:8000/docs)**

## The Mortality experiment

**To do**: create a few tasks, restart your server, GET /tasks .

**Result and Reason** : The task disappear because didnt have any database, the tasks only saved on memory and its temporary. If the server restart or down, the data will disappear

## AI vs Me: Code Comparison & Retrospective

Using `git diff --no-index` to compare my initial implementation against the AI-generated single-file `main.py`, here is how they stack up:

### What did the AI do better — and do you understand its version well enough to explain it?

The AI structured the Pydantic validation models much cleaner (`TaskCreate` and `TaskUpdate`) and implemented robust query-string parsing that cleanly handles both `done` filtering and text `search` simultaneously. Yes, I fully understand its version—it uses Python list comprehensions and clean HTTP status code enums (`status.HTTP_201_CREATED`, etc.) which make the code production-ready and easy to read.

### What did it get wrong or quietly ignore from your prompt?

The AI followed every instruction accurately and included proper status codes (`201`, `204`, `400`, `404`), successfully omitting any unwanted persistence layer and sticking purely to in-memory storage as requested.

### What did your prompt forget to specify — and what did the AI silently decide for you?

My prompt forgot to specify how `id` auto-incrementing should behave after multiple deletions or resets. The AI silently decided to use `max((t["id"] for t in tasks), default=0) + 1`, which smartly prevents ID collision issues if items are added after deletions.

---

**Rematch Improvement:** Improved the prompt by explicitly requesting dynamic ID increment logic upfront, resulting in an even more robust single-pass implementation.

#### Personal Prompt

Help me build the same project using FastAPI as the main backend stack, and use Swagger UI for API endpoint documentation. Ensure the FastAPI application has explicit status codes for every endpoint function and performs incoming request validation. Create these essential endpoints:

- Get all tasks
- Get project description
- Get application health status
- Create a new task
- Delete a task
- Update a task
- Search and filter tasks
- Get total task statistics

Keep everything in a single `main_ai.py` file for easy maintenance.

### Database Direct-Query Check

Executed `SELECT * FROM tasks WHERE done = 1;` directly on `tasks.db`, which returned only the completed task rows matching the exact JSON items served by `GET /tasks?done=true`.
