import os

from pydantic_settings import BaseSettings
from passlib.context import CryptContext
from fastapi import Depends, HTTPException
from datetime import datetime, timedelta
from jose import jwt
from fastapi.security import OAuth2PasswordBearer
from db.db import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.models import User

class AuthSettings(BaseSettings):
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY")
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 72  # 3 days

auth_settings = AuthSettings()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
 
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
  # Placeholder for OAuth2PasswordBearer, to be initialized in main.py

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: int = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expires_delta or auth_settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "sub": str(data.get("user_id")), "type": "access"})
    return jwt.encode(to_encode, auth_settings.JWT_SECRET_KEY, algorithm=auth_settings.JWT_ALGORITHM)

def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, auth_settings.JWT_SECRET_KEY, algorithms=[auth_settings.JWT_ALGORITHM])
        if payload.get("type") != "access" and payload.get("sub") is None:
            raise HTTPException(status_code=401, detail="Invalid token type")
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
async def fetch_user_from_db(user_id: str, db: AsyncSession = Depends(get_db)):

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    return {"user": user}

async def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    return await fetch_user_from_db(user_id)