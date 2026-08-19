"""KPI Drift Detection Engine for Phase 5.4."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from app.monitoring.schemas.continuous_monitoring_schemas import (
    KPIDriftEventResponse,
    KPIDriftListResponse,
)


class KPIDriftEngine:
    """Evaluates live telemetry against baseline targets and categorizes drift severity deterministically."""

    @staticmethod
    def detect_drift(
        portfolio_id: uuid.UUID,
        live_telemetry: Optional[Dict[str, float]] = None,
    ) -> KPIDriftListResponse:
        """
        Calculates drift percentages and assigns severity (LOW, MEDIUM, HIGH, CRITICAL).
        """
        targets = {
            "Customer Retention Rate": 85.8,
            "Delivery Latency (Days)": 3.2,
            "Courier SLA Compliance": 92.0,
            "Average Order Value (AOV)": 242.50,
            "Order Cancellation Rate": 1.4,
        }

        actuals = live_telemetry or {
            "Customer Retention Rate": 79.5,  # -7.3% (HIGH)
            "Delivery Latency (Days)": 5.4,   # +68.8% (CRITICAL)
            "Courier SLA Compliance": 78.4,  # -14.8% (CRITICAL)
            "Average Order Value (AOV)": 238.00, # -1.9% (LOW)
            "Order Cancellation Rate": 2.8,  # +100% (CRITICAL)
        }

        events: List[KPIDriftEventResponse] = []

        for metric, target in targets.items():
            actual = actuals.get(metric, target)
            is_higher_better = "Cancellation" not in metric and "Latency" not in metric

            if is_higher_better:
                drift_pct = round(((actual - target) / target) * 100, 1)
            else:
                drift_pct = round(((target - actual) / target) * 100, 1)

            # Determine severity
            abs_drift = abs(drift_pct)
            if drift_pct >= 0:
                severity = "LOW"
            elif abs_drift < 2.0:
                severity = "LOW"
            elif abs_drift < 5.0:
                severity = "MEDIUM"
            elif abs_drift < 10.0:
                severity = "HIGH"
            else:
                severity = "CRITICAL"

            explanation = (
                f"{metric} is currently {actual} vs. expected target of {target} "
                f"({drift_pct:+.1f}% drift, classified as {severity} severity)."
            )

            events.append(
                KPIDriftEventResponse(
                    id=uuid.uuid4(),
                    portfolio_id=portfolio_id,
                    metric_name=metric,
                    expected_value=target,
                    actual_value=actual,
                    drift_percentage=drift_pct,
                    severity=severity,
                    detected_at=datetime.now(timezone.utc),
                    resolved_at=None,
                    is_resolved=False,
                    explanation=explanation,
                )
            )

        critical_count = len([e for e in events if e.severity == "CRITICAL"])

        return KPIDriftListResponse(
            portfolio_id=portfolio_id,
            total_drift_events=len(events),
            critical_count=critical_count,
            events=events,
        )
