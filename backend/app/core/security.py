"""Auth boundary — supports both RBAC hierarchy and user/supervisor roles."""

from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import get_db
from app.models.user import User

_settings = get_settings()

DEMO_USERS = {
    "analyst@civicpulse.dev": "analyst",
    "reviewer@civicpulse.dev": "reviewer",
    "decision@civicpulse.dev": "decision_maker",
    "admin@civicpulse.dev": "admin",
}

ROLE_HIERARCHY = ["citizen", "user", "analyst", "reviewer", "decision_maker", "supervisor", "admin"]

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

bearer_scheme = HTTPBearer(auto_error=False)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(subject: str, role: str) -> str:
    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "sub": subject,
        "role": role,
        "iat": now,
        "exp": now + timedelta(minutes=_settings.JWT_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, _settings.JWT_SECRET, algorithm=_settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict[str, Any]:
    try:
        return jwt.decode(token, _settings.JWT_SECRET, algorithms=[_settings.JWT_ALGORITHM])
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": {"code": "UNAUTHORIZED", "message": "Invalid or expired token"}},
        ) from exc


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": {"code": "UNAUTHORIZED", "message": "Missing bearer token"}},
        )
    claims = decode_token(credentials.credentials)
    email = claims.get("sub")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": {"code": "UNAUTHORIZED", "message": "Invalid token subject"}},
        )
    user = db.scalar(select(User).where(User.email == email.lower()))
    if not user:
        if email.lower() in DEMO_USERS:
            role = claims.get("role", DEMO_USERS[email.lower()])
            user = User(email=email.lower(), name=email.split("@")[0].title(), role=role)
            db.add(user)
            db.commit()
            db.refresh(user)
            return user
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": {"code": "UNAUTHORIZED", "message": "User not found"}},
        )
    return user


def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> Optional[User]:
    if credentials is None:
        return None
    try:
        claims = decode_token(credentials.credentials)
        email = claims.get("sub")
        if not email:
            return None
        user = db.scalar(select(User).where(User.email == email.lower()))
        if not user and email.lower() in DEMO_USERS:
            role = claims.get("role", DEMO_USERS[email.lower()])
            user = User(email=email.lower(), name=email.split("@")[0].title(), role=role)
            db.add(user)
            db.commit()
            db.refresh(user)
        return user
    except Exception:
        return None


def require_user(user: User = Depends(get_current_user)) -> User:
    return user


def require_role(minimum: str):
    def _checker(user: User = Depends(get_current_user)) -> User:
        user_role = user.role or "citizen"
        have = ROLE_HIERARCHY.index(user_role) if user_role in ROLE_HIERARCHY else 0
        need = ROLE_HIERARCHY.index(minimum) if minimum in ROLE_HIERARCHY else 0
        if have < need:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"error": {"code": "FORBIDDEN", "message": f"Requires role {minimum}+"}},
            )
        return user

    return _checker


def require_supervisor(user: User = Depends(get_current_user)) -> User:
    if user.role not in ["supervisor", "admin", "reviewer", "decision_maker"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": {"code": "FORBIDDEN", "message": "Requires supervisor role"}},
        )
    return user
