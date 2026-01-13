from fastapi import HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from db.db import get_db
from lib.auth import get_current_user
from models.plan import Projects, Plans
from models.user import Usage, Subscriptions
from schema.project import ProjectResponse, CreateProject
from schema.usage import FeatureNameEnum
from schema.subscription import SubscriptionStatusEnum
from datetime import date
from lib.subscription import require_active_subscription



router = APIRouter()

@router.post("/", response_model=ProjectResponse)
def create_project(
    payload: CreateProject,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    subscription = Depends(require_active_subscription)
):
    today = date.today()

    # 1️⃣ Check active subscription
    user_plan = db.query(Plans).filter(subscription.plan_id==Plans.plan_id).first()

    if not user_plan:
        raise HTTPException(404, "no plan exist for this subscription")

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