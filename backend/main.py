from fastapi import FastAPI
import api.auth as auth

app = FastAPI()

app.include_router(auth.router, prefix="/auth", tags=["auth"])

@app.get("/")
async def read_root():
    return {"Hello": "World"}
