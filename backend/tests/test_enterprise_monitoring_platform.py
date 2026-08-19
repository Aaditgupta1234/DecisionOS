"""Unit tests for Phase 6.6 Enterprise Monitoring, Event Intelligence & Predictive Alerting Platform."""

import uuid
import pytest
from app.monitoring.services.autonomous_monitoring_engine import AutonomousMonitoringEngine
from app.monitoring.services.alert_deduplication_engine import AlertDeduplicationEngine
from app.monitoring.services.alert_explanation_engine import AlertExplanationEngine
from app.monitoring.services.alert_impact_forecast_engine import AlertImpactForecastEngine
from app.monitoring.services.alert_sla_governance_engine import AlertSLAGovernanceEngine
from app.monitoring.services.notification_delivery_engine import NotificationDeliveryEngine
from app.monitoring.services.alert_lineage_engine import AlertLineageEngine
from app.monitoring.services.alert_postmortem_engine import AlertPostmortemEngine
from app.monitoring.services.monitoring_coverage_engine import MonitoringCoverageEngine
from app.monitoring.services.monitoring_maturity_engine import MonitoringMaturityEngine


def test_continuous_monitoring_evaluation():
    """Test continuous monitoring health and stream telemetry."""
    portfolio_id = uuid.uuid4()
    health = AutonomousMonitoringEngine.get_monitoring_health(portfolio_id)

    assert health["monitored_streams"] == 7
    assert health["monitored_kpis_count"] == 32
    assert health["active_rules_count"] == 118
    assert health["monitoring_health_pct"] == 97.4
    assert health["overall_status"] == "OPTIMAL_OPERATIONAL"

    alerts = AutonomousMonitoringEngine.get_sample_alerts(portfolio_id)
    assert len(alerts) == 3
    assert alerts[0].alert_code == "ALT-2026-089"
    assert alerts[0].severity == "CRITICAL"
    assert alerts[0].owner_team == "Supply Chain & Logistics"


def test_alert_deduplication_and_merging():
    """Test duplicate detection and incident cluster merging."""
    res = AlertDeduplicationEngine.process_and_deduplicate([])
    assert res["total_raw_signals_evaluated"] == 18
    assert res["deduplicated_incidents_created"] == 3
    assert res["suppressed_duplicate_signals"] == 15
    assert res["noise_reduction_rate_pct"] > 80.0
    assert len(res["consolidated_incident_clusters"]) == 1


def test_alert_explanation_engine():
    """Test diagnostic explainability breakdown."""
    alert_id = uuid.uuid4()
    exp = AlertExplanationEngine.explain_alert(alert_id)

    assert exp.alert_code == "ALT-2026-089"
    assert exp.rule_name == "RETENTION_DRIFT_5PCT"
    assert exp.current_metric == 79.1
    assert exp.drift_pct == -6.0
    assert exp.threshold_pct == -5.0
    assert exp.confidence_score == 94.2


def test_alert_impact_forecasting():
    """Test projected business loss estimation."""
    alert_id = uuid.uuid4()
    impact = AlertImpactForecastEngine.estimate_impact(alert_id)

    assert impact.projected_arr_impact == -82000.0
    assert impact.projected_health_impact == -4.2
    assert impact.projected_risk_increase == 6.1
    assert impact.confidence_pct == 91.0


def test_alert_sla_and_escalation_policy():
    """Test SLA response targets and 4-tier timed escalation ladder."""
    alert_id = uuid.uuid4()
    sla = AlertSLAGovernanceEngine.get_alert_sla(alert_id)
    assert sla.response_time_minutes == 15
    assert sla.resolution_time_minutes == 240
    assert sla.sla_status == "WITHIN_SLA"

    policy = AlertSLAGovernanceEngine.get_escalation_policy(alert_id)
    assert policy.analyst_timeout_minutes == 0
    assert policy.manager_timeout_minutes == 15
    assert policy.executive_timeout_minutes == 30
    assert policy.board_timeout_minutes == 60


def test_notification_delivery_lifecycle():
    """Test notification delivery audit states."""
    alert_id = uuid.uuid4()
    deliveries = NotificationDeliveryEngine.get_deliveries_for_alert(alert_id)

    assert len(deliveries) == 2
    assert deliveries[0].recipient_role == "COO"
    assert deliveries[0].status == "VIEWED"
    assert deliveries[1].recipient_role == "VP Operations"
    assert deliveries[1].status == "DELIVERED"


def test_alert_lineage_and_explainability():
    """Test explainable alert provenance DAG."""
    alert_id = uuid.uuid4()
    lineage = AlertLineageEngine.get_lineage_for_alert(alert_id)

    assert lineage.alert_id == alert_id
    assert len(lineage.lineage_tree["nodes"]) == 5
    assert len(lineage.lineage_tree["edges"]) == 4


def test_alert_postmortem_generation():
    """Test blameless postmortem generation and institutional memory."""
    alert_id = uuid.uuid4()
    post = AlertPostmortemEngine.get_postmortem_for_alert(alert_id)

    assert "Southeastern carrier transit delay" in post.root_cause_summary
    assert len(post.lessons_learned) == 2
    assert len(post.preventive_actions) == 2


def test_monitoring_coverage_and_maturity():
    """Test governance coverage report and composite maturity score."""
    portfolio_id = uuid.uuid4()

    cov = MonitoringCoverageEngine.get_coverage_report(portfolio_id)
    assert cov.kpis_monitored == 32
    assert cov.total_kpis == 34
    assert cov.coverage_pct == 96.4
    assert len(cov.unmonitored_metrics) == 2

    mat = MonitoringMaturityEngine.get_maturity_report(portfolio_id)
    assert mat.maturity_score == 91.8
    assert mat.grade == "Grade A"
    assert mat.coverage_score == 96.4
    assert mat.sla_compliance_score == 95.0
