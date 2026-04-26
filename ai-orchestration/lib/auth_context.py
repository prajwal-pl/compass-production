from datetime import datetime, timedelta, timezone
import hashlib
from typing import Any
from uuid import UUID, uuid4

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
from lib.security_store import security_store

class AuthSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    JWT_SECRET_KEY: str = Field(..., min_length=32)
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(60 * 72, gt=0)  # 3 days
    JWT_REFRESH_TOKEN_EXPIRE_MINUTES: int = Field(60 * 24 * 30, gt=0)  # 30 days
    JWT_RESET_TOKEN_EXPIRE_MINUTES: int = Field(30, gt=0)

try:
    auth_settings = AuthSettings()
except ValidationError as exc:
    raise RuntimeError(f"Invalid auth settings: {exc}") from exc

pwd_context = CryptContext(schemes=["bcrypt_sha256", "bcrypt"], deprecated="auto")
 
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def _credentials_exception(detail: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def _utc_ts_now() -> int:
    return int(datetime.now(timezone.utc).timestamp())


def _token_fingerprint(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _safe_unverified_exp_ts(token: str, fallback_ttl_seconds: int = 300) -> int:
    try:
        unverified: dict[str, Any] = jwt.get_unverified_claims(token)
        exp_claim = unverified.get("exp")
        if isinstance(exp_claim, (int, float)):
            return int(exp_claim)
    except JWTError:
        pass

    return _utc_ts_now() + fallback_ttl_seconds

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


def create_refresh_token(user_id: str, expires_delta: int | None = None) -> str:
    expire_minutes = expires_delta or auth_settings.JWT_REFRESH_TOKEN_EXPIRE_MINUTES
    expire = datetime.now(timezone.utc) + timedelta(minutes=expire_minutes)
    payload = {
        "exp": expire,
        "sub": str(user_id),
        "type": "refresh",
        "jti": str(uuid4()),
    }
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


def decode_refresh_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, auth_settings.JWT_SECRET_KEY, algorithms=[auth_settings.JWT_ALGORITHM])
        if payload.get("type") != "refresh" or payload.get("sub") is None:
            raise _credentials_exception("Invalid refresh token payload")
        if payload.get("jti") is None:
            raise _credentials_exception("Invalid refresh token id")
        return payload
    except ExpiredSignatureError:
        raise _credentials_exception("Refresh token has expired")
    except JWTError:
        raise _credentials_exception("Invalid refresh token")


async def revoke_access_token(token: str) -> None:
    token_exp_ts = _safe_unverified_exp_ts(
        token,
        fallback_ttl_seconds=auth_settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    token_fp = _token_fingerprint(token)
    await security_store.revoke_access_token(token_fp, token_exp_ts)


async def is_access_token_revoked(token: str) -> bool:
    token_fp = _token_fingerprint(token)
    return await security_store.is_access_token_revoked(token_fp)


async def consume_refresh_token_jti(jti: str, token_exp_ts: int) -> bool:
    return await security_store.consume_refresh_token_jti(jti, token_exp_ts)


async def enforce_rate_limit(
    scope: str,
    identifier: str,
    max_attempts: int,
    window_seconds: int,
) -> None:
    allowed, _remaining, retry_after = await security_store.hit_rate_limit(
        scope=scope,
        key=identifier,
        max_attempts=max_attempts,
        window_seconds=window_seconds,
    )

    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests. Please retry later.",
            headers={"Retry-After": str(retry_after)},
        )


async def enforce_lockout(
    scope: str,
    identifier: str,
    detail: str,
) -> None:
    is_locked, retry_after = await security_store.get_lockout_status(
        scope=scope,
        key=identifier,
    )

    if is_locked:
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail=detail,
            headers={"Retry-After": str(max(1, retry_after))},
        )


async def register_auth_failure(
    scope: str,
    identifier: str,
    threshold: int,
    failure_window_seconds: int,
    lockout_seconds: int,
) -> tuple[bool, int]:
    return await security_store.register_auth_failure(
        scope=scope,
        key=identifier,
        threshold=threshold,
        failure_window_seconds=failure_window_seconds,
        lockout_seconds=lockout_seconds,
    )


async def clear_auth_failures(scope: str, identifier: str) -> None:
    await security_store.clear_auth_failures(scope=scope, key=identifier)
    
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
    if await is_access_token_revoked(token):
        raise _credentials_exception("Token has been revoked")

    payload = decode_access_token(token)
    user_id = payload.get("sub")
    if user_id is None:
        raise _credentials_exception("Invalid token payload")
    return await fetch_user_from_db(user_id, db)
