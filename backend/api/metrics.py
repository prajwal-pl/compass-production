from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.db import get_db
from db.models import User
from lib.auth_context import get_current_user
from lib.authz import require_service_access, require_superuser

router = APIRouter()

@router.get("/overview")
async def get_platform_metrics(current_user: User = Depends(get_current_user)):
    require_superuser(current_user)
    # WIP: Add logic to get platform-wide metrics
    return {"message": "Get platform metrics overview is a work in progress"}

@router.get("/{service_id}")
async def get_service_metrics(
    service_id: str,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    interval: str = "5m",
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _ = start_time, end_time, interval
    await require_service_access(service_id, db, current_user)
    # WIP: Add logic to get service metrics
    return {"message": f"Get metrics for service {service_id} is a work in progress"}