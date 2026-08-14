"""Pytest configuration and shared test fixtures."""

import os
import tempfile
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.core.constants import UserRole
from app.core.security import hash_password
from app.database.base import Base
from app.database.session import get_db
from app.main import app
from app.models.user import User

# Use in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Fixture providing a clean in-memory database session for each test."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Fixture providing a FastAPI TestClient with DB session override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def admin_user(db_session):
    """Creates and returns an active ADMIN user."""
    admin = User(
        email="admin_test@example.com",
        full_name="Admin Test User",
        hashed_password=hash_password("adminpassword123"),
        role=UserRole.ADMIN,
        is_active=True,
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    return admin


@pytest.fixture(scope="function")
def analyst_user(db_session):
    """Creates and returns an active ANALYST user."""
    analyst = User(
        email="analyst_test@example.com",
        full_name="Analyst Test User",
        hashed_password=hash_password("analystpassword123"),
        role=UserRole.ANALYST,
        is_active=True,
    )
    db_session.add(analyst)
    db_session.commit()
    db_session.refresh(analyst)
    return analyst


@pytest.fixture(scope="function")
def admin_headers(client, admin_user):
    """Returns authorization headers for an authenticated ADMIN."""
    response = client.post(
        "/api/v1/auth/login",
        data={"username": admin_user.email, "password": "adminpassword123"},
    )
    token = response.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="function")
def analyst_headers(client, analyst_user):
    """Returns authorization headers for an authenticated ANALYST."""
    response = client.post(
        "/api/v1/auth/login",
        data={"username": analyst_user.email, "password": "analystpassword123"},
    )
    token = response.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="function")
def sample_csv_content():
    """Generates standard CSV content with typical business columns."""
    return (
        "CustomerID,Order Date,Revenue Amount,Order Status,Product Category\n"
        "C001,2026-01-15,150.50,completed,Electronics\n"
        "C002,2026-01-16,230.00,completed,Home\n"
        "C003,2026-01-17,45.00,returned,Apparel\n"
        "C004,2026-01-18,310.25,completed,Electronics\n"
        "C005,2026-01-19,89.90,pending,Home\n"
    ).encode("utf-8")


@pytest.fixture(scope="function", autouse=True)
def seed_metric_defs(db_session):
    """Automatically seeds default metric definitions into the test database."""
    from seed_metrics import DEFAULT_METRIC_DEFINITIONS
    from app.models.metric_definition import MetricDefinition
    for item in DEFAULT_METRIC_DEFINITIONS:
        m = MetricDefinition(
            name=item["name"],
            metric_key=item["metric_key"],
            metric_category=item["metric_category"],
            required_field=item["required_field"],
            formula=item["formula"],
            description=item["description"],
            is_active=True,
        )
        db_session.add(m)
    db_session.commit()

