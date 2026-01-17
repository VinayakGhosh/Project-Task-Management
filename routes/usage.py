from datetime import date
from typing import Optional
from fastapi import HTTPException, Depends, Query, APIRouter
from sqlalchemy.orm import Session
from db.db import get_db
from lib.auth import get_current_user
from models.user import Usage

router = APIRouter()

@router.get("/usage")
def get_usage(
    feature_name: Optional[str] = Query(None),
    usage_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    query = db.query(Usage).filter(
        Usage.user_id == current_user.user_id
    )

    if feature_name:
        query = query.filter(Usage.feature_name == feature_name)

    if usage_date:
        query = query.filter(Usage.date == usage_date)
    
    usage = query.all()

    if not usage:
        raise HTTPException(status_code=404, detail="no usage found")
    
    return usage
