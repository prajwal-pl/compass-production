from sqlalchemy import (Boolean, Column, Integer, String, ForeignKey, Float, DateTime, Index, Enum, JSON, Text)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
from .db import Base
from sqlalchemy.dialects.postgresql import UUID, ARRAY
import enum
import uuid

class ServiceStatus(str, enum.Enum):
    ACTIVE = "active"
    DEGRADED = "degraded"
    DOWN = "down"
    MAINTENANCE = "maintenance"

class DeploymentStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"

class Environment(str, enum.Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"

class TimestampMixin:
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True, server_default=func.now())

class User(Base, TimestampMixin):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    full_name = Column(String(100), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, nullable=False)
    is_superuser = Column(Boolean, nullable=False)
    is_google_auth = Column(Boolean, default=False, nullable=False)

    services = relationship("Service", back_populates="owner")
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    deployments = relationship("Deployment", back_populates="deployed_by")

# class Service(Base, TimestampMixin):
#     __tablename__ = "services"

#     id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
#     name = Column(String(100), unique=True, nullable=False)
#     description = Column(Text, nullable=True)
