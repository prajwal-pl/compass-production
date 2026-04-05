from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.db import get_db
from db.models import User
from lib.auth_context import get_current_user
from lib.authz import require_service_access

router = APIRouter()

@router.get("/search")
async def search_docs(
    query: str,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
):
    _ = current_user
    # WIP: Add logic for semantic search across all documentation
    return {"message": f"Search docs for '{query}' is a work in progress"}

@router.get("/{service_id}")
async def get_service_docs(
    service_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await require_service_access(service_id, db, current_user)
    # WIP: Add logic to get service documentation
    return {"message": f"Get docs for service {service_id} is a work in progress"}


@router.post("/{service_id}/generate")
async def generate_docs(
    service_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await require_service_access(service_id, db, current_user, require_owner=True)
    # WIP: Add logic to trigger AI documentation generation
    return {"message": f"Generate docs for service {service_id} is a work in progress"}


@router.get("/{service_id}/readme")
async def get_readme(
    service_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await require_service_access(service_id, db, current_user)
    # WIP: Add logic to get README.md from repository
    return {"message": f"Get README for service {service_id} is a work in progress"}