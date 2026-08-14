"""Integration & Security Tests for Multi-Tenant SaaS Organizations, Roles, and Isolation."""

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


def test_organization_crud_and_membership(client: TestClient, db_session: Session):
    """Verifies organization creation, listing, member invite, role change, and last owner protection."""
    # 1. Create User 1 (Alice - Owner) and User 2 (Bob - Member)
    user1 = User(
        email="alice@company.com",
        full_name="Alice Owner",
        hashed_password=hash_password("password123"),
        role=UserRole.ADMIN,
        is_active=True,
    )
    user2 = User(
        email="bob@company.com",
        full_name="Bob Analyst",
        hashed_password=hash_password("password123"),
        role=UserRole.ANALYST,
        is_active=True,
    )
    db_session.add_all([user1, user2])
    db_session.commit()
    db_session.refresh(user1)
    db_session.refresh(user2)

    token1 = create_access_token(subject=str(user1.id), extra_claims={"email": user1.email, "role": user1.role.value})
    token2 = create_access_token(subject=str(user2.id), extra_claims={"email": user2.email, "role": user2.role.value})

    headers1 = {"Authorization": f"Bearer {token1}"}
    headers2 = {"Authorization": f"Bearer {token2}"}

    # 2. Alice creates Organization 'Acme Corp'
    create_res = client.post(
        "/api/v1/organizations",
        json={"name": "Acme Corp", "slug": "acme-corp"},
        headers=headers1,
    )
    assert create_res.status_code == status.HTTP_201_CREATED
    org_data = create_res.json()["data"]
    org_id = org_data["id"]
    assert org_data["name"] == "Acme Corp"
    assert org_data["current_user_role"] == "OWNER"

    # 3. Alice lists her organizations
    list_res = client.get("/api/v1/organizations", headers=headers1)
    assert list_res.status_code == status.HTTP_200_OK
    assert len(list_res.json()["data"]) >= 1

    # 4. Get Current Organization
    curr_res = client.get("/api/v1/organizations/current", headers=headers1)
    assert curr_res.status_code == status.HTTP_200_OK
    assert curr_res.json()["data"]["name"] == "Acme Corp"

    # 5. Alice adds Bob to Acme Corp with ANALYST role
    add_res = client.post(
        f"/api/v1/organizations/{org_id}/members",
        json={"email": "bob@company.com", "role": "ANALYST"},
        headers=headers1,
    )
    assert add_res.status_code == status.HTTP_201_CREATED
    bob_member_id = add_res.json()["data"]["id"]
    assert add_res.json()["data"]["role"] == "ANALYST"

    # 6. Duplicate member invite rejection (409)
    dup_res = client.post(
        f"/api/v1/organizations/{org_id}/members",
        json={"email": "bob@company.com", "role": "ANALYST"},
        headers=headers1,
    )
    assert dup_res.status_code == status.HTTP_409_CONFLICT

    # 7. Alice updates Bob's role to ADMIN
    update_role_res = client.patch(
        f"/api/v1/organizations/{org_id}/members/{bob_member_id}",
        json={"role": "ADMIN"},
        headers=headers1,
    )
    assert update_role_res.status_code == status.HTTP_200_OK
    assert update_role_res.json()["data"]["role"] == "ADMIN"

    # 8. Last Owner Protection: Get Alice's membership ID and attempt to demote her
    members_res = client.get(f"/api/v1/organizations/{org_id}/members", headers=headers1)
    alice_member = next(m for m in members_res.json()["data"] if m["email"] == "alice@company.com")
    
    demote_res = client.patch(
        f"/api/v1/organizations/{org_id}/members/{alice_member['id']}",
        json={"role": "ANALYST"},
        headers=headers1,
    )
    assert demote_res.status_code == status.HTTP_400_BAD_REQUEST
    assert "Cannot demote the last remaining Organization Owner" in demote_res.json()["detail"]


def test_tenant_dataset_isolation(client: TestClient, db_session: Session):
    """Verifies that datasets belonging to Organization A cannot be accessed by users of Organization B."""
    # 1. Create Org A with User A (Owner)
    user_a = User(
        email="owner_a@orga.com",
        full_name="User A",
        hashed_password=hash_password("password123"),
        role=UserRole.ADMIN,
        is_active=True,
    )
    # 2. Create Org B with User B (Owner)
    user_b = User(
        email="owner_b@orgb.com",
        full_name="User B",
        hashed_password=hash_password("password123"),
        role=UserRole.ANALYST,
        is_active=True,
    )
    db_session.add_all([user_a, user_b])
    db_session.commit()
    db_session.refresh(user_a)
    db_session.refresh(user_b)

    org_a = Organization(name="Organization Alpha", slug="org-alpha", created_by=user_a.id)
    org_b = Organization(name="Organization Beta", slug="org-beta", created_by=user_b.id)
    db_session.add_all([org_a, org_b])
    db_session.commit()
    db_session.refresh(org_a)
    db_session.refresh(org_b)

    db_session.add(OrganizationMember(organization_id=org_a.id, user_id=user_a.id, role=OrgRole.OWNER))
    db_session.add(OrganizationMember(organization_id=org_b.id, user_id=user_b.id, role=OrgRole.OWNER))
    db_session.commit()

    # 3. Create Dataset belonging to Org A
    dataset_a = Dataset(
        name="Alpha Financials",
        original_filename="alpha.csv",
        stored_filename=f"alpha_{uuid.uuid4().hex}.csv",
        file_path="/tmp/alpha.csv",
        file_size=1000,
        uploaded_by=user_a.id,
        organization_id=org_a.id,
        is_deleted=False,
    )
    db_session.add(dataset_a)
    db_session.commit()
    db_session.refresh(dataset_a)

    token_b = create_access_token(subject=str(user_b.id), extra_claims={"email": user_b.email, "role": user_b.role.value})
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # 4. User B attempts to access Dataset A -> Must receive 403 FORBIDDEN
    access_res = client.get(f"/api/v1/datasets/{dataset_a.id}", headers=headers_b)
    assert access_res.status_code == status.HTTP_403_FORBIDDEN
    assert "Dataset belongs to an organization you are not a member of" in access_res.json()["detail"]
