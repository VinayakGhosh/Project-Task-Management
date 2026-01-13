from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime
import enum


class SubscriptionStatusEnum(str, enum.Enum):
    ACTIVE = "Active"
    CANCELLED = "Cancelled"
    EXPIRED = "Expired"
    ENDED = "Ended"  # when new plan subscription added above and existing one


class SubscriptionCreate(BaseModel):
    user_id: UUID
    plan_id: UUID
    start_timestamp: datetime
    end_timestamp: Optional[datetime]
    status: SubscriptionStatusEnum


class SubscriptionResponse(BaseModel):
    subscription_id: UUID
    user_id: UUID
    plan_id: UUID
    start_timestamp: datetime
    end_timestamp: Optional[datetime]
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # IMPORTANT for SQLAlchemy ORM
