# Task API — SQLite edition

A FastAPI task manager whose CRUD endpoints are backed by a real SQLite database.
This is the sequel to Assignment 1: the API behaves exactly the same, but data now
survives a server restart because it lives on disk instead of in memory.

## Why SQLite?

- **Single file** — the whole database is one file, `tasks.db`. Easy to copy, back up, or inspect.
- **Zero setup** — no database server to install or run. It is created automatically the first time the app starts.
- **Survives restarts** — data is written to disk, so it is still there after the server stops and starts again.
- **Good fit here** — a small API with one table does not need a full database server like Postgres.

## Where the database lives

The database file is `tasks.db`, created automatically in this folder the first time the app runs
(the `tasks` table and three example tasks are seeded only when the table is empty).
It is git-ignored, so every fresh clone starts with a brand-new database — no manual setup.

## How to run

```bash
pip install -r requirements.txt
uvicorn app:app --reload
```

Then open http://127.0.0.1:8000/docs — or hit the API directly:

```
GET    /tasks              list all tasks
GET    /tasks/{id}         get one task
POST   /tasks              create a task          {"title": "..."}
PUT    /tasks/{id}         update a task          {"title": "...", "done": true} (either field optional)
DELETE /tasks/{id}         delete a task
GET    /stats              task counts
```

Optional extras: `GET /tasks?search=milk`, `GET /tasks?done=true`, `GET /tasks?sort=title`.

The three example tasks are seeded only when the table is empty — restarting never duplicates them.
To start completely fresh, delete `tasks.db` and restart the server.

## Screenshot — the database in DB Browser

Open `tasks.db` with [DB Browser for SQLite](https://sqlitebrowser.org/) to see the same rows the API serves:

![tasks table in DB Browser](screenshot.png)

## Example SQL

```sql
SELECT * FROM tasks WHERE done = 1;
```

This query returns every completed task (rows where the `done` column is `1`). I ran it in
DB Browser's Execute SQL tab after marking a task done through the API — the change
showed up instantly, because the API and DB Browser read the exact same file.
