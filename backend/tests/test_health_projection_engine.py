"""Unit tests for HealthProjectionEngine and recommendation bonus isolation."""

import pytest
from app.core.constants import BusinessHealthStatus, FindingSeverity
from app.scenario_simulation.engines.health_projection_engine import HealthProjectionEngine


@pytest.fixture
def sample_findings():
    return [
        {
            "title": "Customer Churn Spike (25%)",
            "severity": "HIGH",
            "finding_type": "CUSTOMER_CHURN_SPIKE",
        },
        {
            "title": "Revenue Drop (-15%)",
            "severity": "HIGH",
            "finding_type": "REVENUE_DROP",
        },
    ]


@pytest.fixture
def sample_rcas():
    return [
        {
            "root_cause_title": "Onboarding Drop",
            "impact_score": 0.85,
        }
    ]


def test_health_projection_engine_finding_mitigation(sample_findings, sample_rcas):
    """Verifies that improving customer churn resolves the churn finding and improves health score."""
    base_metrics = {"customer_churn_rate": 25.0, "total_revenue": 100000.0}
    proj_metrics = {"customer_churn_rate": 8.0, "total_revenue": 100000.0}

    health_proj, proj_findings, risks, opps = HealthProjectionEngine.project_health_and_diagnostics(
        baseline_health_score=72,
        baseline_health_status=BusinessHealthStatus.WATCH_LIST,
        baseline_findings=sample_findings,
        baseline_root_causes=sample_rcas,
        baseline_metrics=base_metrics,
        projected_metrics=proj_metrics,
    )

    # Churn finding should be downgraded to LOW
    churn_f = next(f for f in proj_findings if "churn" in f["title"].lower())
    assert churn_f["projected_severity"] == "LOW"
    assert churn_f["severity_improved"] is True

    # Health score should increase
    assert health_proj.projected_score > health_proj.baseline_score
    assert health_proj.score_delta > 0
    assert len(opps) >= 1


def test_health_projection_engine_bonus_isolation(sample_findings, sample_rcas):
    """
    CRITICAL TEST: Verifies that pure metric scenario calculations DO NOT award an unearned
    recommendation implementation bonus (+2 per item).
    
    Formula strictly evaluates: 100 - finding_penalties - rca_penalties.
    """
    # Two HIGH findings (-10 each = -20) and one High RCA (-8) -> total deductions = 28
    # Score must be exactly 100 - 28 = 72, NOT 72 + bonus.
    base_metrics = {"customer_churn_rate": 25.0, "total_revenue": 100000.0}
    proj_metrics = {"customer_churn_rate": 25.0, "total_revenue": 100000.0}  # No change

    health_proj, proj_findings, risks, opps = HealthProjectionEngine.project_health_and_diagnostics(
        baseline_health_score=72,
        baseline_health_status=BusinessHealthStatus.WATCH_LIST,
        baseline_findings=sample_findings,
        baseline_root_causes=sample_rcas,
        baseline_metrics=base_metrics,
        projected_metrics=proj_metrics,
    )

    # 100 - 20 (findings) - 8 (RCA) = 72
    assert health_proj.projected_score == 72
    assert health_proj.score_delta == 0
