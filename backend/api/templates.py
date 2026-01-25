from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def list_templates():
    # WIP: Add logic to list available service templates
    return {"message": "List templates is a work in progress"}


@router.get("/{template_id}")
async def get_template(template_id: str):
    # WIP: Add logic to get template details
    return {"message": f"Get template {template_id} is a work in progress"}


@router.post("/{template_id}/generate")
async def generate_service(template_id: str):
    # WIP: Add logic to generate new service from template
    return {"message": f"Generate service from template {template_id} is a work in progress"}


@router.get("/jobs/{job_id}")
async def get_generation_job(job_id: str):
    # WIP: Add logic to check service generation progress
    return {"message": f"Get generation job {job_id} is a work in progress"}
