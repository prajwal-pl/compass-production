from fastapi import APIRouter, Depends, HTTPException
from db.schema import UserCreate, UserLogin, UserUpdate
from sqlalchemy.ext.asyncio import AsyncSession
from db.db import get_db
from db.models import User
from sqlalchemy import select
from lib.auth_context import get_current_user, hash_password, create_access_token, verify_password

router = APIRouter()

@router.post("/register")
async def register_user(payload: UserCreate, db: AsyncSession = Depends(get_db)):

    result = await db.execute(select(User).where(User.email == payload.email))
    is_existing = result.scalar_one_or_none()

    if is_existing:
        raise HTTPException(status_code=409, detail="User with this email already exists")
    
    hashed_password = hash_password(payload.password)

    new_user = User(email=payload.email, username=payload.username, full_name=payload.full_name, is_google_auth=False, is_superuser=False, hashed_password=hashed_password)

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    serializable_user_id = str(new_user.id)
    access_token = create_access_token({"user_id": serializable_user_id})
    return {"message": "User registered successfully", "user": new_user, "access_token": access_token}


@router.post("/login")
async def login_user(payload: UserLogin, db: AsyncSession = Depends(get_db)):

    result = await db.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    serializable_user_id = str(user.id)

    access_token = create_access_token({"user_id": serializable_user_id})
    return {"message": "User login successful", "user": user, "access_token": access_token}

@router.post("/logout")
async def logout_user():
    # WIP: Add user logout logic here
    return {"message": "User logout is a work in progress"}

@router.post("/reset-password")
async def reset_password(email: str):
    if not email:
        raise HTTPException(status_code=400, detail="Email is required")

    # WIP: Add password reset logic here
    return {"message": "Password reset is a work in progress"}

@router.get("/profile")
async def get_user_profile(user_id: str, db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)):
    if not user_id:
        raise HTTPException(status_code=400, detail="User ID is required")
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {"user": user}

@router.put("/profile")
async def update_user_profile(user_id: str, payload: UserUpdate, db:AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)):
    if not user_id or payload is None:
        raise HTTPException(status_code=400, detail="Necessary fields missing!")
    
    if "email" in payload.model_dump(exclude_unset=True):
        raise HTTPException(status_code=403, detail="Email cannot be changed!")
    
    if "password" in payload:
        current_user.hashed_password = hash_password(payload.password)

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(current_user, field, value)

    await db.commit()
    await db.refresh(current_user)
    return {"message": "User profile updated successfully", "user": current_user}

@router.delete("/delete-account")
async def delete_user_account():
    # WIP: Add logic to delete user account here
    return {"message": "Delete user account is a work in progress"}