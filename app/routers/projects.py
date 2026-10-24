from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.deps import get_current_user, parse_uuid
from app.database import get_db
from app.models.models import Project, User
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/projects", tags=["projects"])

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None

@router.post("/")
def create_project(payload: ProjectCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    project = Project(
        name=payload.name,
        description=payload.description,
        owner_id=current_user.id
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return {"id": str(project.id), "name": project.name, "description": project.description}

@router.get("/")
def get_projects(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    projects = db.query(Project).filter(Project.owner_id == current_user.id).all()
    return [{"id": str(p.id), "name": p.name, "description": p.description} for p in projects]

@router.get("/{project_id}")
def get_project(project_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == parse_uuid(project_id, "Project"), Project.owner_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"id": str(project.id), "name": project.name, "description": project.description}