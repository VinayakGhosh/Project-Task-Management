import uuid
from db.db import Base
from sqlalchemy import Column, TIMESTAMP, String, UUID, Integer, Boolean, text, ForeignKey
from sqlalchemy.orm import relationship
from schema.task import TaskStatusEnum

class Plans(Base):
    __tablename__ = "plans"

    plan_id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    plan_tier = Column(String, nullable=False)
    price = Column(Integer, nullable=True)
    duration_days = Column(Integer, nullable=True)
    max_projects = Column(Integer, nullable=False)
    task_per_day = Column(Integer, nullable=False)
    export_allowed = Column(Boolean, nullable=False)
    is_discontinued = Column(Boolean, nullable=False, server_default=text("false"), default=False)
    is_deleted = Column(Boolean, nullable=False, server_default=text("false"), default=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'))
    updated_at = Column(TIMESTAMP(timezone=True), onupdate=text('now()'), server_default=text('now()'))


class Projects(Base):
    __tablename__ = "projects"
    project_id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    user_id = Column(UUID, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True, default="No description")
    created_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'))
    updated_at = Column(TIMESTAMP(timezone=True), onupdate=text('now()'), server_default=text('now()'))

class Tasks(Base):
    __tablename__ = "tasks"
    task_id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    project_id = Column(UUID, ForeignKey("projects.project_id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True, default="No description") 
    status = Column(String, nullable=False, default=TaskStatusEnum.PENDING.value)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'))
    updated_at = Column(TIMESTAMP(timezone=True), onupdate=text('now()'), server_default=text('now()'))