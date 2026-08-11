# Task API

A simple task-management REST API built with **FastAPI**. Supports creating, listing, filtering, updating, and deleting tasks, plus basic stats — all backed by an in-memory list (no database).

## Requirements

- Python 3.9+
- FastAPI
- Uvicorn (ASGI server)

```bash
pip install fastapi uvicorn
```

## Running the app

```bash
uvicorn main:app --reload
```

Then visit:
- API base: `http://127.0.0.1:8000`
- Interactive docs (Swagger UI): `http://127.0.0.1:8000/docs`

## Data model

Each task looks like this:

```json
{
  "id": 1,
  "Title": "Do Assignment",
  "done": false
}
```

> Note: the `Title` field is capitalized to match the Pydantic model used throughout the project.

## Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/` | API info |
| GET | `/tasks/` | List all tasks |
| GET | `/tasks/{task_id}` | Get a single task by ID |
| GET | `/get-by-title-or-done` | Filter tasks by `Title` and/or `done` (query params) |
| POST | `/create-task/` | Create a new task |
| PATCH | `/update-task/{task_id}` | Partially update a task (only send the fields you want to change) |
| DELETE | `/delete-task/{task_id}` | Delete a task by ID |
| GET | `/stats/` | Task counts: total / done / pending |

### GET `/tasks/{task_id}`

Path parameter `task_id` must be an integer `> 0`. Returns `404` if not found.

### GET `/get-by-title-or-done`

Query parameters (both optional):

- `Title` (string)
- `done` (boolean)

Example:

```
GET /get-by-title-or-done?Title=Do Assignment
GET /get-by-title-or-done?done=false
```

Returns `404` if no tasks match.

### POST `/create-task/`

Body:

```json
{
  "id": 2,
  "Title": "New Task",
  "done": false
}
```

Returns `400` if a task with the same `Title` already exists.

### PATCH `/update-task/{task_id}`

Body — send **only** the fields you want to change:

```json
{
  "done": true
}
```

Uses `model_dump(exclude_unset=True)` so omitted fields are left untouched. Returns `404` if the task doesn't exist.

### DELETE `/delete-task/{task_id}`

Deletes the task with the matching `id`. Returns `404` if not found.

### GET `/stats/`

```json
{
  "total": 3,
  "done": 1,
  "pending": 2
}
```

## Notes for contributors

- Storage is a plain Python list (`tasks`) — data resets every time the server restarts.
- Filtering via query params (`/get-by-title-or-done`) uses `Depends()` with a Pydantic model. Because of how FastAPI resolves query-param dependencies, filtering relies on excluding `None` values (`if v is not None`) rather than `exclude_unset`, which isn't reliable in that context.
- `PATCH` (not `PUT`) is used for updates since the endpoint supports partial updates.
