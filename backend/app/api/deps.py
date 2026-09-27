"""Shared API dependencies (auth boundary, DB session re-export)."""

from app.core.security import get_current_user, require_role
from app.db.session import get_db

__all__ = ["get_current_user", "require_role", "get_db"]
