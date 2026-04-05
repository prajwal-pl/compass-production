from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from db.db import get_db
from db.models import User
from db.schema import (
    AuthResponse,
    PasswordResetConfirm,
    PasswordResetRequest,
    PasswordResetTokenResponse,
    MessageResponse,
    UserCreate,
    UserDelete,
    UserLogin,
    UserMessageResponse,
    UserResponse,
    UserUpdate,
)
from lib.auth_context import (
    create_access_token,
    create_reset_token,
    decode_reset_token,
    get_current_user,
    hash_password,
    oauth2_scheme,
    revoke_access_token,
    verify_password,
)

router = APIRouter()
PASSWORD_RESET_MESSAGE = "If the account exists, a password reset token has been generated"


def _serialize_user(user: User) -> dict:
    return {
        "id": str(user.id),
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "is_active": user.is_active,
        "is_superuser": user.is_superuser,
        "is_google_auth": user.is_google_auth,
        "created_at": user.created_at,
        "updated_at": user.updated_at,
    }


def _resolve_auth_context(current_user: User) -> tuple[str, bool]:
    return str(current_user.id), bool(current_user.is_superuser)


def _parse_user_id(user_id: str) -> UUID:
    try:
        return UUID(user_id)
    except (TypeError, ValueError):
        raise HTTPException(status_code=400, detail="Invalid user ID format")


async def _issue_reset_token_for_email(email: str, db: AsyncSession) -> dict:
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    # Do not leak whether the account exists; return a token-shaped response either way.
    token_user_id = str(user.id) if user and user.is_active else str(uuid4())
    reset_token = create_reset_token(token_user_id)
    return {"message": PASSWORD_RESET_MESSAGE, "reset_token": reset_token}

@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register_user(payload: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(User).where(
            or_(User.email == payload.email, User.username == payload.username)
        )
    )
    is_existing = result.scalar_one_or_none()

    if is_existing:
        if is_existing.email == payload.email:
            raise HTTPException(status_code=409, detail="User with this email already exists")
        raise HTTPException(status_code=409, detail="User with this username already exists")

    hashed_password = hash_password(payload.password)

    new_user = User(
        email=payload.email,
        username=payload.username,
        full_name=payload.full_name,
        is_google_auth=False,
        is_superuser=False,
        hashed_password=hashed_password,
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    serializable_user_id = str(new_user.id)
    access_token = create_access_token({"user_id": serializable_user_id})
    return {
        "message": "User registered successfully",
        "user": _serialize_user(new_user),
        "access_token": access_token,
    }


@router.post("/login", response_model=AuthResponse)
async def login_user(payload: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Inactive user account")

    serializable_user_id = str(user.id)

    access_token = create_access_token({"user_id": serializable_user_id})
    return {
        "message": "User login successful",
        "user": _serialize_user(user),
        "access_token": access_token,
    }

@router.post("/logout", response_model=MessageResponse)
async def logout_user(
    token: str = Depends(oauth2_scheme),
    current_user: User = Depends(get_current_user),
):
    _ = current_user
    revoke_access_token(token)
    return {"message": "User logout successful"}


@router.post("/reset-password/request", response_model=PasswordResetTokenResponse)
async def request_password_reset(
    payload: PasswordResetRequest,
    db: AsyncSession = Depends(get_db),
):
    return await _issue_reset_token_for_email(payload.email, db)

@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(
    email: str,
    db: AsyncSession = Depends(get_db),
):
    # Compatibility endpoint retained for existing clients.
    await _issue_reset_token_for_email(email, db)
    return {"message": PASSWORD_RESET_MESSAGE}


@router.post("/reset-password/confirm", response_model=MessageResponse)
async def confirm_password_reset(
    payload: PasswordResetConfirm,
    db: AsyncSession = Depends(get_db),
):
    token_payload = decode_reset_token(payload.token)
    target_uuid = _parse_user_id(token_payload.get("sub"))

    result = await db.execute(select(User).where(User.id == target_uuid))
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(status_code=400, detail="Invalid password reset request")

    if verify_password(payload.new_password, user.hashed_password):
        raise HTTPException(status_code=400, detail="New password must be different")

    user.hashed_password = hash_password(payload.new_password)
    await db.commit()
    await db.refresh(user)
    return {"message": "Password has been reset successfully"}

@router.get("/profile", response_model=UserResponse)
async def get_user_profile(
    user_id: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    current_user_id, is_superuser = _resolve_auth_context(current_user)
    target_user_id = user_id or current_user_id

    if target_user_id != current_user_id and not is_superuser:
        raise HTTPException(status_code=403, detail="Not authorized to view this profile")

    target_uuid = _parse_user_id(target_user_id)
    result = await db.execute(select(User).where(User.id == target_uuid))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {"user": _serialize_user(user)}


@router.put("/profile", response_model=UserMessageResponse)
async def update_user_profile(
    payload: UserUpdate,
    user_id: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    current_user_id, is_superuser = _resolve_auth_context(current_user)
    target_user_id = user_id or current_user_id

    if target_user_id != current_user_id and not is_superuser:
        raise HTTPException(status_code=403, detail="Not authorized to update this profile")

    target_uuid = _parse_user_id(target_user_id)
    result = await db.execute(select(User).where(User.id == target_uuid))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = payload.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(status_code=400, detail="No updatable fields provided")

    if update_data.get("password"):
        user.hashed_password = hash_password(update_data.pop("password"))
    else:
        update_data.pop("password", None)

    for field, value in update_data.items():
        setattr(user, field, value)

    await db.commit()
    await db.refresh(user)
    return {"message": "User profile updated successfully", "user": _serialize_user(user)}

@router.delete("/delete-account", response_model=MessageResponse)
async def delete_user_account(
    payload: UserDelete,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not payload.confirm:
        raise HTTPException(status_code=400, detail="Deletion confirmation is required")

    if payload.email.lower() != current_user.email.lower():
        raise HTTPException(status_code=403, detail="Email does not match the authenticated user")

    if not current_user.is_active:
        revoke_access_token(token)
        return {"message": "User account is already deactivated"}

    current_user.is_active = False
    current_user.hashed_password = hash_password(str(uuid4()))

    await db.commit()
    await db.refresh(current_user)
    revoke_access_token(token)
    return {"message": "User account deactivated successfully"}