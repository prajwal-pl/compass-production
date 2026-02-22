from fastapi import APIRouter, Depends, HTTPException
from db.schema import UserCreate
from sqlalchemy.ext.asyncio import AsyncSession
from db.db import get_db
from db.models import User
from sqlalchemy import select
from xxhash import xxh64_hexdigest as hash_password

router = APIRouter()

@router.post("/register")
async def register_user(payload: UserCreate, db: AsyncSession = Depends(get_db)):

    if not payload.email or not payload.password or not payload.username:
        raise HTTPException(status_code=400, detail="Neccessary fields are missing")
    
    try: 
        result = await db.execute(select(User).where(User.email == payload.email))
        is_existing = result.scalar_one_or_none()

        if is_existing:
            raise HTTPException(status_code=409, detail="User with this email already exists")
        
        hashed_password = hash_password(payload.password.encode('utf-8'))

        new_user = User(email=payload.email, username=payload.username, full_name=payload.full_name, is_google_auth=False, is_superuser=False, hashed_password=hashed_password)

        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        return {"message": "User registered successfully", "user": new_user}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/login")
async def login_user(payload: UserCreate, db: AsyncSession = Depends(get_db)):
    if not payload.email or not payload.password:
        return {"error": "Email and password are required"}

    try: 
        result = await db.execute(select(User).where(User.email == payload.email))
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        hashed_input_password = hash_password(payload.password.encode('utf-8'))

        if hashed_input_password != user.hashed_password:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        # WIP: Add logic to generate and return access token here
        return {"message": "User login successful", "user": user}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/logout")
async def logout_user():
    # WIP: Add user logout logic here
    return {"message": "User logout is a work in progress"}

@router.post("/reset-password")
async def reset_password(email: str):
    if not email:
        return {"error": "Email is required"}

    # WIP: Add password reset logic here
    return {"message": "Password reset is a work in progress"}

@router.get("/profile")
async def get_user_profile():
    # WIP: Add logic to retrieve user profile here
    return {"message": "Get user profile is a work in progress"}

@router.put("/profile")
async def update_user_profile():
    # WIP: Add logic to update user profile here
    return {"message": "Update user profile is a work in progress"}

@router.delete("/delete-account")
async def delete_user_account():
    # WIP: Add logic to delete user account here
    return {"message": "Delete user account is a work in progress"}