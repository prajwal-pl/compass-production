from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.db import get_db
from db.models import User
from lib.auth_context import get_current_user
from lib.authz import require_deployment_access, require_service_access, require_superuser

router = APIRouter()


@router.get("/")
async def list_deployments(
    service_id: Optional[str] = None,
    environment: Optional[str] = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _ = environment, limit

    if service_id:
        await require_service_access(service_id, db, current_user)
    else:
        require_superuser(current_user)

    # WIP: Add logic to list deployment history
    return {"message": "List deployments is a work in progress"}


@router.post("/")
async def trigger_deployment(
    service_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await require_service_access(service_id, db, current_user, require_owner=True)
    # WIP: Add logic to trigger a new deployment
    return {"message": "Trigger deployment is a work in progress"}


@router.get("/{deployment_id}")
async def get_deployment(
    deployment_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await require_deployment_access(deployment_id, db, current_user)
    # WIP: Add logic to get deployment details
    return {"message": f"Get deployment {deployment_id} is a work in progress"}


@router.post("/{deployment_id}/rollback")
async def rollback_deployment(
    deployment_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await require_deployment_access(deployment_id, db, current_user, require_owner=True)
    # WIP: Add logic to rollback to previous version
    return {"message": f"Rollback deployment {deployment_id} is a work in progress"}


@router.get("/{deployment_id}/status")
async def get_deployment_status(
    deployment_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await require_deployment_access(deployment_id, db, current_user)
    # WIP: Add logic to get real-time deployment status
    return {"message": f"Get status for deployment {deployment_id} is a work in progress"}
