from pgvector import Vector
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List, Any
from uuid import UUID
from datetime import datetime
from enum import Enum

from sqlalchemy import Column

class ServiceStatus(str, Enum):
    ACTIVE = "active"
    DEGRADED = "degraded"
    DOWN = "down"
    MAINTENANCE = "maintenance"

class DeploymentStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"

class Environment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"

class Tier(str, Enum):
    TIER_1 = "tier-1"
    TIER_2 = "tier-2"
    TIER_3 = "tier-3"

class UserCreate(BaseModel):
    username: str = Field(..., max_length=50)
    email: EmailStr
    full_name: Optional[str] = Field(None, max_length=100)
    password: str = Field(..., min_length=8)
    is_google_auth: bool = False

class UserLogin(BaseModel):
    username: str
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, max_length=100)
    password: Optional[str] = Field(None, min_length=8)
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None

class UserDelete(BaseModel):
    confirm: bool = Field(..., description="Confirm that you want to delete this user")
    email: EmailStr

class ServiceCreate(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    repository_url: Optional[str] = None
    tags: List[str] = []
    metadata: Optional[dict] = None
    status: ServiceStatus = ServiceStatus.ACTIVE
    tier: Tier = Tier.TIER_3
    embedding: Optional[Vector] = None
    language: Optional[str] = None
    framework: Optional[str] = None
    health_check_url: Optional[str] = None
    version: Optional[str] = None
    owner_id: UUID

class ServiceUpdate(BaseModel):
    description: Optional[str] = None
    repository_url: Optional[str] = None
    tags: Optional[List[str]] = None
    metadata: Optional[dict] = None
    status: Optional[ServiceStatus] = None
    tier: Optional[Tier] = None
    embedding: Optional[Vector] = None
    language: Optional[str] = None
    framework: Optional[str] = None
    tier: Optional[Tier] = None
    status: Optional[ServiceStatus] = None
    health_check_url: Optional[str] = None
    version: Optional[str] = None
    
class ServiceDelete(BaseModel):
    confirm: bool = Field(..., description="Confirm that you want to delete this service")
    service_id: UUID

class DeploymentCreate(BaseModel):
    service_id: UUID
    environment: Environment
    version: Optional[str] = None
    commit_sha: Optional[str] = None
    commit_message: Optional[str] = None
    version: Optional[str] = None
    status: DeploymentStatus = DeploymentStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    triggered_by: Optional[UUID] = None
    triggered_type: Optional[str] = None
    rollback_from_id: Optional[UUID] = None
    logs: Optional[str] = None
    metadata: Optional[dict] = None

class DeploymentUpdate(BaseModel):
    environment: Optional[Environment] = None
    version: Optional[str] = None
    commit_sha: Optional[str] = None
    commit_message: Optional[str] = None
    version: Optional[str] = None
    status: Optional[DeploymentStatus] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    triggered_by: Optional[UUID] = None
    triggered_type: Optional[str] = None
    rollback_from_id: Optional[UUID] = None
    logs: Optional[str] = None
    metadata: Optional[dict] = None

class DeploymentDelete(BaseModel):
    confirm: bool = Field(..., description="Confirm that you want to delete this deployment")
    deployment_id: UUID

class DocumentationCreate(BaseModel):
    service_id: UUID
    title: str = Field(..., max_length=200)
    content: str
    version: Optional[str] = None
    is_ai_generated: bool = False
    embedding: Optional[Vector] = None
    author_id: Optional[UUID] = None

class DocumentationUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    content: Optional[str] = None
    version: Optional[str] = None
    is_ai_generated: Optional[bool] = None
    embedding: Optional[Vector] = None
    author_id: Optional[UUID] = None

class DocumentationDelete(BaseModel):
    confirm: bool = Field(..., description="Confirm that you want to delete this documentation")
    documentation_id: UUID

