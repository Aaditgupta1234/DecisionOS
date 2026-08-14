"""SQLAlchemy database connection setup and session maker with fallback support."""

import logging
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings
from app.database.base import Base

logger = logging.getLogger("decisionos")

connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

try:
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
        connect_args=connect_args,
    )
    # Test connection eagerly
    with engine.connect() as conn:
        pass
except Exception as e:
    logger.warning(f"Could not connect using primary DATABASE_URL ({e}). Falling back to SQLite.")
    sqlite_url = "sqlite:///./decisionos.db"
    engine = create_engine(
        sqlite_url,
        connect_args={"check_same_thread": False},
    )
    # Ensure tables exist on local SQLite fallback
    import app.models  # noqa: F401
    Base.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Dependency generator that yields a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
