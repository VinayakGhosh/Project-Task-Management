from pydantic import BaseModel 
import enum
from uuid import UUID
from typing import Optional

class TaskStatusEnum(str, enum.Enum):
    DONE = "Done"
    PENDING = "Pending"
    IN_PROGRESS = "InProgress"
    CANCELLED = "Cancelled"

class TaskCreateSchema(BaseModel):
    project_id: UUID
    name: str
    description: Optional[str] = None

class TaskResponseSchema(BaseModel):
    task_id: UUID
    project_id: UUID 
    name: str
    description: str
    status: str
    created_at: str 
    updated_at: str

class PatchTask(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str]=None