from fastapi import FastAPI, Path, HTTPException, Depends
from typing import Optional
from pydantic import BaseModel

app = FastAPI()

# Standardized dictionary keys to match the Pydantic model casing (Title, done)
tasks = [{"id": 1, "Title": "Do Assignment", "done": False}]

class Task(BaseModel):
    id: int
    Title: str
    done: bool

class UpdateTask(BaseModel):
    Title: Optional[str] = None
    done: Optional[bool] = None

@app.get("/")
def index():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}
@app.get("/health")
def index():
    return {"status": "ok"}

@app.get("/tasks/")
def get_all_tasks():
    return tasks

@app.get("/tasks/{task_id}")
def get_task_by_id(task_id: int = Path(..., description="The ID of the task you want to view", gt=0)):
    for i in tasks:
        if i["id"] == task_id:
            return i
    # FIX: Moved outside the loop. Also, use HTTPException instead of returning a dict for errors.
    raise HTTPException(status_code=404, detail="Task not found")

@app.get("/get-by-title-or-done")
def filter_tasks(filters: UpdateTask = Depends()):
    filtered_tasks = tasks
    active_filters = {k: v for k, v in filters.model_dump().items() if v is not None}

    for field_name, field_value in active_filters.items():
        filtered_tasks = [t for t in filtered_tasks if t.get(field_name) == field_value]

    if not filtered_tasks:
        raise HTTPException(status_code=404, detail="No tasks found")
    return filtered_tasks

@app.post("/create-task/", status_code=201) # FIX: Removed redundant {title} from path, added status_code
def create_task(task: Task):
    for i in tasks:
        if i["Title"] == task.Title: # FIX: Matched casing ("Title" not "title")
            raise HTTPException(status_code=400, detail="Task already exists")
            
    tasks.append(task.model_dump()) # FIX: Convert Pydantic model to dictionary before appending
    return {"Status": "Created", "task": task.model_dump()}

@app.patch("/update-task/{task_id}")
def update_task(task_id: int, task_update: UpdateTask):
    for task in tasks:
        if task["id"] == task_id:
            update_data = task_update.model_dump(exclude_unset=True) 
            for key, value in update_data.items():
                task[key] = value   
            return task      
            
    raise HTTPException(status_code=404, detail="Task not found")

@app.delete("/delete-task/{task_id}")
def delete_task(task_id: int):
    # FIX: Rewrote loop to prevent variable shadowing and correctly delete by ID, not index
    for i in range(len(tasks)):
        if tasks[i]["id"] == task_id:
            del tasks[i]
            return {"Message": "Task deleted successfully"}
            
    raise HTTPException(status_code=404, detail="Task not found")

@app.get("/stats/")
def stats():
    done_count = 0
    pending_count = 0 # FIX: Renamed 'open' to 'pending' (open is a reserved Python keyword)
    
    for i in tasks:
        if i["done"] == False: # FIX: Changed tasks["done"] to i["done"]
            pending_count += 1
        else:
            done_count += 1
            
    return {"total": len(tasks), "done": done_count, "pending": pending_count}