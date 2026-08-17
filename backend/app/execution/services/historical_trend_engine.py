"""Historical Trend Engine for Phase 12.8."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from app.execution.constants import (
    HISTORICAL_TREND_ENGINE_VERSION,
    STRATEGIC_SNAPSHOT_METRIC_VERSION,
    TrendDirection,
    calculate_trend_direction,
)


class HistoricalTrendEngine:
    """
    Deterministic trend calculation engine evaluating longitudinal velocity across snapshots.
    Tracks Health, Risk, Governance, Outcome, ROI, and Strategic Maturity trajectories.
    """

    ENGINE_VERSION = HISTORICAL_TREND_ENGINE_VERSION
    SNAPSHOT_METRIC_VERSION = STRATEGIC_SNAPSHOT_METRIC_VERSION

    @classmethod
    def calculate_longitudinal_trends(
        cls,
        snapshots: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Calculates multi-dimensional trend vectors across a chronological sequence of snapshots.
        Snapshots are expected to be ordered chronologically (oldest to newest).
        """
        now = datetime.now(timezone.utc)
        warnings: List[str] = []

        if len(snapshots) < 2:
            warnings.append("Insufficient snapshot history for longitudinal trend evaluation (minimum 2 required).")
            return {
                "health_trend": TrendDirection.STABLE,
                "health_delta_percentage": 0.0,
                "risk_trend": TrendDirection.STABLE,
                "risk_delta_percentage": 0.0,
                "governance_trend": TrendDirection.STABLE,
                "governance_delta_percentage": 0.0,
                "outcome_trend": TrendDirection.STABLE,
                "outcome_delta_percentage": 0.0,
                "roi_trend": TrendDirection.STABLE,
                "roi_delta_percentage": 0.0,
                "maturity_trend": TrendDirection.STABLE,
                "maturity_delta_percentage": 0.0,
                "snapshots_evaluated": len(snapshots),
                "data_quality_warnings": warnings,
                "calculated_at": now,
            }

        oldest = snapshots[0]
        newest = snapshots[-1]

        def _calc_delta(old_val: float, new_val: float, higher_is_better: bool = True) -> Dict[str, Any]:
            if abs(old_val) > 1e-6:
                delta_pct = round(((new_val - old_val) / abs(old_val)) * 100.0, 2)
            else:
                delta_pct = 100.0 if new_val > 0 else (0.0 if new_val == 0 else -100.0)
            trend = calculate_trend_direction(delta_pct, higher_is_better=higher_is_better)
            return {"delta_pct": delta_pct, "trend": trend}

        # 1. Health Trend
        h_res = _calc_delta(
            float(oldest.get("portfolio_health_score", oldest.get("health_score", 100.0))),
            float(newest.get("portfolio_health_score", newest.get("health_score", 100.0))),
            higher_is_better=True,
        )

        # 2. Risk Trend (Lower is better)
        r_res = _calc_delta(
            float(oldest.get("portfolio_risk_score", oldest.get("risk_score", 0.0))),
            float(newest.get("portfolio_risk_score", newest.get("risk_score", 0.0))),
            higher_is_better=False,
        )

        # 3. Governance Trend
        g_res = _calc_delta(
            float(oldest.get("portfolio_governance_score", oldest.get("governance_score", 100.0))),
            float(newest.get("portfolio_governance_score", newest.get("governance_score", 100.0))),
            higher_is_better=True,
        )

        # 4. Outcome Trend
        o_res = _calc_delta(
            float(oldest.get("portfolio_outcome_attainment_rate", oldest.get("outcome_score", 0.0))),
            float(newest.get("portfolio_outcome_attainment_rate", newest.get("outcome_score", 0.0))),
            higher_is_better=True,
        )

        # 5. ROI Trend
        roi_res = _calc_delta(
            float(oldest.get("portfolio_roi_score", oldest.get("roi_score", 0.0))),
            float(newest.get("portfolio_roi_score", newest.get("roi_score", 0.0))),
            higher_is_better=True,
        )

        # 6. Strategic Maturity Trend
        m_res = _calc_delta(
            float(oldest.get("portfolio_strategic_maturity_score", oldest.get("maturity_score", 0.0))),
            float(newest.get("portfolio_strategic_maturity_score", newest.get("maturity_score", 0.0))),
            higher_is_better=True,
        )

        return {
            "health_trend": h_res["trend"],
            "health_delta_percentage": h_res["delta_pct"],
            "risk_trend": r_res["trend"],
            "risk_delta_percentage": r_res["delta_pct"],
            "governance_trend": g_res["trend"],
            "governance_delta_percentage": g_res["delta_pct"],
            "outcome_trend": o_res["trend"],
            "outcome_delta_percentage": o_res["delta_pct"],
            "roi_trend": roi_res["trend"],
            "roi_delta_percentage": roi_res["delta_pct"],
            "maturity_trend": m_res["trend"],
            "maturity_delta_percentage": m_res["delta_pct"],
            "snapshots_evaluated": len(snapshots),
            "data_quality_warnings": warnings,
            "calculated_at": now,
        }
