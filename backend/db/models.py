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

class Tier(str, enum.Enum):
    TIER_1 = "tier-1"
    TIER_2 = "tier-2"
    TIER_3 = "tier-3"

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

class Service(Base, TimestampMixin):
    __tablename__ = "services"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    repository_url = Column(String(255), nullable=True)
    tags = Column(ARRAY(String), default=[])
    metadata = Column(JSON, default={})
    status = Column(Enum(ServiceStatus), default=ServiceStatus.ACTIVE, nullable=False)
    embedding = Column(Vector(1536), nullable=True)
    health_check_url = Column(String(500), nullable=True)
    language = Column(String(50), nullable=True)
    framework = Column(String(50), nullable=True)
    version = Column(String(50), nullable=True)
    tier = Column(Enum(Tier), default=Tier.TIER_3, nullable=False)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    owner = relationship("User", back_populates="services")
    deployments = relationship("Deployment", back_populates="service", cascade="all, delete-orphan")
    documentation = relationship("Documentation", back_populates="service", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_services_name", "name"),
        Index("ix_services_tags", "tags", postgresql_using="gin"),
        Index("ix_services_team", "team")
    )

class Deployment(Base, TimestampMixin):
    __tablename__ = "deployments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    service_id = Column(UUID(as_uuid=True), ForeignKey("services.id"), nullable=False)

    commit_sha = Column(String(40), nullable=False)
    version = Column(String(50), nullable=False)
    commit_message = Column(Text, nullable=True)

    environment = Column(Enum(Environment), nullable=False)
    status = Column(Enum(DeploymentStatus), default=DeploymentStatus.PENDING, nullable=False)

    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    triggered_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    triggered_type = Column(String(50), default="manual", nullable=False)

    rollback_from_id = Column(UUID(as_uuid=True), ForeignKey("deployments.id"), nullable=True)

    logs = Column(Text, nullable=True)
    metadata = Column(JSON, default={})

    service = relationship("Service", back_populates="deployments")

    __table_args__ = (
        Index("ix_deployments_service_env", "service_id", "environment"),
        Index("ix_deployments_status", "status"),
    )

class Documentation(Base, TimestampMixin):
    __tablename__ = "documentation"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    service_id = Column(UUID(as_uuid=True), ForeignKey("services.id"), nullable=False)

    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    version = Column(String(50), nullable=True)

    is_ai_generated = Column(Boolean, default=False, nullable=False)

    embedding = Column(Vector(1536), nullable=True)

    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    service = relationship("Service", back_populates="documentation")