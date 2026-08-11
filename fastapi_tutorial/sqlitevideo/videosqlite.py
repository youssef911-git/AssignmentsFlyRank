import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "tasks.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            done INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    count = c.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
    if count == 0:
        c.executemany(
            "INSERT INTO tasks (title, done) VALUES (?, ?)",
            [
                ("Do Assignment", 0),
                ("Study SQLite", 0),
                ("Build CRUD API", 0),
            ],
        )
    conn.commit()
    conn.close()


def _to_task(row):
    task = dict(row)
    task["done"] = bool(task["done"])
    return task


def list_tasks(search=None, done=None, sort="id"):
    conn = get_connection()
    c = conn.cursor()
    query = "SELECT * FROM tasks"
    clauses = []
    params = []
    if search:
        clauses.append("title LIKE ?")
        params.append(f"%{search}%")
    if done is not None:
        clauses.append("done = ?")
        params.append(int(done))
    if clauses:
        query += " WHERE " + " AND ".join(clauses)
    query += " ORDER BY title" if sort == "title" else " ORDER BY id"
    rows = c.execute(query, params).fetchall()
    conn.close()
    return [_to_task(row) for row in rows]


def get_task(task_id):
    conn = get_connection()
    c = conn.cursor()
    row = c.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    conn.close()
    return _to_task(row) if row else None


def create_task(title):
    conn = get_connection()
    c = conn.cursor()
    existing = c.execute(
        "SELECT id FROM tasks WHERE title = ?", (title,)
    ).fetchone()
    if existing:
        conn.close()
        return None
    c.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", (title, 0))
    task_id = c.lastrowid
    conn.commit()
    conn.close()
    return get_task(task_id)


def update_task(task_id, title, done):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "UPDATE tasks SET title = ?, done = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
        (title, int(done), task_id),
    )
    conn.commit()
    conn.close()
    return get_task(task_id)


def get_stats():
    conn = get_connection()
    c = conn.cursor()
    total = c.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
    done = c.execute("SELECT COUNT(*) FROM tasks WHERE done = 1").fetchone()[0]
    conn.close()
    return {"total": total, "done": done, "pending": total - done}


def delete_task(task_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
