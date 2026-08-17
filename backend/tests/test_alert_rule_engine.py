"""Unit tests for Phase 13 AlertRuleEngine."""

import uuid
from datetime import date, datetime, timezone
from app.models.monitoring_alert import MonitoringAlert
from app.monitoring.constants import (
    AlertConfidenceLevel,
    MonitoringCategory,
    MonitoringSeverity,
    REASON_BENEFIT_REALIZATION_LAG,
    REASON_COMPLIANCE_FAILURE_DETECTED,
    REASON_CRITICAL_BLOCKER_PRESENT,
    REASON_HEALTH_SCORE_DEGRADATION,
    REASON_PORTFOLIO_IMBALANCE_DETECTED,
    REASON_REVENUE_DROP_THRESHOLD_EXCEEDED,
    REASON_RISK_POSTURE_ESCALATION,
    REASON_SNAPSHOT_RECENCY_BREACH,
    REASON_SPOF_CLUSTER_DETECTED,
)
from app.monitoring.services.alert_rule_engine import AlertRuleEngine


class DummyInitiative:
    def __init__(self, init_id, title, health=80.0, risk=20.0, has_crit=False):
        self.id = init_id
        self.title = title
        self.execution_health_score = health
        self.risk_score = risk
        self.has_critical_blockers = has_crit


class DummyGovReview:
    def __init__(self, comp_score=80.0):
        self.compliance_score = comp_score


class DummyBenefit:
    def __init__(self, expected=100000.0, realized=50000.0):
        self.expected_value = expected
        self.realized_value = realized


class DummySnapshot:
    def __init__(self, snap_id, days_ago=10, coverage=90.0, completeness=95.0):
        self.id = snap_id
        self.snapshot_date = date.fromordinal(datetime.now(timezone.utc).date().toordinal() - days_ago)
        self.snapshot_coverage_rate = coverage
        self.snapshot_completeness_score = completeness


def test_alert_rule_engine_kpi_and_risk_rules():
    """Tests KPI threshold drops and critical blocker risk rule triggering."""
    org_id = uuid.uuid4()
    init_id = uuid.uuid4()

    kpis = {
        "revenue_growth_rate": -18.5,
        "average_execution_health": 42.0,
    }
    initiatives = [
        DummyInitiative(init_id, "Edge Node Deployment", health=40.0, risk=85.0, has_crit=True),
        DummyInitiative(uuid.uuid4(), "Legacy ERP Upgrade", health=55.0, risk=78.0, has_crit=False),
    ]

    alerts = AlertRuleEngine.evaluate_rules(
        organization_id=org_id,
        kpi_metrics=kpis,
        initiatives=initiatives,
    )

    assert len(alerts) >= 4
    # Check Revenue Drop Alert
    rev_alert = next(a for a in alerts if a.rule_name == "RULE_KPI_REVENUE_DROP")
    assert rev_alert.category == MonitoringCategory.KPI
    assert rev_alert.severity == MonitoringSeverity.HIGH
    assert REASON_REVENUE_DROP_THRESHOLD_EXCEEDED in rev_alert.reason_codes

    # Check Health Degradation Alert
    health_alert = next(a for a in alerts if a.rule_name == "RULE_KPI_HEALTH_DEGRADATION")
    assert health_alert.severity == MonitoringSeverity.CRITICAL
    assert REASON_HEALTH_SCORE_DEGRADATION in health_alert.reason_codes

    # Check Critical Blocker Alert
    blocker_alert = next(a for a in alerts if a.rule_name == "RULE_RISK_CRITICAL_BLOCKER")
    assert blocker_alert.severity == MonitoringSeverity.CRITICAL
    assert blocker_alert.source_entity_id == str(init_id)
    assert REASON_CRITICAL_BLOCKER_PRESENT in blocker_alert.reason_codes

    # Check High Risk Exposure Alert
    risk_alert = next(a for a in alerts if a.rule_name == "RULE_RISK_HIGH_EXPOSURE")
    assert risk_alert.severity == MonitoringSeverity.HIGH
    assert REASON_RISK_POSTURE_ESCALATION in risk_alert.reason_codes


def test_alert_rule_engine_governance_benefits_portfolio_rules():
    """Tests governance compliance, benefits realization lag, and portfolio SPOF cluster alerts."""
    org_id = uuid.uuid4()

    gov_reviews = [
        DummyGovReview(comp_score=60.0),
        DummyGovReview(comp_score=50.0),
        DummyGovReview(comp_score=40.0),
    ]
    benefits = [
        DummyBenefit(expected=500000.0, realized=100000.0), # 20% realization
    ]
    portfolio_balance = {
        "portfolio_balance_score": 40.0,
        "single_points_of_failure_count": 3,
        "portfolio_strategic_exposure_score": 75.0,
    }
    latest_snap = DummySnapshot(uuid.uuid4(), days_ago=75, coverage=70.0, completeness=80.0)

    alerts = AlertRuleEngine.evaluate_rules(
        organization_id=org_id,
        governance_reviews=gov_reviews,
        benefits=benefits,
        portfolio_balance=portfolio_balance,
        latest_snapshot=latest_snap,
    )

    # Gov Alert
    gov_alert = next(a for a in alerts if a.rule_name == "RULE_GOV_NON_COMPLIANCE")
    assert gov_alert.severity == MonitoringSeverity.CRITICAL
    assert REASON_COMPLIANCE_FAILURE_DETECTED in gov_alert.reason_codes

    # Benefits Alert
    ben_alert = next(a for a in alerts if a.rule_name == "RULE_BENEFITS_LAG")
    assert ben_alert.severity == MonitoringSeverity.HIGH
    assert REASON_BENEFIT_REALIZATION_LAG in ben_alert.reason_codes

    # Portfolio Imbalance & SPOF Alert
    bal_alert = next(a for a in alerts if a.rule_name == "RULE_PORTFOLIO_IMBALANCE")
    assert REASON_PORTFOLIO_IMBALANCE_DETECTED in bal_alert.reason_codes

    spof_alert = next(a for a in alerts if a.rule_name == "RULE_PORTFOLIO_SPOF_CLUSTER")
    assert spof_alert.severity == MonitoringSeverity.HIGH
    assert REASON_SPOF_CLUSTER_DETECTED in spof_alert.reason_codes

    # Snapshot Recency Alert
    snap_alert = next(a for a in alerts if a.rule_name == "RULE_SNAPSHOT_RECENCY_BREACH")
    assert snap_alert.severity == MonitoringSeverity.MEDIUM
    assert REASON_SNAPSHOT_RECENCY_BREACH in snap_alert.reason_codes

    # Confidence check
    assert gov_alert.alert_confidence_score > 0.0
    assert gov_alert.alert_confidence_level in (AlertConfidenceLevel.HIGH, AlertConfidenceLevel.MEDIUM, AlertConfidenceLevel.LOW)
