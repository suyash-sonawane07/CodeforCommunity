"""Auth boundary — DEMO PLACEHOLDER ONLY.

SCAFFOLD: implements just enough for the PRD demo-login flow (POST /auth/login →
role-scoped token; PRD §5 roles). This is NOT production authentication. RBAC
enforcement hooks exist (`require_role`) but only check claims, with dev-only secrets.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from app.core.config import get_settings

_settings = get_settings()

ROLE_HIERARCHY = ["citizen", "analyst", "reviewer", "decision_maker", "admin"]

bearer_scheme = HTTPBearer(auto_error=False)


def create_access_token(subject: str, role: str) -> str:
    """Issue a demo role-scoped JWT. TODO(PRD FR-058+): replace with real auth in Phase 3."""
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
    except JWTError as exc:  # pragma: no cover - trivial
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": {"code": "UNAUTHORIZED", "message": "Invalid or expired token"}},
        ) from exc


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
) -> dict[str, Any]:
    """Dependency: require a valid demo token. Public endpoints simply don't use it."""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": {"code": "UNAUTHORIZED", "message": "Missing bearer token"}},
        )
    claims = decode_token(credentials.credentials)
    return {"subject": claims.get("sub"), "role": claims.get("role", "citizen")}


def require_role(minimum: str):
    """RBAC placeholder: enforce the PRD §5 role hierarchy at the API layer."""

    def _checker(user: dict[str, Any] = Depends(get_current_user)) -> dict[str, Any]:
        have, need = (
            ROLE_HIERARCHY.index(user.get("role", "citizen")),
            ROLE_HIERARCHY.index(minimum),
        )
        if have < need:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"error": {"code": "FORBIDDEN", "message": f"Requires role {minimum}+"}},
            )
        return user

    return _checker
