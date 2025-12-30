from pydantic import BaseModel, EmailStr, Field
from typing import Annotated
from uuid import UUID

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
