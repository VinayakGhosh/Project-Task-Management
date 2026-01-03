from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from models.plan import Plans
from lib.auth import get_current_user
from schema.plan import PlanResponse
from db.db import get_db
from typing import List
from pydantic import UUID4
from typing import Optional


router = APIRouter()


@router.get("/", response_model=List[PlanResponse])
def get_plans(
    db: Session = Depends(get_db), 
    plan_id: Optional[UUID4] = Query(None, description="Filter by PlayPassId"),
    current_user: dict = Depends(get_current_user)
):
    # Start building the base SQLAlchemy query
    query = db.query(Plans)     
    
    # If plan_id is provided in the query string,
    # add a WHERE clause to filter by plan_id
    if plan_id:
        query = query.filter(Plans.plan_id == plan_id)

    # Execute the query and fetch all matching plans
    plans = query.all()

    # If no plans are found, return a 404 error
    if not plans:
        raise HTTPException(
            status_code=404,
            detail="No Plans Found"
        )

    # Convert each Plan object to a PlanResponse schema
    return plans

