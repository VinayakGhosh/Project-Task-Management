import uuid
from sqlalchemy import Column, Integer, String, UUID, Boolean, ForeignKey, TIMESTAMP, text
from db.db import Base


class Users(Base):
    __tablename__ = "users"

    user_id = Column(
        UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4
    )
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    CreatedAtTimeStamp = Column(TIMESTAMP(timezone=True), server_default=text('now()'))
    UpdatedAtTimeStamp = Column(TIMESTAMP(timezone=True), onupdate=text('now()'), server_default=text('now()'))


class Subscriptions(Base):
    __tablename__ = "subscriptions"
    subscription_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID, ForeignKey("users.user_id"), nullable=False)
    plan_id = Column(UUID, ForeignKey("plans.plan_id"), nullable=False)
    start_timestamp = Column(TIMESTAMP(timezone=True), nullable=False)
    end_timestamp = Column(TIMESTAMP(timezone=True), nullable=False)
    status = Column(String, nullable=False)
    CreatedAtTimeStamp = Column(TIMESTAMP(timezone=True), server_default=text('now()'))
    UpdatedAtTimeStamp = Column(TIMESTAMP(timezone=True), onupdate=text('now()'), server_default=text('now()'))
    