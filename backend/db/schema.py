from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from enum import Enum

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
    model_config = ConfigDict(extra="forbid")

    username: str = Field(..., max_length=50)
    email: EmailStr
    full_name: Optional[str] = Field(None, max_length=100)
    password: str = Field(..., min_length=8, max_length=128)

class UserLogin(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    full_name: Optional[str] = Field(None, max_length=100)
    password: Optional[str] = Field(None, min_length=8)


class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool
    is_superuser: bool
    is_google_auth: bool
    created_at: datetime
    updated_at: Optional[datetime] = None


class AuthResponse(BaseModel):
    message: str
    user: UserPublic
    access_token: str
    refresh_token: Optional[str] = None


class UserResponse(BaseModel):
    user: UserPublic


class UserMessageResponse(BaseModel):
    message: str
    user: UserPublic


class MessageResponse(BaseModel):
    message: str


class PasswordResetRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: EmailStr


class PasswordResetConfirm(BaseModel):
    model_config = ConfigDict(extra="forbid")

    token: str = Field(..., min_length=20)
    new_password: str = Field(..., min_length=8, max_length=128)


class PasswordResetTokenResponse(BaseModel):
    message: str
    reset_token: str


class RefreshTokenRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    refresh_token: str = Field(..., min_length=20)


class LogoutRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    refresh_token: Optional[str] = Field(default=None, min_length=20)

class UserDelete(BaseModel):
    model_config = ConfigDict(extra="forbid")

    confirm: bool = Field(..., description="Confirm that you want to delete this user")
    email: EmailStr

class ServiceCreate(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    repository_url: Optional[str] = None
    tags: List[str] = []
    meta_data: Optional[dict] = None
    status: ServiceStatus = ServiceStatus.ACTIVE
    tier: Tier = Tier.TIER_3
    language: Optional[str] = None
    framework: Optional[str] = None
    health_check_url: Optional[str] = None
    version: Optional[str] = None
    owner_id: UUID

class ServiceUpdate(BaseModel):
    description: Optional[str] = None
    repository_url: Optional[str] = None
    tags: Optional[List[str]] = None
    meta_data: Optional[dict] = None
    status: Optional[ServiceStatus] = None
    tier: Optional[Tier] = None
    language: Optional[str] = None
    framework: Optional[str] = None
    status: Optional[ServiceStatus] = None
    health_check_url: Optional[str] = None
    version: Optional[str] = None
    
class ServiceDelete(BaseModel):
    confirm: bool = Field(..., description="Confirm that you want to delete this service")
    service_id: UUID

class TeamCreate(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = None

class TeamUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None

class TeamDelete(BaseModel):
    confirm: bool = Field(..., description="Confirm that you want to delete this team")
    team_id: UUID

class DeploymentCreate(BaseModel):
    service_id: UUID
    environment: Environment
    version: Optional[str] = None
    commit_sha: Optional[str] = None
    commit_message: Optional[str] = None
    status: DeploymentStatus = DeploymentStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    triggered_by: Optional[UUID] = None
    triggered_type: Optional[str] = None
    rollback_from_id: Optional[UUID] = None
    logs: Optional[str] = None
    meta_data: Optional[dict] = None

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
    meta_data: Optional[dict] = None

class DeploymentDelete(BaseModel):
    confirm: bool = Field(..., description="Confirm that you want to delete this deployment")
    deployment_id: UUID

class DocumentationCreate(BaseModel):
    service_id: UUID
    title: str = Field(..., max_length=200)
    content: str
    version: Optional[str] = None
    is_ai_generated: bool = False
    author_id: Optional[UUID] = None

class DocumentationUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    content: Optional[str] = None
    version: Optional[str] = None
    is_ai_generated: Optional[bool] = None
    author_id: Optional[UUID] = None

class DocumentationDelete(BaseModel):
    confirm: bool = Field(..., description="Confirm that you want to delete this documentation")
    documentation_id: UUID

