from fastapi import APIRouter, Depends, HTTPException, Form, Query
from sqlalchemy.orm import Session
from schema.user import UserRegister, UserResponse
from models.user import Users
from lib.auth import jwt, JWTError, create_access_token, get_current_user
from db.db import get_db
from sqlalchemy.exc import IntegrityError

router = APIRouter()

@router.post("/", response_model=UserResponse)
def register_user(user: UserRegister, db: Session = Depends(get_db)):
    try:
        db_user = Users(
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            hashed_password=user.password
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        return db_user

    except IntegrityError as e:
        db.rollback()

        # Handles duplicate email (unique constraint)
        if "email" in str(e.orig).lower():
            raise HTTPException(
                status_code=400,
                detail="Email already registered"
            )

        raise HTTPException(
            status_code=400,
            detail="Database integrity error"
        )
        
