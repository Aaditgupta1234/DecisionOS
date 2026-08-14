"""Unit and integration tests for authentication and RBAC endpoints."""

from app.core.constants import UserRole
from app.core.security import hash_password
from app.models.user import User


def test_user_registration_success(client):
    """Test public registration creates user with ANALYST role."""
    payload = {
        "email": "analyst@example.com",
        "full_name": "Test Analyst",
        "password": "password123",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    res_data = response.json()
    assert res_data["success"] is True
    data = res_data["data"]
    assert data["email"] == "analyst@example.com"
    assert data["full_name"] == "Test Analyst"
    assert data["role"] == UserRole.ANALYST
    assert data["is_active"] is True
    assert "id" in data


def test_user_registration_duplicate_email(client):
    """Test registration rejects duplicate emails."""
    payload = {
        "email": "duplicate@example.com",
        "full_name": "First User",
        "password": "password123",
    }
    response1 = client.post("/api/v1/auth/register", json=payload)
    assert response1.status_code == 201

    # Second registration with same email
    response2 = client.post("/api/v1/auth/register", json=payload)
    assert response2.status_code == 400
    assert "already exists" in response2.json()["detail"]


def test_login_success_and_token(client):
    """Test login with valid credentials returns JWT token."""
    # Register user first
    reg_payload = {
        "email": "user@example.com",
        "full_name": "Login User",
        "password": "password123",
    }
    client.post("/api/v1/auth/register", json=reg_payload)

    # Login via form-data
    login_data = {
        "username": "user@example.com",
        "password": "password123",
    }
    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 200
    res_json = response.json()
    assert res_json["success"] is True
    token_data = res_json["data"]
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"


def test_login_failure_invalid_credentials(client):
    """Test login fails with incorrect password."""
    reg_payload = {
        "email": "wrongpass@example.com",
        "full_name": "User",
        "password": "password123",
    }
    client.post("/api/v1/auth/register", json=reg_payload)

    login_data = {
        "username": "wrongpass@example.com",
        "password": "wrongpassword",
    }
    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 401


def test_get_current_user_profile(client):
    """Test /me endpoint returns authenticated user profile."""
    # Register and login
    reg_payload = {
        "email": "profile@example.com",
        "full_name": "Profile User",
        "password": "password123",
    }
    client.post("/api/v1/auth/register", json=reg_payload)

    login_resp = client.post(
        "/api/v1/auth/login",
        data={"username": "profile@example.com", "password": "password123"},
    )
    token = login_resp.json()["data"]["access_token"]

    # Fetch profile with Bearer header
    headers = {"Authorization": f"Bearer {token}"}
    me_resp = client.get("/api/v1/auth/me", headers=headers)
    assert me_resp.status_code == 200
    me_data = me_resp.json()["data"]
    assert me_data["email"] == "profile@example.com"
    assert me_data["full_name"] == "Profile User"


def test_auth_health_endpoint(client):
    """Test protected /auth/health endpoint returns token payload info."""
    reg_payload = {
        "email": "healthuser@example.com",
        "full_name": "Health User",
        "password": "password123",
    }
    client.post("/api/v1/auth/register", json=reg_payload)

    login_resp = client.post(
        "/api/v1/auth/login",
        data={"username": "healthuser@example.com", "password": "password123"},
    )
    token = login_resp.json()["data"]["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    health_resp = client.get("/api/v1/auth/health", headers=headers)
    assert health_resp.status_code == 200
    h_data = health_resp.json()
    assert h_data["authenticated"] is True
    assert h_data["email"] == "healthuser@example.com"
    assert h_data["role"] == UserRole.ANALYST


def test_rbac_admin_route_guard(client, db_session):
    """Test RBAC admin route: Analyst gets 403, Admin gets 200."""
    # 1. Create Analyst User
    client.post(
        "/api/v1/auth/register",
        json={"email": "analyst_rbac@example.com", "full_name": "Analyst", "password": "password123"},
    )
    analyst_token = client.post(
        "/api/v1/auth/login",
        data={"username": "analyst_rbac@example.com", "password": "password123"},
    ).json()["data"]["access_token"]

    # 2. Create Admin User directly in DB session
    admin = User(
        email="admin_rbac@example.com",
        full_name="Admin User",
        hashed_password=hash_password("adminpassword123"),
        role=UserRole.ADMIN,
        is_active=True,
    )
    db_session.add(admin)
    db_session.commit()

    admin_token = client.post(
        "/api/v1/auth/login",
        data={"username": "admin_rbac@example.com", "password": "adminpassword123"},
    ).json()["data"]["access_token"]

    # Test Analyst Access (Expected 403 Forbidden)
    analyst_resp = client.get(
        "/api/v1/auth/admin-only",
        headers={"Authorization": f"Bearer {analyst_token}"},
    )
    assert analyst_resp.status_code == 403

    # Test Admin Access (Expected 200 OK)
    admin_resp = client.get(
        "/api/v1/auth/admin-only",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert admin_resp.status_code == 200
    assert admin_resp.json()["data"]["admin"] is True
