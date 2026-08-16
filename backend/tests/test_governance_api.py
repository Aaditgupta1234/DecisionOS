"""Integration tests for Governance & Review REST APIs (Phase 12.5).

Tests Review and Action CRUD, filtering, state machine enforcement,
initiative & program governance detail endpoints, portfolio summary, multi-tenant isolation, and 401s.
"""

from datetime import datetime, timezone
import uuid
import pytest

from app.execution.constants import (
    ActionPriority,
    EscalationLevel,
    GovernanceActionStatus,
    GovernanceDecision,
    GovernanceReviewStatus,
    ReviewType,
)


def test_api_governance_review_and_action_crud(client, analyst_headers):
    """Tests complete review and action CRUD workflows via REST APIs."""
    # 1. Create Initiative
    init_res = client.post(
        "/api/v1/execution/initiatives",
        json={
            "title": "API Gateway Modernization",
            "description": "Modernize enterprise API gateway.",
            "objective": "Achieve high throughput governance.",
        },
        headers=analyst_headers,
    )
    assert init_res.status_code == 201
    init_id = init_res.json()["id"]

    # 2. Schedule Review
    rev_res = client.post(
        "/api/v1/execution/reviews",
        json={
            "initiative_id": init_id,
            "title": "Architecture Review 1",
            "review_type": ReviewType.GOVERNANCE_REVIEW.value,
            "scheduled_at": datetime.now(timezone.utc).isoformat(),
            "review_owner": "Architecture Board",
            "evidence_links": ["https://wiki.corp/arch-spec-1"],
        },
        headers=analyst_headers,
    )
    assert rev_res.status_code == 201
    review_id = rev_res.json()["id"]
    assert rev_res.json()["review_status"] == GovernanceReviewStatus.SCHEDULED.value
    assert rev_res.json()["evidence_links"] == ["https://wiki.corp/arch-spec-1"]

    # 3. Create Action under review
    act_res = client.post(
        "/api/v1/execution/actions",
        json={
            "review_id": review_id,
            "title": "Document Rate Limiting Strategy",
            "assigned_to": "Lead Engineer",
            "priority": ActionPriority.CRITICAL.value,
        },
        headers=analyst_headers,
    )
    assert act_res.status_code == 201
    action_id = act_res.json()["id"]
    assert act_res.json()["priority"] == ActionPriority.CRITICAL.value
    assert act_res.json()["status"] == GovernanceActionStatus.OPEN.value

    # 4. Get Review and verify action is nested
    get_rev = client.get(
        f"/api/v1/execution/reviews/{review_id}",
        headers=analyst_headers,
    )
    assert get_rev.status_code == 200
    assert len(get_rev.json()["actions"]) == 1
    assert get_rev.json()["actions"][0]["id"] == action_id

    # 5. List Reviews with filters
    list_revs = client.get(
        f"/api/v1/execution/reviews?initiative_id={init_id}&review_status={GovernanceReviewStatus.SCHEDULED.value}",
        headers=analyst_headers,
    )
    assert list_revs.status_code == 200
    assert list_revs.json()["total"] >= 1
    assert list_revs.json()["scheduled_count"] >= 1

    # 6. List Actions with filters
    list_acts = client.get(
        f"/api/v1/execution/actions?review_id={review_id}&priority={ActionPriority.CRITICAL.value}",
        headers=analyst_headers,
    )
    assert list_acts.status_code == 200
    assert list_acts.json()["total"] == 1
    assert list_acts.json()["open_count"] == 1

    # 7. Update Action Status (OPEN -> IN_PROGRESS -> COMPLETED)
    patch_act1 = client.patch(
        f"/api/v1/execution/actions/{action_id}",
        json={"status": GovernanceActionStatus.IN_PROGRESS.value},
        headers=analyst_headers,
    )
    assert patch_act1.status_code == 200

    patch_act2 = client.patch(
        f"/api/v1/execution/actions/{action_id}",
        json={"status": GovernanceActionStatus.COMPLETED.value},
        headers=analyst_headers,
    )
    assert patch_act2.status_code == 200
    assert patch_act2.json()["completed_at"] is not None

    # 8. Update Review Status (SCHEDULED -> IN_PROGRESS -> COMPLETED with Decision)
    patch_rev1 = client.patch(
        f"/api/v1/execution/reviews/{review_id}",
        json={"review_status": GovernanceReviewStatus.IN_PROGRESS.value},
        headers=analyst_headers,
    )
    assert patch_rev1.status_code == 200

    patch_rev2 = client.patch(
        f"/api/v1/execution/reviews/{review_id}",
        json={
            "review_status": GovernanceReviewStatus.COMPLETED.value,
            "decision": GovernanceDecision.APPROVED.value,
            "decision_rationale": "All architectural requirements satisfied.",
        },
        headers=analyst_headers,
    )
    assert patch_rev2.status_code == 200
    assert patch_rev2.json()["decision"] == GovernanceDecision.APPROVED.value
    assert patch_rev2.json()["decision_outcome"] == "POSITIVE"

    # 9. Delete Action
    act2_res = client.post(
        "/api/v1/execution/actions",
        json={
            "review_id": review_id,
            "title": "Temporary Action To Delete",
        },
        headers=analyst_headers,
    )
    act2_id = act2_res.json()["id"]
    del_act = client.delete(f"/api/v1/execution/actions/{act2_id}", headers=analyst_headers)
    assert del_act.status_code == 204


