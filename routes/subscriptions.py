from fastapi import HTTPException, Depends, APIRouter, Query
from sqlalchemy.orm import Session
from models.user import Subscriptions, Users
from schema.subscription import SubscriptionResponse, SubscriptionCreate, SubscriptionStatusEnum
from db.db import get_db
from lib.auth import get_current_user, get_admin_user
from typing import List, Optional
from pydantic import UUID4

router=APIRouter()

# @router.post("/", response_model=SubscriptionResponse)
# def create_subscription(
#     Subs: SubscriptionCreate,
#     db: Session = Depends(get_db),
#     current_user: dict = Depends(get_current_user)
# ):
    
#     new_subscription =0
#     return new_subscription
    

@router.get(
    "/",
    response_model=List[SubscriptionResponse],
    summary="Get subscriptions",
    description="Authenticated users can view subscriptions. Admins can view all."
)
def get_subscriptions(
    subscription_id: Optional[UUID4] = Query(None, description="Filter by subscription ID"),
    user_id: Optional[UUID4] = Query(None, description="Filter by user ID (Admin only)"),
    plan_id: Optional[UUID4] = Query(None, description="Filter by plan ID"),
    db: Session = Depends(get_db),
    current_user:dict = Depends(get_current_user),
):
    # Base query
    query = db.query(Subscriptions)

    # Restrict non-admin users to their own subscriptions
    if current_user.role != "Admin":
        query = query.filter(Subscriptions.user_id == current_user.user_id)
    else:
        # Admins can optionally filter by user_id
        if user_id:
            query = query.filter(Subscriptions.user_id == user_id)

    # Apply optional filters
    if subscription_id:
        query = query.filter(Subscriptions.subscription_id == subscription_id)

    if plan_id:
        query = query.filter(Subscriptions.plan_id == plan_id)

    subscriptions = query.all()
    if not subscriptions:
        raise HTTPException(status_code=404, detail="No subscriptions found")

    return subscriptions