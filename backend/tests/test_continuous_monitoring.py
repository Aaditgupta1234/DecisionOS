"""Unit tests for Phase 5.4 Continuous Intelligence, Monitoring & Adaptive Recovery."""

import uuid
import pytest
from app.monitoring.schemas.continuous_monitoring_schemas import AdaptiveRecalculationRequest
from app.monitoring.services.kpi_drift_engine import KPIDriftEngine
from app.monitoring.services.forecast_validation_engine import ForecastValidationEngine
from app.monitoring.services.initiative_monitoring_engine import InitiativeMonitoringEngine
from app.monitoring.services.portfolio_health_trend_engine import PortfolioHealthTrendEngine
from app.monitoring.services.risk_escalation_engine import RiskEscalationEngine
from app.monitoring.services.adaptive_recovery_engine import AdaptiveRecoveryEngine
from app.monitoring.services.executive_alert_engine import ExecutiveAlertEngine


def test_kpi_drift_engine():
    """Test live telemetry drift detection and severity grading."""
    portfolio_id = uuid.uuid4()
    res = KPIDriftEngine.detect_drift(
        portfolio_id,
        live_telemetry={"Customer Retention Rate": 79.5, "Delivery Latency (Days)": 5.4},
    )

    assert res.portfolio_id == portfolio_id
    assert res.total_drift_events == 5
    retention_event = next(e for e in res.events if e.metric_name == "Customer Retention Rate")
    assert retention_event.actual_value == 79.5
    assert retention_event.drift_percentage == -7.3
    assert retention_event.severity == "HIGH"


def test_forecast_validation_engine_rolling_accuracy():
    """Test forecast variance evaluation and longitudinal rolling accuracy."""
    portfolio_id = uuid.uuid4()
    res = ForecastValidationEngine.validate_forecasts(portfolio_id)

    assert res.portfolio_id == portfolio_id
    assert len(res.forecast_deviations) == 3
    assert res.rolling_accuracy_score >= 85.0
    assert res.latest_accuracy_score > 90.0
    assert res.confidence_adjustment == 0.0


def test_initiative_monitoring_engine():
    """Test initiative execution performance status classification."""
    portfolio_id = uuid.uuid4()
    res = InitiativeMonitoringEngine.monitor_initiatives(portfolio_id)

    assert res.portfolio_id == portfolio_id
    assert res.total_tracked_initiatives == 5
    assert res.underperforming_count >= 1

    hub_init = next(i for i in res.initiatives if i.initiative_id == "INIT-2026-002")
    assert hub_init.status == "UNDERPERFORMING"
    assert hub_init.variance_arr == -110000.0


def test_portfolio_health_trend_engine_windows():
    """Test 7d, 30d, 90d longitudinal health velocity analytics."""
    portfolio_id = uuid.uuid4()
    res = PortfolioHealthTrendEngine.evaluate_health_trends(portfolio_id, current_health_score=74.0)

    assert res.portfolio_id == portfolio_id
    assert res.current_health_score == 74.0
    assert len(res.trend_windows) == 3

    win_7d = next(w for w in res.trend_windows if w.window_days == 7)
    assert win_7d.trend_status == "IMPROVING"
    assert win_7d.delta_health_score == +1.8

    win_90d = next(w for w in res.trend_windows if w.window_days == 90)
    assert win_90d.trend_status == "RECOVERY_ACCELERATING"
    assert win_90d.delta_health_score == +6.0


def test_risk_escalation_engine_velocity():
    """Test systemic risk index calculation and escalation velocity vector."""
    portfolio_id = uuid.uuid4()
    res = RiskEscalationEngine.evaluate_risks(portfolio_id)

    assert res.portfolio_id == portfolio_id
    assert res.systemic_risk_index == 24.3
    assert res.escalation_velocity == "STABLE"
    assert res.critical_risk_count == 1

    deadlock_risk = next(r for r in res.active_risks if r.risk_category == "OPERATIONAL_DEPENDENCY")
    assert deadlock_risk.severity == "CRITICAL"
    assert deadlock_risk.trend == "DETERIORATING"


def test_adaptive_recovery_engine_provenance():
    """Test adaptive recovery recalculation with trigger provenance lineage."""
    portfolio_id = uuid.uuid4()
    drift_event_id = uuid.uuid4()

    req = AdaptiveRecalculationRequest(
        portfolio_id=portfolio_id,
        trigger_event_id=drift_event_id,
        trigger_type="KPI_DRIFT",
        trigger_severity="HIGH",
        reason="Customer retention dropped to 79.5%",
    )

    res = AdaptiveRecoveryEngine.recalculate_recovery(req)

    assert res.portfolio_id == portfolio_id
    assert res.trigger_event_id == drift_event_id
    assert res.trigger_severity == "HIGH"
    assert res.expected_arr_delta == +75000.0
    assert len(res.recalculated_priorities) == 3
    assert len(res.updated_directives) == 3
    assert len(res.sha256_hash) == 64


def test_executive_alert_engine_lifecycle_and_snapshot():
    """Test 5-state alert queue and versioned monitoring snapshot."""
    portfolio_id = uuid.uuid4()
    alerts_res = ExecutiveAlertEngine.get_alerts(portfolio_id)

    assert alerts_res.portfolio_id == portfolio_id
    assert alerts_res.total_alerts == 3
    assert alerts_res.open_alerts >= 2
    assert alerts_res.critical_alerts == 1

    snap_res = ExecutiveAlertEngine.capture_monitoring_snapshot(portfolio_id, snapshot_version=1)
    assert snap_res.portfolio_id == portfolio_id
    assert snap_res.snapshot_version == 1
    assert snap_res.overall_health_score == 74.0
    assert snap_res.score_summary.overall_monitoring_score == 78.0
    assert snap_res.score_summary.risk_velocity == "STABLE"
    assert len(snap_res.sha256_hash) == 64
