from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, WebSocket
from sqlalchemy.ext.asyncio import AsyncSession

from db.db import get_db
from db.models import User
from lib.auth_context import (
    decode_access_token,
    fetch_user_from_db,
    get_current_user,
    is_access_token_revoked,
)
from lib.authz import require_service_access

router = APIRouter()


@router.get("/")
async def list_services(
    skip: int = 0,
    limit: int = 100,
    owner: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user),
):
    _ = current_user
    # WIP: Add logic to list all services with filters
    return {"message": "List services is a work in progress"}


@router.post("/")
async def create_service(current_user: User = Depends(get_current_user)):
    _ = current_user
    # WIP: Add logic to create a new service
    return {"message": "Create service is a work in progress"}


@router.get("/{service_id}")
async def get_service(
    service_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await require_service_access(service_id, db, current_user)
    # WIP: Add logic to get service details
    return {"message": f"Get service {service_id} is a work in progress"}


@router.put("/{service_id}")
async def update_service(
    service_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await require_service_access(service_id, db, current_user, require_owner=True)
    # WIP: Add logic to update service metadata
    return {"message": f"Update service {service_id} is a work in progress"}


@router.delete("/{service_id}")
async def delete_service(
    service_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await require_service_access(service_id, db, current_user, require_owner=True)
    # WIP: Add logic to delete service
    return {"message": f"Delete service {service_id} is a work in progress"}


@router.get("/{service_id}/health")
async def get_service_health(
    service_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await require_service_access(service_id, db, current_user)
    # WIP: Add logic to get real-time health status
    return {"message": f"Get health for service {service_id} is a work in progress"}


@router.get("/{service_id}/logs")
async def get_service_logs(
    service_id: str,
    lines: int = 100,
    level: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await require_service_access(service_id, db, current_user)
    # WIP: Add logic to get recent logs
    return {"message": f"Get logs for service {service_id} is a work in progress"}


@router.websocket("/{service_id}/logs/stream")
async def stream_logs(
    websocket: WebSocket,
    service_id: str,
    db: AsyncSession = Depends(get_db),
):
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=1008, reason="Missing auth token")
        return

    try:
        if await is_access_token_revoked(token):
            raise HTTPException(status_code=401, detail="Token has been revoked")

        payload = decode_access_token(token)
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token payload")

        current_user = await fetch_user_from_db(str(user_id), db)
        await require_service_access(service_id, db, current_user)
    except HTTPException as exc:
        await websocket.close(code=1008, reason=exc.detail)
        return

    # WIP: Add logic for live log streaming via WebSocket
    await websocket.accept()
    await websocket.send_json({"message": f"Log streaming for {service_id} is a work in progress"})
    await websocket.close()