def test_api_initiative_and_program_governance(client, analyst_headers):
    """Tests GET /initiatives/{id}/governance and /programs/{id}/governance intelligence endpoints."""
    # 1. Create Program
    prog_res = client.post(
        "/api/v1/execution/programs",
        json={
            "title": "Digital Core Modernization Program",
            "description": "Core platform modernization program.",
        },
        headers=analyst_headers,
    )
    assert prog_res.status_code == 201
    prog_id = prog_res.json()["id"]

    # 2. Create Initiative under Program
    init_res = client.post(
        "/api/v1/execution/initiatives",
        json={
            "title": "Cloud Data Pipeline",
            "description": "Streaming data pipeline in cloud.",
            "objective": "Real-time governance analytics.",
            "program_id": prog_id,
        },
        headers=analyst_headers,
    )
    assert init_res.status_code == 201
    init_id = init_res.json()["id"]

    # 3. Schedule and complete a review with decision APPROVED
    rev_res = client.post(
        "/api/v1/execution/reviews",
        json={
            "initiative_id": init_id,
            "program_id": prog_id,
            "title": "Pipeline Go-Live Governance Review",
            "scheduled_at": datetime.now(timezone.utc).isoformat(),
        },
        headers=analyst_headers,
    )
    rev_id = rev_res.json()["id"]

    client.patch(
        f"/api/v1/execution/reviews/{rev_id}",
        json={"review_status": GovernanceReviewStatus.IN_PROGRESS.value},
        headers=analyst_headers,
    )
    client.patch(
        f"/api/v1/execution/reviews/{rev_id}",
        json={
            "review_status": GovernanceReviewStatus.COMPLETED.value,
            "decision": GovernanceDecision.APPROVED.value,
        },
        headers=analyst_headers,
    )

    # 4. Fetch Initiative Governance Detail
    init_gov_res = client.get(
        f"/api/v1/execution/initiatives/{init_id}/governance",
        headers=analyst_headers,
    )
    assert init_gov_res.status_code == 200
    init_gov = init_gov_res.json()
    assert init_gov["initiative_id"] == init_id
    assert "governance_metrics" in init_gov
    assert init_gov["governance_metrics"]["review_readiness_score"] >= 0.0
    assert init_gov["governance_metrics"]["review_readiness_level"] in ("READY", "REVIEW_REQUIRED", "ESCALATION_REQUIRED", "EXECUTIVE_ATTENTION")
    assert len(init_gov["reviews"]) == 1

    # 5. Fetch Program Governance Detail
    prog_gov_res = client.get(
        f"/api/v1/execution/programs/{prog_id}/governance",
        headers=analyst_headers,
    )
    assert prog_gov_res.status_code == 200
    prog_gov = prog_gov_res.json()
    assert prog_gov["program_id"] == prog_id
    assert prog_gov["initiatives_count"] >= 1
    assert "governance_metrics" in prog_gov


def test_api_portfolio_governance_summary(client, analyst_headers):
    """Tests GET /api/v1/execution/governance/summary endpoint."""
    res = client.get(
        "/api/v1/execution/governance/summary",
        headers=analyst_headers,
    )
    assert res.status_code == 200
    summary = res.json()
    assert "governance_maturity_level" in summary
    assert "governance_compliance_score" in summary
    assert "review_effectiveness_score" in summary
    assert "decision_positive_rate" in summary
    assert "decision_neutral_rate" in summary
    assert "decision_negative_rate" in summary
    assert "total_reviews" in summary
    assert "total_actions" in summary


def test_api_governance_tenant_isolation(client, analyst_headers, admin_headers):
    """Tests multi-tenant isolation ensuring Tenant B cannot access Tenant A review."""
    # Create review in Tenant A
    rev_res = client.post(
        "/api/v1/execution/reviews",
        json={
            "title": "Tenant A Confidential Review",
            "scheduled_at": datetime.now(timezone.utc).isoformat(),
        },
        headers=analyst_headers,
    )
    assert rev_res.status_code == 201
    rev_id = rev_res.json()["id"]

    # Try accessing with foreign tenant organization ID
    foreign_org_id = uuid.uuid4()
    for_res = client.get(
        f"/api/v1/execution/reviews/{rev_id}?organization_id={foreign_org_id}",
        headers=admin_headers,
    )
    assert for_res.status_code == 404


def test_api_governance_unauthorized_401(client):
    """Tests 401 Unauthorized rejection when unauthenticated."""
    res = client.get("/api/v1/execution/reviews")
    assert res.status_code == 401

    res_sum = client.get("/api/v1/execution/governance/summary")
    assert res_sum.status_code == 401
