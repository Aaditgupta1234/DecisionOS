"""Portfolio Ranking Engine for Phase 12.7."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.execution.constants import (
    RANKING_ENGINE_VERSION,
    STRATEGIC_SNAPSHOT_METRIC_VERSION,
    calculate_ranking_percentile,
)


class PortfolioRankingEngine:
    """
    Deterministic multi-dimensional ranking engine for strategic initiatives.
    Enforces strict multi-key tie-breaking rules and percentile positioning.
    """

    ENGINE_VERSION = RANKING_ENGINE_VERSION
    SNAPSHOT_METRIC_VERSION = STRATEGIC_SNAPSHOT_METRIC_VERSION

    @classmethod
    def rank_portfolio(
        cls,
        initiatives: List[Dict[str, Any]],
        limit: int = 10,
    ) -> Dict[str, Any]:
        """
        Produces 6 deterministic portfolio rankings.
        """
        now = datetime.now(timezone.utc)
        warnings: List[str] = []

        if not initiatives:
            warnings.append("No initiatives available to generate portfolio rankings.")
            return {
                "top_strategic_value_initiatives": [],
                "top_roi_initiatives": [],
                "highest_risk_initiatives": [],
                "highest_strategic_impact_initiatives": [],
                "lowest_value_efficiency_initiatives": [],
                "highest_governance_maturity_initiatives": [],
                "data_quality_warnings": warnings,
                "calculated_at": now,
            }

        total_items = len(initiatives)

        # Helper to format ranked item
        def _format_item(rank: int, item: Dict[str, Any], metric_val: float, sec_metric_val: Optional[float] = None) -> Dict[str, Any]:
            init_id = item.get("id", item.get("initiative_id", uuid.uuid4()))
            return {
                "rank": rank,
                "ranking_percentile": calculate_ranking_percentile(rank, total_items),
                "initiative_id": init_id,
                "initiative_title": item.get("title", item.get("name", "Untitled Initiative")),
                "program_id": item.get("program_id"),
                "program_title": item.get("program_title"),
                "metric_value": round(metric_val, 2),
                "secondary_metric_value": round(sec_metric_val, 2) if sec_metric_val is not None else None,
                "status": str(item.get("status", "ACTIVE")),
                "health_grade": str(item.get("health_grade", item.get("strategic_health_grade", "STABLE"))),
            }

        # 1. Top Strategic Value
        sorted_val = sorted(
            initiatives,
            key=lambda x: (
                -float(x.get("strategic_value_score", 0.0)),
                -float(x.get("outcome_achievement", x.get("outcome_score", 0.0))),
                -float(x.get("roi_score", 0.0)),
                str(x.get("created_at", "")),
                str(x.get("id", x.get("initiative_id", ""))),
            ),
        )
        top_value = [
            _format_item(
                idx + 1,
                item,
                float(item.get("strategic_value_score", 0.0)),
                float(item.get("outcome_achievement", item.get("outcome_score", 0.0))),
            )
            for idx, item in enumerate(sorted_val[:limit])
        ]

        # 2. Top ROI Initiatives
        sorted_roi = sorted(
            initiatives,
            key=lambda x: (
                -float(x.get("roi_score", 0.0)),
                -float(x.get("strategic_value_score", 0.0)),
                -float(x.get("outcome_achievement", 0.0)),
                str(x.get("id", x.get("initiative_id", ""))),
            ),
        )
        top_roi = [
            _format_item(
                idx + 1,
                item,
                float(item.get("roi_score", 0.0)),
                float(item.get("strategic_value_score", 0.0)),
            )
            for idx, item in enumerate(sorted_roi[:limit])
        ]

        # 3. Highest Risk Initiatives
        sorted_risk = sorted(
            initiatives,
            key=lambda x: (
                -float(x.get("risk_score", x.get("execution_risk", 0.0))),
                -float(x.get("timeline_risk_score", 0.0)),
                -float(x.get("cost_variance_pct", 0.0)),
                str(x.get("id", x.get("initiative_id", ""))),
            ),
        )
        highest_risk = [
            _format_item(
                idx + 1,
                item,
                float(item.get("risk_score", item.get("execution_risk", 0.0))),
                float(item.get("timeline_risk_score", 0.0)),
            )
            for idx, item in enumerate(sorted_risk[:limit])
        ]

        # 4. Highest Strategic Impact
        # Impact = 0.50 * value_score + 0.30 * budget_allocated + 0.20 * outcomes_count
        def _get_impact(x: Dict[str, Any]) -> float:
            v = float(x.get("strategic_value_score", 50.0))
            out_cnt = float(x.get("target_metrics_count", x.get("outcomes_count", 1)))
            return round(v * (1.0 + min(1.0, out_cnt / 10.0)), 2)

        sorted_impact = sorted(
            initiatives,
            key=lambda x: (
                -_get_impact(x),
                -float(x.get("strategic_value_score", 0.0)),
                str(x.get("id", x.get("initiative_id", ""))),
            ),
        )
        highest_impact = [
            _format_item(
                idx + 1,
                item,
                _get_impact(item),
                float(item.get("strategic_value_score", 0.0)),
            )
            for idx, item in enumerate(sorted_impact[:limit])
        ]

        # 5. Lowest Value Efficiency Initiatives
        sorted_efficiency = sorted(
            initiatives,
            key=lambda x: (
                float(x.get("value_efficiency_score", 100.0)),
                -float(x.get("risk_score", 0.0)),
                str(x.get("id", x.get("initiative_id", ""))),
            ),
        )
        lowest_efficiency = [
            _format_item(
                idx + 1,
                item,
                float(item.get("value_efficiency_score", 100.0)),
                float(item.get("risk_score", 0.0)),
            )
            for idx, item in enumerate(sorted_efficiency[:limit])
        ]

        # 6. Highest Governance Maturity
        sorted_gov = sorted(
            initiatives,
            key=lambda x: (
                -float(x.get("governance_maturity_score", x.get("governance_score", 0.0))),
                -float(x.get("governance_compliance_score", 0.0)),
                str(x.get("id", x.get("initiative_id", ""))),
            ),
        )
        highest_gov = [
            _format_item(
                idx + 1,
                item,
                float(item.get("governance_maturity_score", item.get("governance_score", 0.0))),
                float(item.get("governance_compliance_score", 0.0)),
            )
            for idx, item in enumerate(sorted_gov[:limit])
        ]

        return {
            "top_strategic_value_initiatives": top_value,
            "top_roi_initiatives": top_roi,
            "highest_risk_initiatives": highest_risk,
            "highest_strategic_impact_initiatives": highest_impact,
            "lowest_value_efficiency_initiatives": lowest_efficiency,
            "highest_governance_maturity_initiatives": highest_gov,
            "data_quality_warnings": warnings,
            "calculated_at": now,
        }
