from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Task, Project, User, Priority
from app.core.security import decode_token
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import Optional
from transformers import pipeline

router = APIRouter(prefix="/tasks", tags=["tasks"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Load NLP model once when server starts
print("Loading NLP model... this takes ~30 seconds on first run")
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
print("NLP model loaded!")

PRIORITY_LABELS = ["low priority", "medium priority", "high priority", "critical priority"]

def get_priority_from_nlp(text: str) -> Priority:
    result = classifier(text, PRIORITY_LABELS)
    top_label = result["labels"][0]
    if "critical" in top_label:
        return Priority.critical
    elif "high" in top_label:
        return Priority.high
    elif "medium" in top_label:
        return Priority.medium
    else:
        return Priority.low

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter(User.id == payload["sub"]).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None

@router.post("/{project_id}/tasks")
def create_task(
    project_id: str,
    payload: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check project exists and belongs to user
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.owner_id == current_user.id
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Use NLP to assign priority
    text = f"{payload.title}. {payload.description or ''}"
    priority = get_priority_from_nlp(text)

    task = Task(
        title=payload.title,
        description=payload.description,
        priority=priority,
        project_id=project_id
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    return {
        "id": str(task.id),
        "title": task.title,
        "description": task.description,
        "priority": task.priority,
        "completed": task.completed,
        "ai_assigned_priority": True
    }

@router.get("/{project_id}/tasks")
def get_tasks(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.owner_id == current_user.id
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    tasks = db.query(Task).filter(Task.project_id == project_id).all()
    return [
        {
            "id": str(t.id),
            "title": t.title,
            "description": t.description,
            "priority": t.priority,
            "completed": t.completed
        }
        for t in tasks
    ]

@router.patch("/{project_id}/tasks/{task_id}")
def update_task(
    project_id: str,
    task_id: str,
    payload: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    task = db.query(Task).filter(Task.id == task_id, Task.project_id == project_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if payload.title is not None:
        task.title = payload.title
    if payload.description is not None:
        task.description = payload.description
    if payload.completed is not None:
        task.completed = payload.completed

    db.commit()
    db.refresh(task)
    return {"id": str(task.id), "title": task.title, "completed": task.completed, "priority": task.priority}