from fastapi import HTTPException, Depends, APIRouter, Path
from sqlalchemy.orm import Session
from db.db import get_db
from lib.auth import get_current_user
from models.plan import Projects, Plans
from schema.project import ProjectResponse, CreateProject, PatchProject
from pydantic import UUID4
from lib.subscription import require_active_subscription


router = APIRouter()


@router.post("/", response_model=ProjectResponse)
def create_project(
    payload: CreateProject,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    subscription=Depends(require_active_subscription),
):

    # Check active subscription
    user_plan = db.query(Plans).filter(Plans.plan_id == subscription.plan_id).first()

    if not user_plan:
        raise HTTPException(
            status_code=404, detail="no plan exist for this subscription"
        )

    total_projects = (
        db.query(Projects).filter(Projects.user_id == current_user.user_id).count()
    )

    # check total projects < max project allowed in plan
    if total_projects >= user_plan.max_projects:
        raise HTTPException(
            status_code=403, detail="Project limit reached for your current plan"
        )

    new_project = Projects(
        user_id=current_user.user_id,
        name=payload.name,
        description=payload.description,
    )
    db.add(new_project)

    db.commit()
    db.refresh(new_project)

    return new_project


@router.patch("/{project_id}", response_model=ProjectResponse)
def update_project_details(
    payload: PatchProject,
    project_id: UUID4 = Path(..., description="project_id of the project"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    user_project = (
        db.query(Projects)
        .filter(
            Projects.project_id == project_id,
            Projects.user_id == current_user.user_id,
        )
        .first()
    )

    if not user_project:
        raise HTTPException(status_code=404, detail="Project not found")

    if payload.name is not None:
        user_project.name = payload.name
    if payload.description is not None:
        user_project.description = payload.description

    db.commit()
    db.refresh(user_project)
    return user_project
