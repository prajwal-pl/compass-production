from fastapi import FastAPI
import api.auth as auth
import api.ai as ai

app = FastAPI()

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(auth.router, prefix="/ai", tags=["ai"])

@app.get("/")
async def read_root():
    return {"Hello": "World"}
