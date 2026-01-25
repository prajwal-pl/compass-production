from fastapi import APIRouter
from typing import Optional
from datetime import datetime

router = APIRouter()


@router.get("/{service_id}")
async def get_service_metrics(
    service_id: str,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    interval: str = "5m"
):
    # WIP: Add logic to get service metrics
    return {"message": f"Get metrics for service {service_id} is a work in progress"}


@router.get("/overview")
async def get_platform_metrics():
    # WIP: Add logic to get platform-wide metrics
    return {"message": "Get platform metrics overview is a work in progress"}
