"""Shared API dependencies (auth boundary, DB session re-export)."""

from app.core.security import get_current_user, require_user, require_supervisor
from app.db.session import get_db

__all__ = ["get_current_user", "require_user", "require_supervisor", "get_db"]
