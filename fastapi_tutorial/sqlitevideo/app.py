from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel

import repository


@asynccontextmanager
async def lifespan(app: FastAPI):
    repository.init_db()
    yield


app = FastAPI(lifespan=lifespan)


class TaskIn(BaseModel):
    title: str = ""


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None


def _error(status_code: int, message: str) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"error": message})


@app.get("/tasks")
def read_tasks(
    search: Optional[str] = None,
    done: Optional[bool] = None,
    sort: Optional[str] = None,
):
    return repository.list_tasks(search=search, done=done, sort=sort)


@app.get("/tasks/{task_id}")
def read_task(task_id: int):
    task = repository.get_task(task_id)
    if task is None:
        return _error(404, "Task not found")
    return task


@app.post("/tasks", status_code=201)
def create_task(task: TaskIn):
    title = task.title.strip()
    if not title:
        return _error(400, "Title is required")
    created = repository.create_task(title)
    if created is None:
        return _error(400, "Task already exists")
    return created


@app.get("/stats")
def stats():
    return repository.get_stats()


@app.put("/tasks/{task_id}")
def update_task(task_id: int, task: TaskUpdate):
    current = repository.get_task(task_id)
    if current is None:
        return _error(404, "Task not found")
    title = task.title.strip() if task.title is not None else current["title"]
    if not title:
        return _error(400, "Title is required")
    done = task.done if task.done is not None else current["done"]
    return repository.update_task(task_id, title, done)


@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    if repository.get_task(task_id) is None:
        return _error(404, "Task not found")
    repository.delete_task(task_id)
    return Response(status_code=204)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
