from fastapi import APIRouter
from typing import Optional, List

router = APIRouter()


@router.get("/")
async def global_search(
    query: str,
    types: Optional[List[str]] = None,
    limit: int = 20
):
    # WIP: Add logic for global search across everything
    # types can be: ["services", "docs", "deployments"]
    return {"message": f"Global search for '{query}' is a work in progress"}
