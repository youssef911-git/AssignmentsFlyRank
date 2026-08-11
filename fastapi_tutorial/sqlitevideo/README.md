# Task API — containerized (Postgres + Docker)

A FastAPI task manager whose CRUD endpoints run against a real **PostgreSQL** database
in a **Docker** container. This is the third storage swap in the same repo:
**memory (A1) → SQLite (A2) → containerized Postgres (this one)** — and the API
on top never changed.

## What this is

- A Postgres database running as its own server in a container, with a named
  volume so your data survives restarts.
- A FastAPI app that talks to it via a connection string from `.env` (never hardcoded).
- One command starts the whole stack: **`docker compose up`**.

## One command to run everything

```bash
cp .env.example .env   # first time only — same keys, your real values
docker compose up
```

That builds the app image, starts Postgres, and serves the API at http://127.0.0.1:8000.
The `tasks` table and three example tasks are created automatically on first run —
seeded only when the table is empty, so restarts never duplicate them.

`docker compose down` stops the stack; `docker compose up` again brings it back —
your tasks survive because the volume keeps them.

> The `db` service isn't exposed on a host port: the app reaches it by the service
> name `db` inside the compose network, so the port doesn't conflict with anything
> on your machine.

## Configuration / secrets

Copy `.env.example` to `.env` and adjust if needed:

```
DATABASE_URL=postgres://postgres:dev@localhost:5433/tasks
```

- `.env` holds your real credentials and is **git-ignored** — never commit it.
- `.env.example` is the committed template with placeholder values.
- Inside `docker compose`, `DATABASE_URL` is overridden to use the service name `db`.

## Endpoints

| Method | Path             | Body                        | Success | Errors                    |
|--------|------------------|-----------------------------|---------|---------------------------|
| GET    | `/tasks`         | —                           | 200     | —                         |
| GET    | `/tasks/{id}`    | —                           | 200     | 404                       |
| POST   | `/tasks`         | `{"title": "..."}`          | 201     | 400 empty title / dup     |
| PUT    | `/tasks/{id}`    | `{"title": ..., "done": ...}` (either field optional) | 200 | 400, 404    |
| DELETE | `/tasks/{id}`    | —                           | 204     | 404                       |
| GET    | `/stats`         | —                           | 200     | —                         |

Extras: `GET /tasks?search=milk`, `GET /tasks?done=true`, `GET /tasks?sort=title`.

## Example — one `curl -i`

```bash
curl -i http://127.0.0.1:8000/tasks
```

```
HTTP/1.1 200 OK
date: Tue, 11 Aug 2026 12:09:00 GMT
server: uvicorn
content-length: 427
content-type: application/json

[{"id":1,"title":"Do Assignment","done":false,"created_at":"2026-08-11T12:08:04.261681+00:00","updated_at":"2026-08-11T12:08:04.261681+00:00"},{"id":2,"title":"Study SQLite","done":false,"created_at":"2026-08-11T12:08:04.261681+00:00","updated_at":"2026-08-11T12:08:04.261681+00:00"},{"id":3,"title":"Build CRUD API","done":false,"created_at":"2026-08-11T12:08:04.261681+00:00","updated_at":"2026-08-11T12:08:04.261681+00:00"}]
```

## The data in the database

See the same rows Postgres is serving:

```bash
docker compose exec db psql -U postgres -d tasks -c "\dt"
docker compose exec db psql -U postgres -d tasks -c "SELECT * FROM tasks;"
```

![tasks in the database](screenshot-db.png)

## Repository layout

- `app.py` — the FastAPI routes (unchanged across all three storage swaps).
- `repository.py` — the one module that talks to the database; swapping storage
  only ever touches this file.
- `Dockerfile` — builds the app image.
- `compose.yaml` — the two services (`api` + `db`) and the named volume.
- `.env` / `.env.example` — secrets and their template.
