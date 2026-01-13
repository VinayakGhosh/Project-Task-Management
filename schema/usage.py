from pydantic import BaseModel
import enum

class FeatureNameEnum(str, enum.Enum):
    PROJECT = "Project"
    TASK = "Task"