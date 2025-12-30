from pydantic import BaseModel, EmailStr, Field
from typing import Annotated
from uuid import UUID
from datetime import datetime

class UserRegister(BaseModel):
    first_name: Annotated[str, Field(..., min_length=1, example="John")]
    last_name: Annotated[str, Field(..., min_length=1, example="Dwane")]
    email: Annotated[EmailStr, Field(..., examples=["abc@gmail.com"])]
    password: Annotated[str, Field(..., examples=["strongpassword"])]

class UserResponse(BaseModel):
    user_id: UUID
    first_name: str
    last_name: str
    email: EmailStr

class UserLoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_at: datetime
    user_id: UUID
    refresh_token_expires_at: datetime
