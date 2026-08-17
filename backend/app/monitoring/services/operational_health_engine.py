"""Deterministic Operational Health Scoring Engine for Phase 13: Production Governance & Alert Monitoring."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.monitoring.constants import (
    OPERATIONAL_HEALTH_ENGINE_VERSION,
    MonitoringSeverity,
    MonitoringStatus,
    OperationalHealthGrade,
    calculate_operational_health,
)
from app.monitoring.schemas.production_monitoring import OperationalHealthMetricsResponse


class OperationalHealthEngine:
    """Computes exact 5-factor normalized composite operational health index and risk posture."""

    @classmethod
    def evaluate_health(
        cls,
        organization_id: uuid.UUID,
        alerts: List[Any],
        governance_score: float = 80.0,
        average_risk_score: float = 20.0,
        metric_coverage: float = 90.0,
        snapshot_completeness: float = 90.0,
        portfolio_balance_score: float = 80.0,
    ) -> OperationalHealthMetricsResponse:
        """Calculates deterministic composite operational health score (0-100) and factor contributions."""
        active_alerts = [a for a in alerts if getattr(a, "status", None) == MonitoringStatus.ACTIVE]

        crit_count = sum(1 for a in active_alerts if getattr(a, "severity", None) == MonitoringSeverity.CRITICAL)
        high_count = sum(1 for a in active_alerts if getattr(a, "severity", None) == MonitoringSeverity.HIGH)
        med_count = sum(1 for a in active_alerts if getattr(a, "severity", None) == MonitoringSeverity.MEDIUM)
        low_count = sum(1 for a in active_alerts if getattr(a, "severity", None) in (MonitoringSeverity.LOW, MonitoringSeverity.INFO))

        composite, grade, factors = calculate_operational_health(
            active_critical_count=crit_count,
            active_high_count=high_count,
            active_medium_count=med_count,
            active_low_count=low_count,
            governance_score=governance_score,
            average_risk_score=average_risk_score,
            metric_coverage=metric_coverage,
            snapshot_completeness=snapshot_completeness,
            portfolio_balance_score=portfolio_balance_score,
        )

        return OperationalHealthMetricsResponse(
            organization_id=organization_id,
            operational_health_score=composite,
            operational_health_grade=grade,
            alert_score=factors["alert_score"],
            alert_penalty=factors["alert_penalty"],
            governance_score=factors["governance_score"],
            risk_posture_score=factors["risk_posture_score"],
            data_quality_score=factors["data_quality_score"],
            portfolio_balance_score=factors["portfolio_balance_score"],
            contributing_factors=factors,
            engine_version=OPERATIONAL_HEALTH_ENGINE_VERSION,
            calculated_at=datetime.now(timezone.utc),
        )
