from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, parse_uuid
from app.database import get_db
from app.models.models import Priority, Project, Task, User

router = APIRouter(prefix="/tasks", tags=["tasks"])

PRIORITY_LABELS = ["low priority", "medium priority", "high priority", "critical priority"]
NLP_MODEL = "facebook/bart-large-mnli"

_classifier = None


def _get_classifier():
    """Load the zero-shot model on first use rather than at import time,
    so tests and tooling can import the app without downloading it."""
    global _classifier
    if _classifier is None:
        from transformers import pipeline

        _classifier = pipeline("zero-shot-classification", model=NLP_MODEL)
    return _classifier


def get_priority_from_nlp(text: str) -> Priority:
    result = _get_classifier()(text, PRIORITY_LABELS)
    top_label = result["labels"][0]
    if "critical" in top_label:
        return Priority.critical
    if "high" in top_label:
        return Priority.high
    if "medium" in top_label:
        return Priority.medium
    return Priority.low


def _owned_project(project_id: str, user: User, db: Session) -> Project:
    project = db.query(Project).filter(
        Project.id == parse_uuid(project_id, "Project"),
        Project.owner_id == user.id,
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


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
    db: Session = Depends(get_db),
):
    project = _owned_project(project_id, current_user, db)

    text = f"{payload.title}. {payload.description or ''}"
    priority = get_priority_from_nlp(text)

    task = Task(
        title=payload.title,
        description=payload.description,
        priority=priority,
        project_id=project.id,
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
        "ai_assigned_priority": True,
    }


@router.get("/{project_id}/tasks")
def get_tasks(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    project = _owned_project(project_id, current_user, db)
    tasks = db.query(Task).filter(Task.project_id == project.id).all()
    return [
        {
            "id": str(t.id),
            "title": t.title,
            "description": t.description,
            "priority": t.priority,
            "completed": t.completed,
        }
        for t in tasks
    ]


@router.patch("/{project_id}/tasks/{task_id}")
def update_task(
    project_id: str,
    task_id: str,
    payload: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Previously this looked the task up by id and project id only, so any
    # logged-in user could edit another user's task. Check ownership first.
    project = _owned_project(project_id, current_user, db)
    task = db.query(Task).filter(
        Task.id == parse_uuid(task_id, "Task"),
        Task.project_id == project.id,
    ).first()
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
