from models.plan import Projects, Tasks, Plans
from datetime import date
from typing import Optional
from fastapi import HTTPException, Depends, Query, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import func
from db.db import get_db
from lib.auth import get_current_user
from lib.subscription import require_active_subscription
from schema.stats import StatsResponse
from schema.task import TaskStatusEnum

router = APIRouter()

@router.get("/", response_model=StatsResponse)
def get_overall_stats(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    subscription=Depends(require_active_subscription)
):
    # Calculate Projects Count
    projects_count = db.query(Projects).filter(
        Projects.owner_user_id == current_user.user_id,
        Projects.isDelete == False
    ).count()

    # Calculate Tasks Count
    # Joining with Projects to ensure we only count tasks for projects owned by the user
    base_task_query = db.query(Tasks).join(Projects).filter(
        Projects.owner_user_id == current_user.user_id,
        Projects.isDelete == False,
        Tasks.isDelete == False
    )

    tasks_count = base_task_query.count()
    
    tasks_completed_count = base_task_query.filter(Tasks.status == TaskStatusEnum.DONE.value).count()
    tasks_pending_count = base_task_query.filter(Tasks.status == TaskStatusEnum.PENDING.value).count()
    tasks_in_progress_count = base_task_query.filter(Tasks.status == TaskStatusEnum.IN_PROGRESS.value).count()

    # Get plan limits from subscription
    plan = db.query(Plans).filter(
        Plans.plan_id == subscription.plan_id,
        Plans.is_deleted == False,
        Plans.is_discontinued == False
    ).first()

    if not plan:
        raise HTTPException(status_code=404, detail="No active subscription plan found")

    return StatsResponse(
        projects_count=projects_count,
        tasks_count=tasks_count,
        tasks_completed_count=tasks_completed_count,
        tasks_pending_count=tasks_pending_count,
        tasks_in_progress_count=tasks_in_progress_count,
        task_limit=plan.task_per_day,
        project_limit=plan.max_projects
    )
