from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import ExpiredSignatureError, JWTError, jwt
from passlib.context import CryptContext
from pydantic import Field, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.db import get_db
from db.models import User

class AuthSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    JWT_SECRET_KEY: str = Field(..., min_length=32)
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(60 * 72, gt=0)  # 3 days
    JWT_RESET_TOKEN_EXPIRE_MINUTES: int = Field(30, gt=0)

try:
    auth_settings = AuthSettings()
except ValidationError as exc:
    raise RuntimeError(f"Invalid auth settings: {exc}") from exc

pwd_context = CryptContext(schemes=["bcrypt_sha256", "bcrypt"], deprecated="auto")
 
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
_revoked_access_tokens: dict[str, int] = {}


def _credentials_exception(detail: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def _utc_ts_now() -> int:
    return int(datetime.now(timezone.utc).timestamp())


def _cleanup_revoked_tokens() -> None:
    now_ts = _utc_ts_now()
    expired_tokens = [token for token, exp_ts in _revoked_access_tokens.items() if exp_ts <= now_ts]
    for token in expired_tokens:
        _revoked_access_tokens.pop(token, None)

def hash_password(password: str) -> str:
    # bcrypt_sha256 safely handles long and unicode passwords.
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: int | None = None) -> str:
    user_id = data.get("user_id")
    if not user_id:
        raise ValueError("user_id is required to create an access token")

    to_encode = data.copy()
    expire_minutes = expires_delta or auth_settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    expire = datetime.now(timezone.utc) + timedelta(minutes=expire_minutes)
    to_encode.update({"exp": expire, "sub": str(user_id), "type": "access"})
    return jwt.encode(to_encode, auth_settings.JWT_SECRET_KEY, algorithm=auth_settings.JWT_ALGORITHM)


def create_reset_token(user_id: str, expires_delta: int | None = None) -> str:
    expire_minutes = expires_delta or auth_settings.JWT_RESET_TOKEN_EXPIRE_MINUTES
    expire = datetime.now(timezone.utc) + timedelta(minutes=expire_minutes)
    payload = {"exp": expire, "sub": str(user_id), "type": "reset"}
    return jwt.encode(payload, auth_settings.JWT_SECRET_KEY, algorithm=auth_settings.JWT_ALGORITHM)

def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, auth_settings.JWT_SECRET_KEY, algorithms=[auth_settings.JWT_ALGORITHM])
        if payload.get("type") != "access" or payload.get("sub") is None:
            raise _credentials_exception("Invalid token payload")
        return payload
    except ExpiredSignatureError:
        raise _credentials_exception("Token has expired")
    except JWTError:
        raise _credentials_exception("Invalid token")


def decode_reset_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, auth_settings.JWT_SECRET_KEY, algorithms=[auth_settings.JWT_ALGORITHM])
        if payload.get("type") != "reset" or payload.get("sub") is None:
            raise _credentials_exception("Invalid reset token payload")
        return payload
    except ExpiredSignatureError:
        raise _credentials_exception("Reset token has expired")
    except JWTError:
        raise _credentials_exception("Invalid reset token")


def revoke_access_token(token: str) -> None:
    token_exp_ts = _utc_ts_now() + (auth_settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    try:
        unverified: dict[str, Any] = jwt.get_unverified_claims(token)
        exp_claim = unverified.get("exp")
        if isinstance(exp_claim, (int, float)):
            token_exp_ts = int(exp_claim)
    except JWTError:
        # If we cannot decode claims, block briefly so replay attempts still fail.
        token_exp_ts = _utc_ts_now() + 300

    _cleanup_revoked_tokens()
    _revoked_access_tokens[token] = token_exp_ts


def is_access_token_revoked(token: str) -> bool:
    _cleanup_revoked_tokens()
    return token in _revoked_access_tokens
    
async def fetch_user_from_db(user_id: str, db: AsyncSession = Depends(get_db)) -> User:
    try:
        user_uuid = UUID(user_id)
    except (TypeError, ValueError):
        raise _credentials_exception("Invalid token payload")

    result = await db.execute(select(User).where(User.id == user_uuid))
    user = result.scalar_one_or_none()

    if user is None:
        raise _credentials_exception("User not found")

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user account")

    return user

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> User:
    if is_access_token_revoked(token):
        raise _credentials_exception("Token has been revoked")

    payload = decode_access_token(token)
    user_id = payload.get("sub")
    if user_id is None:
        raise _credentials_exception("Invalid token payload")
    return await fetch_user_from_db(user_id, db)
