"""Executive Attention Queue Engine for Phase 12.7."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.execution.constants import (
    EXECUTIVE_ATTENTION_ENGINE_VERSION,
    STRATEGIC_SNAPSHOT_METRIC_VERSION,
    ExecutiveAttentionLevel,
    StrategicTrend,
    calculate_executive_attention_level,
    calculate_strategic_trend,
)


class ExecutiveAttentionEngine:
    """
    Deterministic calculation engine for prioritized executive attention queues.
    Provides complete 5-factor explainability breakdowns, attention trends, and aging metrics.
    """

    ENGINE_VERSION = EXECUTIVE_ATTENTION_ENGINE_VERSION
    SNAPSHOT_METRIC_VERSION = STRATEGIC_SNAPSHOT_METRIC_VERSION

    @classmethod
    def calculate_attention_item(
        cls,
        initiative_id: uuid.UUID,
        initiative_title: str,
        risk_score: float = 0.0,
        timeline_exposure: float = 0.0,
        outcome_gap: float = 0.0,
        governance_deficit: float = 0.0,
        health_score: float = 100.0,
        previous_attention_score: Optional[float] = None,
        first_triggered_at: Optional[datetime] = None,
        program_id: Optional[uuid.UUID] = None,
        program_title: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Calculates explainable attention score and drivers for a single initiative.
        """
        now = datetime.now(timezone.utc)

        # Health deficit = 100 - health_score
        health_deficit = max(0.0, 100.0 - health_score)

        # 5 Explainable Contributions (Sum directly to attention_score)
        risk_contrib = round(0.30 * max(0.0, min(100.0, risk_score)), 2)
        timeline_contrib = round(0.25 * max(0.0, min(100.0, timeline_exposure)), 2)
        outcome_contrib = round(0.20 * max(0.0, min(100.0, outcome_gap)), 2)
        gov_contrib = round(0.15 * max(0.0, min(100.0, governance_deficit)), 2)
        health_contrib = round(0.10 * max(0.0, min(100.0, health_deficit)), 2)

        attention_score = round(
            risk_contrib + timeline_contrib + outcome_contrib + gov_contrib + health_contrib,
            2,
        )
        attention_level = calculate_executive_attention_level(attention_score)

        # Trend and Delta
        if previous_attention_score is not None:
            if abs(previous_attention_score) > 1e-6:
                delta_pct = round(((attention_score - previous_attention_score) / abs(previous_attention_score)) * 100.0, 2)
            else:
                delta_pct = 100.0 if attention_score > 0 else 0.0
            # For attention score, higher is worse (more attention needed = deteriorating)
            trend = calculate_strategic_trend(delta_pct, higher_is_better=False)
        else:
            delta_pct = 0.0
            trend = StrategicTrend.STABLE

        # Aging in Days
        if first_triggered_at:
            t_trig = first_triggered_at if first_triggered_at.tzinfo is not None else first_triggered_at.replace(tzinfo=timezone.utc)
            delta_days = max(0, (now - t_trig).days)
        else:
            delta_days = 0

        # Deterministic Drivers
        drivers: List[str] = []
        if risk_contrib >= 15.0:
            drivers.append(f"Elevated delivery risk factor (+{risk_contrib:.1f} pts)")
        if timeline_contrib >= 12.0:
            drivers.append(f"Critical path delay exposure (+{timeline_contrib:.1f} pts)")
        if outcome_contrib >= 10.0:
            drivers.append(f"Strategic outcome realization gap (+{outcome_contrib:.1f} pts)")
        if gov_contrib >= 8.0:
            drivers.append(f"Overdue governance checkpoint (+{gov_contrib:.1f} pts)")
        if health_contrib >= 5.0:
            drivers.append(f"Execution health deterioration (+{health_contrib:.1f} pts)")

        if not drivers:
            drivers.append("Steady state operational execution")

        # Deterministic Recommended Action
        if attention_level == ExecutiveAttentionLevel.CRITICAL:
            recommended_action = "Immediate executive steering committee intervention and scope re-authorization required."
        elif attention_level == ExecutiveAttentionLevel.HIGH:
            recommended_action = "Assign senior PMO sponsor to remove operational blockers within 7 days."
        elif attention_level == ExecutiveAttentionLevel.MEDIUM:
            recommended_action = "Review risk mitigation plan at the upcoming bi-weekly program review."
        else:
            recommended_action = "Maintain standard tracking and checkpoint cadence."

        return {
            "initiative_id": initiative_id,
            "initiative_title": initiative_title,
            "program_id": program_id,
            "program_title": program_title,
            "attention_score": attention_score,
            "risk_contribution": risk_contrib,
            "timeline_contribution": timeline_contrib,
            "outcome_contribution": outcome_contrib,
            "governance_contribution": gov_contrib,
            "health_contribution": health_contrib,
            "attention_level": attention_level,
            "attention_trend": trend,
            "attention_delta_percentage": delta_pct,
            "attention_age_days": delta_days,
            "primary_drivers": drivers,
            "recommended_action": recommended_action,
            "calculated_at": now,
        }

    @classmethod
    def generate_attention_queue(
        cls,
        items: List[Dict[str, Any]],
        min_level: Optional[ExecutiveAttentionLevel] = None,
    ) -> Dict[str, Any]:
        """
        Generates and sorts executive attention queue descending by attention score.
        """
        now = datetime.now(timezone.utc)
        warnings: List[str] = []

        if not items:
            warnings.append("No active items found requiring executive attention.")
            return {
                "total_items_count": 0,
                "critical_items_count": 0,
                "high_items_count": 0,
                "queue": [],
                "data_quality_warnings": warnings,
                "calculated_at": now,
            }

        # Deterministic multi-level sorting: (-attention_score, -risk_contribution, -timeline_contribution, id)
        sorted_queue = sorted(
            items,
            key=lambda x: (
                -float(x.get("attention_score", 0.0)),
                -float(x.get("risk_contribution", 0.0)),
                -float(x.get("timeline_contribution", 0.0)),
                str(x.get("initiative_id", "")),
            ),
        )

        if min_level:
            level_rank = {
                ExecutiveAttentionLevel.LOW: 1,
                ExecutiveAttentionLevel.MEDIUM: 2,
                ExecutiveAttentionLevel.HIGH: 3,
                ExecutiveAttentionLevel.CRITICAL: 4,
            }
            min_rank = level_rank.get(min_level, 1)
            sorted_queue = [
                i for i in sorted_queue if level_rank.get(i.get("attention_level"), 1) >= min_rank
            ]

        critical_count = sum(1 for i in sorted_queue if i.get("attention_level") == ExecutiveAttentionLevel.CRITICAL)
        high_count = sum(1 for i in sorted_queue if i.get("attention_level") == ExecutiveAttentionLevel.HIGH)

        return {
            "total_items_count": len(sorted_queue),
            "critical_items_count": critical_count,
            "high_items_count": high_count,
            "queue": sorted_queue,
            "data_quality_warnings": warnings,
            "calculated_at": now,
        }
