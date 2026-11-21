from datetime import datetime, timedelta, timezone
import uuid
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from pwdlib import PasswordHash
from sqlalchemy.orm import Session
from .config import settings
from .database import get_db
from .models import User

password_hash = PasswordHash.recommended()
bearer = HTTPBearer(auto_error=False)

def hash_password(password: str) -> str:
    return password_hash.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    return password_hash.verify(password, hashed)

def create_access_token(user: User) -> str:
    if not settings.jwt_secret_key or len(settings.jwt_secret_key) < 32:
        raise RuntimeError("JWT_SECRET_KEY must be set to a random value of at least 32 characters")
    now = datetime.now(timezone.utc)
    payload = {"sub": str(user.id), "iat": now, "exp": now + timedelta(minutes=settings.access_token_minutes)}
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)

def create_purpose_token(user: User, purpose: str, minutes: int) -> str:
    if not settings.jwt_secret_key or len(settings.jwt_secret_key) < 32:
        raise RuntimeError("JWT_SECRET_KEY must be set to a random value of at least 32 characters")
    now = datetime.now(timezone.utc)
    payload = {"sub": str(user.id), "purpose": purpose, "iat": now, "exp": now + timedelta(minutes=minutes)}
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)

def get_user_with_purpose(purpose: str):
    def dependency(credentials: HTTPAuthorizationCredentials | None = Depends(bearer), db: Session = Depends(get_db)) -> User:
        unauthorized = HTTPException(status_code=401, detail="Invalid or expired authorization")
        if not credentials or not settings.jwt_secret_key:
            raise unauthorized
        try:
            payload = jwt.decode(credentials.credentials, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
            if payload.get("purpose") != purpose:
                raise unauthorized
            user = db.get(User, uuid.UUID(payload.get("sub", "")))
        except (JWTError, ValueError, TypeError):
            raise unauthorized
        if not user or not user.is_active:
            raise unauthorized
        return user
    return dependency

def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_db)
) -> User:
    unauthorized = HTTPException(status_code=401, detail="Sign in required", headers={"WWW-Authenticate": "Bearer"})
    if not credentials or not settings.jwt_secret_key:
        raise unauthorized
    try:
        payload = jwt.decode(credentials.credentials, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        if payload.get("purpose") is not None:
            raise unauthorized
        user_id = payload.get("sub")
        if not user_id:
            raise unauthorized
        user = db.get(User, uuid.UUID(user_id))
    except (JWTError, ValueError):
        raise unauthorized
    if not user or not user.is_active or user.must_change_password or not user.security_setup_complete:
        raise unauthorized
    return user

def require_read(user: User = Depends(get_current_user)) -> User:
    return user

def require_write(user: User = Depends(get_current_user)) -> User:
    if not (user.is_admin or user.privilege == "write"):
        raise HTTPException(status_code=403, detail="Write privilege required")
    return user

def require_admin(user: User = Depends(get_current_user)) -> User:
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Administrator access required")
    return user
