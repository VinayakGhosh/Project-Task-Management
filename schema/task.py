from pydantic import BaseModel
import enum

class TaskStatusEnum(str, enum.Enum):
    DONE = "Done",
    PENDING = "Pending",
    IN_PROGRESS = "InProgress",
    CANCELLED = "Cancelled"