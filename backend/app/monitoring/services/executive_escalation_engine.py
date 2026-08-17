"""Executive Escalation Prioritization Engine for Phase 13: Production Governance & Alert Monitoring."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.monitoring.constants import (
    EXECUTIVE_ESCALATION_ENGINE_VERSION,
    EscalationLevel,
    MonitoringSeverity,
    MonitoringStatus,
    calculate_escalation_tier,
)
from app.monitoring.schemas.production_monitoring import (
    ExecutiveEscalationItem,
    ExecutiveEscalationQueueResponse,
)


class ExecutiveEscalationEngine:
    """Classifies operational anomalies and initiatives into prioritized executive escalation tiers."""

    SEVERITY_WEIGHTS = {
        MonitoringSeverity.CRITICAL: 4,
        MonitoringSeverity.HIGH: 3,
        MonitoringSeverity.MEDIUM: 2,
        MonitoringSeverity.LOW: 1,
        MonitoringSeverity.INFO: 0,
    }

    LEVEL_WEIGHTS = {
        EscalationLevel.EXECUTIVE_ESCALATION: 4,
        EscalationLevel.EXECUTIVE_REVIEW: 3,
        EscalationLevel.ACTION_REQUIRED: 2,
        EscalationLevel.WATCH: 1,
    }

    @classmethod
    def generate_escalation_queue(
        cls,
        organization_id: uuid.UUID,
        alerts: List[Any],
        initiatives: Optional[List[Any]] = None,
    ) -> ExecutiveEscalationQueueResponse:
        """Evaluates active alerts and generates a deterministic executive escalation queue."""
        now = datetime.now(timezone.utc)
        escalation_items: List[ExecutiveEscalationItem] = []

        # 1. Process Active Operational Alerts
        active_alerts = [a for a in alerts if getattr(a, "status", None) == MonitoringStatus.ACTIVE]
        for a in active_alerts:
            sev = getattr(a, "severity", MonitoringSeverity.MEDIUM)
            reason_codes = getattr(a, "reason_codes", []) or []
            entity_id = getattr(a, "source_entity_id", None)
            entity_uuid = uuid.UUID(str(entity_id)) if entity_id else None
            
            # Determine business impact
            if sev == MonitoringSeverity.CRITICAL:
                bus_impact = "TRANSFORMATIONAL"
                gov_impact = "CRITICAL"
                port_impact = "SEVERE"
            elif sev == MonitoringSeverity.HIGH:
                bus_impact = "HIGH"
                gov_impact = "MODERATE"
                port_impact = "ELEVATED"
            elif sev == MonitoringSeverity.MEDIUM:
                bus_impact = "MEDIUM"
                gov_impact = "LOW"
                port_impact = "MODERATE"
            else:
                bus_impact = "LOW"
                gov_impact = "MINIMAL"
                port_impact = "LOW"

            esc_level = calculate_escalation_tier(
                severity=sev,
                business_impact=bus_impact,
                has_critical_blockers=("CRITICAL_BLOCKER_PRESENT" in reason_codes),
                is_governance_non_compliant=("COMPLIANCE_FAILURE_DETECTED" in reason_codes),
            )

            triggered_at = getattr(a, "first_triggered_at", now) or now
            age_days = max(0, (now.date() - triggered_at.date()).days)
            occurrence_count = int(getattr(a, "occurrence_count", 1) or 1)

            esc_id = uuid.UUID(str(getattr(a, "id", uuid.uuid4())))
            escalation_items.append(
                ExecutiveEscalationItem(
                    escalation_id=esc_id,
                    entity_id=entity_uuid,
                    entity_name=getattr(a, "title", "Operational Anomaly"),
                    escalation_level=esc_level,
                    severity=sev,
                    title=getattr(a, "title", "Operational Alert"),
                    business_impact=bus_impact,
                    governance_impact=gov_impact,
                    portfolio_impact=port_impact,
                    reason_codes=reason_codes,
                    occurrence_count=occurrence_count,
                    age_days=age_days,
                    triggered_at=triggered_at,
                )
            )

        # 2. Process Initiative Execution Risks if provided
        if initiatives:
            for init in initiatives:
                has_crit = getattr(init, "has_critical_blockers", False)
                risk_val = float(getattr(init, "risk_score", 20.0) or 20.0)
                if has_crit or risk_val >= 70.0:
                    init_id = getattr(init, "id", uuid.uuid4())
                    init_uuid = uuid.UUID(str(init_id))
                    # Prevent duplicate if alert already created for this entity
                    if any(item.entity_id == init_uuid for item in escalation_items):
                        continue

                    init_sev = MonitoringSeverity.CRITICAL if has_crit else MonitoringSeverity.HIGH
                    init_level = EscalationLevel.EXECUTIVE_ESCALATION if has_crit else EscalationLevel.EXECUTIVE_REVIEW
                    reasons = ["CRITICAL_BLOCKER_PRESENT"] if has_crit else ["HIGH_RISK_POSTURE"]
                    created_at = getattr(init, "created_at", now) or now
                    age_days = max(0, (now.date() - created_at.date()).days)

                    escalation_items.append(
                        ExecutiveEscalationItem(
                            escalation_id=uuid.uuid4(),
                            entity_id=init_uuid,
                            entity_name=getattr(init, "title", "Strategic Initiative"),
                            escalation_level=init_level,
                            severity=init_sev,
                            title=f"Strategic Execution Risk: {getattr(init, 'title', 'Initiative')}",
                            business_impact="TRANSFORMATIONAL" if has_crit else "HIGH",
                            governance_impact="CRITICAL" if has_crit else "MODERATE",
                            portfolio_impact="SEVERE" if has_crit else "ELEVATED",
                            reason_codes=reasons,
                            occurrence_count=1,
                            age_days=age_days,
                            triggered_at=created_at,
                        )
                    )

        # 3. Deterministic Multi-Key Sorting:
        # (-level_weight, -severity_weight, -occurrence_count, -age_days, escalation_id)
        sorted_queue = sorted(
            escalation_items,
            key=lambda x: (
                -cls.LEVEL_WEIGHTS.get(x.escalation_level, 0),
                -cls.SEVERITY_WEIGHTS.get(x.severity, 0),
                -x.occurrence_count,
                -x.age_days,
                str(x.escalation_id),
            ),
        )

        exec_esc_count = sum(1 for x in sorted_queue if x.escalation_level == EscalationLevel.EXECUTIVE_ESCALATION)
        exec_rev_count = sum(1 for x in sorted_queue if x.escalation_level == EscalationLevel.EXECUTIVE_REVIEW)
        act_req_count = sum(1 for x in sorted_queue if x.escalation_level == EscalationLevel.ACTION_REQUIRED)
        watch_count = sum(1 for x in sorted_queue if x.escalation_level == EscalationLevel.WATCH)

        return ExecutiveEscalationQueueResponse(
            organization_id=organization_id,
            total_escalations=len(sorted_queue),
            executive_escalation_count=exec_esc_count,
            executive_review_count=exec_rev_count,
            action_required_count=act_req_count,
            watch_count=watch_count,
            escalation_queue=sorted_queue,
            engine_version=EXECUTIVE_ESCALATION_ENGINE_VERSION,
            calculated_at=datetime.now(timezone.utc),
        )
