# FastAPI Task Manager Backend

A lightweight, robust in-memory task management API built with **FastAPI**, designed for speed, clean validation, and seamless developer experience.

## How to Install & Run It

Make sure you have Python and `uv` installed, then run this single command sequence to set up the environment and launch the server:

```bash
uvicorn main:app --reload
```
*(Server will start live at `http://127.0.0.1:8000`)*

---

## Table of All Endpoints

| Method | Endpoint | Description | Status Codes |
| :--- | :--- | :--- | :--- |
| **GET** | `/` | Retrieve information of the app | `200 OK` |
| **GET** | `/health` | Check health of the app | `200 OK` |
| **GET** | `/tasks` | Retrieve all tasks from memory | `200 OK` |
| **GET** | `/tasks/{id}` | Retrieve task by id | `200 OK` , `404 Not Found` |
| **POST** | `/tasks` | Create a new task item | `201 Created`, `400 Bad Request` |
| **PUT** | `/tasks/{id}` | Update an existing task (partial or full) | `200 OK`, `400 Bad Request`, `404 Not Found` |
| **DELETE** | `/tasks/{id}` | Delete a task by its ID | `200 OK`, `404 Not Found` |

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
