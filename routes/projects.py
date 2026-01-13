from fastapi import HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from db.db import get_db
from lib.auth import get_current_user
from models.plan import Projects, Plans
from models.user import Usage, Subscriptions
from schema.project import ProjectResponse, CreateProject
from schema.usage import FeatureNameEnum
from schema.subscription import SubscriptionStatusEnum
from datetime import datetime, date, time



router = APIRouter()

@router.post("/", response_model=ProjectResponse)
def create_project(
    payload: CreateProject,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    today = date.today()

    # 1️⃣ Check active subscription
    result = (
        db.query(Plans, Subscriptions)
        .join(Plans, Subscriptions.plan_id == Plans.plan_id)
        .filter(
            Subscriptions.user_id == current_user.user_id,
            Subscriptions.status == SubscriptionStatusEnum.ACTIVE.value,
        )
        .first()
    )

    if not result:
        raise HTTPException(403, "Active subscription required")

    user_plan, user_subscription = result

    # 2️⃣ Check today's usage (USER-SPECIFIC)
    usage_today = (
        db.query(Usage)
        .filter(
            Usage.user_id == current_user.user_id,
            Usage.feature_name == FeatureNameEnum.PROJECT.value,
            Usage.date == today,
        )
        .first()
    )

    # 3️⃣ Enforce plan limit
    if usage_today and usage_today.feature_count >= user_plan.max_projects:
        raise HTTPException(403, "Project limit reached")

    # 4️⃣ Create project
    new_project = Projects(
        user_id=current_user.user_id,
        name=payload.name,
        description=payload.description,
    )
    db.add(new_project)

    # 5️⃣ Update usage
    if usage_today:
        usage_today.feature_count += 1
    else:
        db.add(
            Usage(
                user_id=current_user.user_id,
                feature_name=FeatureNameEnum.PROJECT.value,
                feature_count=1,
                date=today,
            )
        )

    # 6️⃣ Commit once
    db.commit()
    db.refresh(new_project)

    return new_project