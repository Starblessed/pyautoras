from fastapi import FastAPI
from celery.result import AsyncResult
from worker.tasks import create_session, logout_session

app = FastAPI(title="AutoRAS API")

@app.get("/health")
def get_health():
    return {"status": "ok"}

@app.post("/create")
def create_ras():
    task = create_session.delay() 
    return {"task_id": task.id}   

@app.get("/{task_id}/status")
def get_status(task_id: str):
    task_result = AsyncResult(task_id)
    return {"task_id": task_id,
            "status": task_result.status,
            "result": task_result.result if task_result.ready() else None
            }

@app.post("/{task_id}/close")
def close_ras(task_id: str):
    logout_session.delay(task_id)
    return {"message": f"Logout signal sent for task {task_id}"}
