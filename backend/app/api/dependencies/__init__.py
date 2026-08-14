"""Dependency injection layer for FastAPI routes (Auth, DB, Permissions)."""

from app.database.session import get_db

__all__ = ["get_db"]
