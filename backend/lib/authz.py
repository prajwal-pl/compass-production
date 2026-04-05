from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Deployment, Service, User, user_teams


def _parse_uuid(value: str, field_name: str) -> UUID:
    try:
        return UUID(value)
    except (TypeError, ValueError):
        raise HTTPException(status_code=400, detail=f"Invalid {field_name} format")


async def _is_team_member(user_id: UUID, team_id: UUID | None, db: AsyncSession) -> bool:
    if not team_id:
        return False

    result = await db.execute(
        select(user_teams.c.user_id).where(
            user_teams.c.user_id == user_id,
            user_teams.c.team_id == team_id,
        )
    )
    return result.scalar_one_or_none() is not None


def require_superuser(current_user: User) -> None:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Superuser privileges are required",
        )


async def require_service_access(
    service_id: str,
    db: AsyncSession,
    current_user: User,
    require_owner: bool = False,
) -> Service:
    service_uuid = _parse_uuid(service_id, "service_id")
    result = await db.execute(select(Service).where(Service.id == service_uuid))
    service = result.scalar_one_or_none()

    if service is None:
        raise HTTPException(status_code=404, detail="Service not found")

    is_owner = service.owner_id == current_user.id
    is_superuser = current_user.is_superuser

    if is_superuser or is_owner:
        return service

    if require_owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Owner or superuser access required",
        )

    is_team_member = await _is_team_member(current_user.id, service.team_id, db)
    has_access = is_team_member

    if not require_owner and not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this service",
        )

    return service


async def require_deployment_access(
    deployment_id: str,
    db: AsyncSession,
    current_user: User,
    require_owner: bool = False,
) -> Deployment:
    deployment_uuid = _parse_uuid(deployment_id, "deployment_id")
    result = await db.execute(select(Deployment).where(Deployment.id == deployment_uuid))
    deployment = result.scalar_one_or_none()

    if deployment is None:
        raise HTTPException(status_code=404, detail="Deployment not found")

    await require_service_access(
        service_id=str(deployment.service_id),
        db=db,
        current_user=current_user,
        require_owner=require_owner,
    )
    return deployment
