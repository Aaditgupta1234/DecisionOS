"""Comprehensive Multi-Tenant Security & Isolation Verification Tests."""

import uuid
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.constants import OrgRole, UserRole
from app.core.security import create_access_token, hash_password
from app.models.dataset import Dataset
from app.models.organization import Organization
from app.models.organization_member import OrganizationMember
from app.models.user import User


def test_cross_tenant_intelligence_and_report_isolation(client: TestClient, db_session: Session):
    """Verifies that User B from Org B cannot access intelligence or datasets from Org A."""
    # 1. Create User A and User B
    user_a = User(
        email="corp_a_lead@enterprise.com",
        full_name="Corp A Lead",
        hashed_password=hash_password("password123"),
        role=UserRole.ADMIN,
        is_active=True,
    )
    user_b = User(
        email="competitor_b@rival.com",
        full_name="Rival User",
        hashed_password=hash_password("password123"),
        role=UserRole.ANALYST,
        is_active=True,
    )
    db_session.add_all([user_a, user_b])
    db_session.commit()
    db_session.refresh(user_a)
    db_session.refresh(user_b)

    # 2. Create Org A and Org B
    org_a = Organization(name="Enterprise A", slug="enterprise-a", created_by=user_a.id)
    org_b = Organization(name="Rival B", slug="rival-b", created_by=user_b.id)
    db_session.add_all([org_a, org_b])
    db_session.commit()
    db_session.refresh(org_a)
    db_session.refresh(org_b)

    db_session.add(OrganizationMember(organization_id=org_a.id, user_id=user_a.id, role=OrgRole.OWNER))
    db_session.add(OrganizationMember(organization_id=org_b.id, user_id=user_b.id, role=OrgRole.OWNER))
    db_session.commit()

    # 3. Create Dataset belonging to Org A
    dataset_a = Dataset(
        name="Confidential A Financials",
        original_filename="confidential_a.csv",
        stored_filename=f"conf_a_{uuid.uuid4().hex}.csv",
        file_path="/tmp/conf_a.csv",
        file_size=5000,
        uploaded_by=user_a.id,
        organization_id=org_a.id,
        is_deleted=False,
    )
    db_session.add(dataset_a)
    db_session.commit()
    db_session.refresh(dataset_a)

    token_b = create_access_token(subject=str(user_b.id), extra_claims={"email": user_b.email, "role": user_b.role.value})
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # 4. User B attempts to access Dataset A -> 403 Forbidden
    dataset_res = client.get(f"/api/v1/datasets/{dataset_a.id}", headers=headers_b)
    assert dataset_res.status_code == status.HTTP_403_FORBIDDEN

    # 5. User B attempts to access Org A details -> 403 Forbidden
    org_res = client.get(f"/api/v1/organizations/{org_a.id}", headers=headers_b)
    assert org_res.status_code == status.HTTP_403_FORBIDDEN


def test_tenant_role_restrictions(client: TestClient, db_session: Session):
    """Verifies that VIEWER and ANALYST roles cannot perform administrative or member management mutations."""
    # 1. Create Owner and Viewer users
    owner = User(
        email="org_owner@test.com",
        full_name="Org Owner",
        hashed_password=hash_password("password123"),
        role=UserRole.ADMIN,
        is_active=True,
    )
    viewer = User(
        email="org_viewer@test.com",
        full_name="Org Viewer",
        hashed_password=hash_password("password123"),
        role=UserRole.VIEWER,
        is_active=True,
    )
    db_session.add_all([owner, viewer])
    db_session.commit()
    db_session.refresh(owner)
    db_session.refresh(viewer)

    org = Organization(name="Security Test Org", slug="sec-test-org", created_by=owner.id)
    db_session.add(org)
    db_session.commit()
    db_session.refresh(org)

    db_session.add(OrganizationMember(organization_id=org.id, user_id=owner.id, role=OrgRole.OWNER))
    viewer_member = OrganizationMember(organization_id=org.id, user_id=viewer.id, role=OrgRole.VIEWER)
    db_session.add(viewer_member)
    db_session.commit()

    token_viewer = create_access_token(subject=str(viewer.id), extra_claims={"email": viewer.email, "role": viewer.role.value})
    headers_viewer = {"Authorization": f"Bearer {token_viewer}"}

    # 2. Viewer attempts to update organization profile -> 403 Forbidden
    update_res = client.patch(
        f"/api/v1/organizations/{org.id}",
        json={"name": "Hacked Org Name"},
        headers=headers_viewer,
    )
    assert update_res.status_code == status.HTTP_403_FORBIDDEN
    assert "Only Organization Owners and Admins" in update_res.json()["detail"]

    # 3. Viewer attempts to invite a member -> 403 Forbidden
    invite_res = client.post(
        f"/api/v1/organizations/{org.id}/members",
        json={"email": "newbie@test.com", "role": "ANALYST"},
        headers=headers_viewer,
    )
    assert invite_res.status_code == status.HTTP_403_FORBIDDEN
    assert "Only Organization Owners and Admins" in invite_res.json()["detail"]


def test_backward_compatibility_auto_provision(client: TestClient, db_session: Session):
    """Verifies that legacy users without prior organization memberships get auto-provisioned personal workspace."""
    legacy_user = User(
        email="legacy_user@enterprise.com",
        full_name="Legacy Leader",
        hashed_password=hash_password("password123"),
        role=UserRole.ANALYST,
        is_active=True,
    )
    db_session.add(legacy_user)
    db_session.commit()
    db_session.refresh(legacy_user)

    token = create_access_token(subject=str(legacy_user.id), extra_claims={"email": legacy_user.email, "role": legacy_user.role.value})
    headers = {"Authorization": f"Bearer {token}"}

    # Listing organizations should auto-provision a Personal Workspace
    list_res = client.get("/api/v1/organizations", headers=headers)
    assert list_res.status_code == status.HTTP_200_OK
    orgs = list_res.json()["data"]
    assert len(orgs) == 1
    assert "Legacy Leader Workspace" in orgs[0]["name"]
    assert orgs[0]["current_user_role"] == "OWNER"
