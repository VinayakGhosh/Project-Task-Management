from fastapi import APIRouter, Depends, HTTPException, Form, Query
from sqlalchemy.orm import Session
from schema.user import UserRegister, UserResponse, UserLoginResponse
from models.user import Users
from lib.auth import jwt, JWTError, create_access_token, get_current_user
from db.db import get_db
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
import os
from dotenv import load_dotenv
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


load_dotenv()
router = APIRouter()

ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS"))

@router.post("/signup", response_model=UserResponse)
def register_user(user: UserRegister, db: Session = Depends(get_db)):
    try:
        db_user = Users(
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            hashed_password=str(pwd_context.hash(user.password))
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
        

@router.post('/login', response_model=UserLoginResponse)
def user_login(
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    
    user = db.query(Users).filter(Users.email == email).first()
    if not user or not pwd_context.verify(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid Credentials")
    
    token_data = {"sub": str(user.user_id), "email": user.email}
    access_token = create_access_token(data=token_data, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    refresh_token = create_access_token(data=token_data, expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))

    refresh_token_expires_at = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_at": datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        "user_id": str(user.user_id),
        "refresh_token_expires_at": refresh_token_expires_at
    }