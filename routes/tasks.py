from fastapi import HTTPException, Depends, APIRouter, Query
from sqlalchemy.orm import Session
from models.plan import Tasks, Plans, Projects
from models.user import Usage
from lib.subscription import require_active_subscription
from lib.auth import get_current_user
from schema.task import TaskCreateSchema, TaskResponseSchema, PatchTask, TaskStatusEnum
from schema.usage import FeatureNameEnum
from db.db import get_db
from datetime import datetime, timezone
from typing import Optional, List
from uuid import UUID

router = APIRouter()


@router.post("/", response_model=TaskResponseSchema)
def create_task(
    payload: TaskCreateSchema,
    db: Session = Depends(get_db),
    subscription = Depends(require_active_subscription),
    current_user = Depends(get_current_user)
):
    
    project = db.query(Projects).filter(
        Projects.id == payload.project_id,
        Projects.user_id == current_user.user_id
        ).first()

    if not project:
        raise HTTPException(status_code=403, detail="Invalid project")

    # fetch user's current plan
    user_plan = db.query(Plans).filter(Plans.plan_id==subscription.plan_id).first()
    
    if not user_plan:
        raise HTTPException(status_code=404, detail="no plans found for this subscription")
    
    #  task_per_day limit
    task_per_day = user_plan.task_per_day

    # Find out user's todays usage
    today = datetime.now(timezone.utc).date()


    usage_today = db.query(Usage).filter(
        Usage.date==today,
        Usage.feature_name==FeatureNameEnum.TASK.value,
        Usage.user_id == current_user.user_id
        ).first()
    if usage_today:
        # check if the usage is greater than equal to allowed usage in plan
        if usage_today.feature_count >=task_per_day:
            raise HTTPException(status_code=403, detail="Task limit exceeded")
        else:
            usage_today.feature_count +=1
    else:
        new_usage = Usage(
            user_id=current_user.user_id,
            feature_name=FeatureNameEnum.TASK.value,
            feature_count=1,
            date=today,
        )
        db.add(new_usage)
    
    #create the task
    new_task = Tasks(
        project_id=payload.project_id,
        user_id = current_user.user_id,
        name = payload.name,
        description=payload.description
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task



@router.patch("/{task_id}", response_model=TaskResponseSchema)
def update_task(
    task_id: str,
    payload: PatchTask,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    # 1️⃣ Fetch task and enforce ownership
    task = db.query(Tasks).filter(
        Tasks.task_id == task_id,
        Tasks.user_id == current_user.user_id
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # 2️⃣ Apply partial updates safely
    if payload.name is not None:
        task.name = payload.name

    if payload.description is not None:
        task.description = payload.description

    if payload.status is not None:
        task.status = payload.status

    # 3️⃣ Persist changes
    db.commit()
    db.refresh(task)

    return task


@router.get("/", response_model=List[TaskResponseSchema])
def get_tasks(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),

    task_id: Optional[UUID] = Query(None),
    project_id: Optional[UUID] = Query(None),
    status: Optional[TaskStatusEnum] = Query(None),
):
    query = db.query(Tasks).filter(
        Tasks.user_id == current_user.user_id
    )

    # Optional filters
    if task_id is not None:
        query = query.filter(Tasks.task_id == task_id)

    if project_id is not None:
        query = query.filter(Tasks.project_id == project_id)

    if status is not None:
        query = query.filter(Tasks.status == status.value)

    tasks = query.order_by(Tasks.created_at.desc()).all()
    return tasks