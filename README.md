# FastAPI Task Manager Backend

A lightweight, production-ready task management REST API built with **FastAPI** and **PostgreSQL** (`psycopg`), containerized with **Docker** and orchestrated via **Docker Compose**.

---

## How to Run Everything (One Command)

Make sure you have **Docker** and **Docker Compose** installed, then clone this repository, copy the environment template, and start the stack:

```bash
cp .env.example .env
docker compose up --build
```

_(The API will be live at `http://localhost:8000` and PostgreSQL will initialize automatically with 3 seeded tasks.)_

### Environment Variables

Configuration is loaded from `.env` (see **`.env.example`** for the template):

| Variable | Description | Default Value (`.env.example`) |
| :--- | :--- | :--- |
| `DATABASE_URL` | PostgreSQL connection string used by `psycopg` inside the Compose network (`db` service) | `postgresql://postgres:dev@db:5432/tasks` |

---

## Table of All Endpoints

| Method     | Endpoint      | Description                                                        | Status Codes                                 |
| :--------- | :------------ | :----------------------------------------------------------------- | :------------------------------------------- |
| **GET**    | `/`           | Retrieve application metadata                                      | `200 OK`                                     |
| **GET**    | `/health`     | Check application health status                                    | `200 OK`                                     |
| **GET**    | `/tasks`      | Retrieve all tasks from PostgreSQL (`?done=true/false`, `?search=`) | `200 OK`, `400 Bad Request`                  |
| **GET**    | `/tasks/{id}` | Retrieve a single task by ID                                       | `200 OK`, `404 Not Found`                    |
| **POST**   | `/tasks`      | Create a new task item                                             | `201 Created`, `400 Bad Request`             |
| **PUT**    | `/tasks/{id}` | Update an existing task (partial or full)                          | `200 OK`, `400 Bad Request`, `404 Not Found` |
| **DELETE** | `/tasks/{id}` | Delete a task by its ID                                            | `204 No Content`, `404 Not Found`            |

<img width="1463" height="573" alt="image" src="https://github.com/user-attachments/assets/287c80b1-9ba8-4630-a69d-c7e39e1c462a" />

---

## Sample `curl -i` Output

**Request:**

```bash
curl -i -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"Buy milk"}'
```

**Response:**

```http
HTTP/1.1 201 Created
date: Thu, 19 Nov 2026 14:00:00 GMT
server: uvicorn
content-type: application/json
content-length: 34

{"id":4,"title":"Buy milk","done":false}
```

---

## Database & Persistence (PostgreSQL + Docker Compose)

All tasks are persisted in **PostgreSQL** (`postgres` image) backed by a named Docker volume (`taskdata`), ensuring data survives container restarts (`docker compose down` followed by `docker compose up`).

### Database Verification (`\dt` & `SELECT * FROM tasks;`)

<img width="923" height="220" alt="image" src="https://github.com/user-attachments/assets/2934aa79-7b6c-4f79-b7b4-f7098e761d96" />


---

## Swagger UI Documentation

Access the built-in interactive documentation instantly in your browser:
🔗 **[http://localhost:8000/docs](http://localhost:8000/docs)**

---

## Previous Stage Notes (A1 & A2)

### The Mortality Experiment (A1 - In-Memory)

**To do**: Create a few tasks, restart your server, `GET /tasks`.

**Result and Reason**: The tasks disappeared because there was no database—the tasks were only saved in memory and were temporary. When the server restarted or went down, the data vanished.

### AI vs Me: Code Comparison & Retrospective (A1)

Using `git diff --no-index` to compare my initial implementation against the AI-generated single-file `main.py`, here is how they stack up:

#### What did the AI do better — and do you understand its version well enough to explain it?

The AI structured the Pydantic validation models much cleaner (`TaskCreate` and `TaskUpdate`) and implemented robust query-string parsing that cleanly handles both `done` filtering and text `search` simultaneously. Yes, I fully understand its version—it uses Python list comprehensions and clean HTTP status code enums (`status.HTTP_201_CREATED`, etc.) which make the code production-ready and easy to read.

#### What did it get wrong or quietly ignore from your prompt?

The AI followed every instruction accurately and included proper status codes (`201`, `204`, `400`, `404`), successfully omitting any unwanted persistence layer and sticking purely to in-memory storage as requested.

#### What did your prompt forget to specify — and what did the AI silently decide for you?

My prompt forgot to specify how `id` auto-incrementing should behave after multiple deletions or resets. The AI silently decided to use `max((t["id"] for t in tasks), default=0) + 1`, which smartly prevents ID collision issues if items are added after deletions.

**Rematch Improvement:** Improved the prompt by explicitly requesting dynamic ID increment logic upfront, resulting in an even more robust single-pass implementation.

<details>
<summary>Personal Prompt Used for AI Comparison</summary>

> Help me build the same project using FastAPI as the main backend stack, and use Swagger UI for API endpoint documentation. Ensure the FastAPI application has explicit status codes for every endpoint function and performs incoming request validation. Create these essential endpoints:
> - Get all tasks
> - Get project description
> - Get application health status
> - Create a new task
> - Delete a task
> - Update a task
> - Search and filter tasks
> - Get total task statistics
>
> Keep everything in a single `main_ai.py` file for easy maintenance.

</details>
