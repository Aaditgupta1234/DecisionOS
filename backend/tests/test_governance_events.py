"""Unit and integration tests for Governance Audit Events (Phase 12.5).

Verifies domain audit events dispatched on review lifecycles, action assignments,
escalation triggers, and resolutions.
"""

from datetime import datetime, timezone
import uuid
import pytest

from app.execution.constants import (
    ActionPriority,
    EscalationLevel,
    ExecutionEventType,
    GovernanceActionStatus,
    GovernanceDecision,
    GovernanceReviewStatus,
    ReviewType,
)
from app.execution.schemas.governance import (
    GovernanceReviewCreate,
    GovernanceReviewUpdate,
    ReviewActionCreate,
    ReviewActionUpdate,
)
from app.execution.services.governance_service import GovernanceService
from app.execution.services.initiative_service import InitiativeService
from app.execution.schemas.initiative import InitiativeCreate


def test_governance_review_and_action_events_dispatch(client, analyst_headers, db_session):
    """Tests audit event dispatching throughout the governance review and action lifecycle."""
    # 1. Create an initiative to attach reviews and actions to
    init_res = client.post(
        "/api/v1/execution/initiatives",
        json={
            "title": "ERP Cloud Stage-Gate Initiative",
            "description": "Enterprise ERP cloud transition.",
            "objective": "Complete stage-gate governance requirements.",
            "budget_allocated": 150000.0,
            "budget_spent": 50000.0,
        },
        headers=analyst_headers,
    )
    assert init_res.status_code == 201
    init_id = init_res.json()["id"]

    # 2. Schedule Review with ESCALATION -> emits REVIEW_SCHEDULED and ESCALATION_TRIGGERED
    sched_res = client.post(
        "/api/v1/execution/reviews",
        json={
            "initiative_id": init_id,
            "title": "Stage-Gate 1 Review",
            "review_type": ReviewType.GOVERNANCE_REVIEW.value,
            "scheduled_at": datetime.now(timezone.utc).isoformat(),
            "review_owner": "PMO Director",
            "escalation_level": EscalationLevel.LEVEL_1.value,
            "review_notes": "Review initial architecture readiness.",
        },
        headers=analyst_headers,
    )
    assert sched_res.status_code == 201
    review_id = sched_res.json()["id"]

    # Check initiative events
    events_res = client.get(
        f"/api/v1/execution/events/initiatives/{init_id}",
        headers=analyst_headers,
    )
    assert events_res.status_code == 200
    events = events_res.json()["events"]
    event_types = [e["event_type"] for e in events]
    assert ExecutionEventType.REVIEW_SCHEDULED.value in event_types
    assert ExecutionEventType.ESCALATION_TRIGGERED.value in event_types

    # 3. Transition review to IN_PROGRESS -> emits REVIEW_STARTED
    upd_res = client.patch(
        f"/api/v1/execution/reviews/{review_id}",
        json={
            "review_status": GovernanceReviewStatus.IN_PROGRESS.value,
        },
        headers=analyst_headers,
    )
    assert upd_res.status_code == 200

    events_res2 = client.get(
        f"/api/v1/execution/events/initiatives/{init_id}",
        headers=analyst_headers,
    )
    event_types2 = [e["event_type"] for e in events_res2.json()["events"]]
    assert ExecutionEventType.REVIEW_STARTED.value in event_types2

    # 4. Create an action item -> emits ACTION_CREATED and ACTION_ASSIGNED
    act_res = client.post(
        "/api/v1/execution/actions",
        json={
            "review_id": review_id,
            "title": "Security Architecture Sign-Off",
            "assigned_to": "Security Lead",
            "priority": ActionPriority.HIGH.value,
        },
        headers=analyst_headers,
    )
    assert act_res.status_code == 201
    action_id = act_res.json()["id"]

    events_res3 = client.get(
        f"/api/v1/execution/events/initiatives/{init_id}",
        headers=analyst_headers,
    )
    event_types3 = [e["event_type"] for e in events_res3.json()["events"]]
    assert ExecutionEventType.ACTION_CREATED.value in event_types3
    assert ExecutionEventType.ACTION_ASSIGNED.value in event_types3

    # 5. Complete the action item -> emits ACTION_COMPLETED
    act_comp_res = client.patch(
        f"/api/v1/execution/actions/{action_id}",
        json={
            "status": GovernanceActionStatus.IN_PROGRESS.value,
        },
        headers=analyst_headers,
    )
    assert act_comp_res.status_code == 200

    act_comp_res2 = client.patch(
        f"/api/v1/execution/actions/{action_id}",
        json={
            "status": GovernanceActionStatus.COMPLETED.value,
        },
        headers=analyst_headers,
    )
    assert act_comp_res2.status_code == 200

    events_res4 = client.get(
        f"/api/v1/execution/events/initiatives/{init_id}",
        headers=analyst_headers,
    )
    event_types4 = [e["event_type"] for e in events_res4.json()["events"]]
    assert ExecutionEventType.ACTION_COMPLETED.value in event_types4

    # 6. Complete Review and Resolve Escalation -> emits REVIEW_COMPLETED and ESCALATION_RESOLVED
    rev_comp_res = client.patch(
        f"/api/v1/execution/reviews/{review_id}",
        json={
            "review_status": GovernanceReviewStatus.COMPLETED.value,
            "decision": GovernanceDecision.APPROVED_WITH_CONDITIONS.value,
            "decision_rationale": "Security signoff received, pending final QA report.",
            "escalation_level": EscalationLevel.NONE.value,
        },
        headers=analyst_headers,
    )
    assert rev_comp_res.status_code == 200
    assert rev_comp_res.json()["decision_outcome"] == "NEUTRAL"

    events_res5 = client.get(
        f"/api/v1/execution/events/initiatives/{init_id}",
        headers=analyst_headers,
    )
    event_types5 = [e["event_type"] for e in events_res5.json()["events"]]
    assert ExecutionEventType.REVIEW_COMPLETED.value in event_types5
    assert ExecutionEventType.ESCALATION_RESOLVED.value in event_types5
