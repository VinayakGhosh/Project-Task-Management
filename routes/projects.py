from fastapi import HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from db.db import get_db
from lib.auth import get_current_user
from models.plan import Projects, Plans
from schema.project import ProjectResponse, CreateProject

from lib.subscription import require_active_subscription


router = APIRouter()


@router.post("/", response_model=ProjectResponse)
def create_project(
    payload: CreateProject,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    subscription=Depends(require_active_subscription),
):

    # Check active subscription
    user_plan = db.query(Plans).filter(Plans.plan_id == subscription.plan_id).first()

    if not user_plan:
        raise HTTPException(status_code=404, detail="no plan exist for this subscription")

    total_projects = (
        db.query(Projects).filter(Projects.user_id == current_user.user_id).count()
    )

    # check total projects < max project allowed in plan
    if total_projects >= user_plan.max_projects:
        raise HTTPException(status_code=403, detail="Project limit reached for your current plan")

    
    new_project = Projects(
        user_id=current_user.user_id,
        name=payload.name,
        description=payload.description,
    )
    db.add(new_project)

    db.commit()
    db.refresh(new_project)

    return new_project
