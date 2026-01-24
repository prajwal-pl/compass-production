from fastapi import APIRouter

router = APIRouter()

@router.post("/generate-text")
async def generate_text(prompt: str):
    if not prompt:
        return {"error": "Prompt is required"}

    # WIP: Add text generation logic here
    return {"message": "Text generation is a work in progress"}