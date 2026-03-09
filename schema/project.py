from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime

class CreateProject(BaseModel):
    name: str
    description: Optional[str] = None

class ProjectResponse(BaseModel):
    project_id: UUID
    owner_user_id: UUID
    organization_id: Optional[UUID]
    name: str
    description: str
    created_at: datetime
    updated_at: datetime

class PatchProject(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
