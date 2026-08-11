import os

from dotenv import load_dotenv
from psycopg import connect
from psycopg.rows import dict_row

load_dotenv()

DATABASE_URL = os.environ["DATABASE_URL"]


def get_connection():
    return connect(DATABASE_URL)


def init_db():
    conn = get_connection()
    with conn.cursor() as c:
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                done BOOLEAN NOT NULL DEFAULT FALSE,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
            """
        )
        count = c.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
        if count == 0:
            c.executemany(
                "INSERT INTO tasks (title, done) VALUES (%s, %s)",
                [
                    ("Do Assignment", False),
                    ("Study SQLite", False),
                    ("Build CRUD API", False),
                ],
            )
    conn.commit()
    conn.close()


def _to_task(row):
    return {
        "id": row["id"],
        "title": row["title"],
        "done": bool(row["done"]),
        "created_at": row["created_at"].isoformat() if row["created_at"] else None,
        "updated_at": row["updated_at"].isoformat() if row["updated_at"] else None,
    }


def list_tasks(search=None, done=None, sort="id"):
    conn = get_connection()
    query = "SELECT * FROM tasks"
    clauses = []
    params = []
    if search:
        clauses.append("title ILIKE %s")
        params.append(f"%{search}%")
    if done is not None:
        clauses.append("done = %s")
        params.append(bool(done))
    if clauses:
        query += " WHERE " + " AND ".join(clauses)
    query += " ORDER BY title" if sort == "title" else " ORDER BY id"
    with conn.cursor(row_factory=dict_row) as c:
        rows = c.execute(query, params).fetchall()
    conn.close()
    return [_to_task(row) for row in rows]


def get_task(task_id):
    conn = get_connection()
    with conn.cursor(row_factory=dict_row) as c:
        row = c.execute("SELECT * FROM tasks WHERE id = %s", (task_id,)).fetchone()
    conn.close()
    return _to_task(row) if row else None


def create_task(title):
    conn = get_connection()
    with conn.cursor(row_factory=dict_row) as c:
        existing = c.execute(
            "SELECT id FROM tasks WHERE title = %s", (title,)
        ).fetchone()
        if existing:
            conn.close()
            return None
        row = c.execute(
            "INSERT INTO tasks (title, done) VALUES (%s, %s) RETURNING *",
            (title, False),
        ).fetchone()
        task = _to_task(row)
    conn.commit()
    conn.close()
    return task


def update_task(task_id, title, done):
    conn = get_connection()
    with conn.cursor(row_factory=dict_row) as c:
        row = c.execute(
            "UPDATE tasks SET title = %s, done = %s, updated_at = NOW() WHERE id = %s RETURNING *",
            (title, bool(done), task_id),
        ).fetchone()
        task = _to_task(row) if row else None
    conn.commit()
    conn.close()
    return task


def get_stats():
    conn = get_connection()
    with conn.cursor() as c:
        total = c.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
        done = c.execute("SELECT COUNT(*) FROM tasks WHERE done = TRUE").fetchone()[0]
    conn.close()
    return {"total": total, "done": done, "pending": total - done}


def delete_task(task_id):
    conn = get_connection()
    with conn.cursor() as c:
        c.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
    conn.commit()
    conn.close()
