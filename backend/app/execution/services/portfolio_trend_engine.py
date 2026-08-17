"""Portfolio Trend Engine for Phase 12.7."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.execution.constants import (
    PORTFOLIO_TREND_ENGINE_VERSION,
    STRATEGIC_SNAPSHOT_METRIC_VERSION,
    PortfolioTrajectoryGrade,
    StrategicTrend,
    calculate_portfolio_trajectory_grade,
    calculate_strategic_trend,
)


class PortfolioTrendEngine:
    """
    Deterministic calculation engine for portfolio trends across historical snapshots.
    Enforces minimum snapshot history requirements and deterministic trajectory grades.
    """

    ENGINE_VERSION = PORTFOLIO_TREND_ENGINE_VERSION
    SNAPSHOT_METRIC_VERSION = STRATEGIC_SNAPSHOT_METRIC_VERSION
    MINIMUM_SNAPSHOTS_REQUIRED = 2

    @classmethod
    def calculate_trends(
        cls,
        snapshots: Optional[List[Dict[str, Any]]] = None,
        current_health: float = 100.0,
        current_risk: float = 0.0,
        current_governance: float = 100.0,
        current_outcome: float = 100.0,
        current_roi: float = 0.0,
        previous_health: Optional[float] = None,
        previous_risk: Optional[float] = None,
        previous_governance: Optional[float] = None,
        previous_outcome: Optional[float] = None,
        previous_roi: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Calculates 5-dimensional portfolio trends and trajectory grade.
        Can consume explicit snapshot list or previous values.
        """
        now = datetime.now(timezone.utc)
        warnings: List[str] = []
        
        # If snapshots provided, extract current and previous
        snapshots_count = len(snapshots) if snapshots else (2 if previous_health is not None else 1)
        
        if snapshots and len(snapshots) >= 2:
            latest = snapshots[-1]
            prior = snapshots[-2]
            
            c_health = float(latest.get("health_score", latest.get("execution_health", current_health)))
            p_health = float(prior.get("health_score", prior.get("execution_health", c_health)))
            
            c_risk = float(latest.get("risk_score", latest.get("execution_risk", current_risk)))
            p_risk = float(prior.get("risk_score", prior.get("execution_risk", c_risk)))
            
            c_gov = float(latest.get("governance_score", latest.get("governance_maturity", current_governance)))
            p_gov = float(prior.get("governance_score", prior.get("governance_maturity", c_gov)))
            
            c_out = float(latest.get("outcome_achievement", latest.get("outcome_score", current_outcome)))
            p_out = float(prior.get("outcome_achievement", prior.get("outcome_score", c_out)))
            
            c_roi = float(latest.get("roi_score", latest.get("portfolio_roi", current_roi)))
            p_roi = float(prior.get("roi_score", prior.get("portfolio_roi", c_roi)))
            has_history = True
        elif previous_health is not None:
            c_health = current_health
            p_health = previous_health
            c_risk = current_risk
            p_risk = previous_risk if previous_risk is not None else current_risk
            c_gov = current_governance
            p_gov = previous_governance if previous_governance is not None else current_governance
            c_out = current_outcome
            p_out = previous_outcome if previous_outcome is not None else current_outcome
            c_roi = current_roi
            p_roi = previous_roi if previous_roi is not None else current_roi
            has_history = True
        else:
            c_health, p_health = current_health, None
            c_risk, p_risk = current_risk, None
            c_gov, p_gov = current_governance, None
            c_out, p_out = current_outcome, None
            c_roi, p_roi = current_roi, None
            has_history = False

        if not has_history or snapshots_count < cls.MINIMUM_SNAPSHOTS_REQUIRED:
            warnings.append("Insufficient historical snapshots (< 2 snapshots) for longitudinal trend analysis.")
            return {
                "health_trend": {
                    "metric_name": "Execution Health",
                    "current_value": round(c_health, 2),
                    "previous_value": None,
                    "trend_delta_percentage": 0.0,
                    "trend": StrategicTrend.STABLE,
                    "higher_is_better": True,
                },
                "risk_trend": {
                    "metric_name": "Execution Risk",
                    "current_value": round(c_risk, 2),
                    "previous_value": None,
                    "trend_delta_percentage": 0.0,
                    "trend": StrategicTrend.STABLE,
                    "higher_is_better": False,
                },
                "governance_trend": {
                    "metric_name": "Governance Maturity",
                    "current_value": round(c_gov, 2),
                    "previous_value": None,
                    "trend_delta_percentage": 0.0,
                    "trend": StrategicTrend.STABLE,
                    "higher_is_better": True,
                },
                "outcome_trend": {
                    "metric_name": "Outcome Achievement",
                    "current_value": round(c_out, 2),
                    "previous_value": None,
                    "trend_delta_percentage": 0.0,
                    "trend": StrategicTrend.STABLE,
                    "higher_is_better": True,
                },
                "roi_trend": {
                    "metric_name": "Portfolio ROI",
                    "current_value": round(c_roi, 2),
                    "previous_value": None,
                    "trend_delta_percentage": 0.0,
                    "trend": StrategicTrend.STABLE,
                    "higher_is_better": True,
                },
                "portfolio_trajectory_grade": PortfolioTrajectoryGrade.STABLE,
                "insufficient_history": True,
                "historical_snapshots_count": snapshots_count,
                "data_quality_warnings": warnings,
                "calculated_at": now,
            }

        # Helper for delta percentage
        def _compute_delta(curr: float, prev: float) -> float:
            if abs(prev) > 1e-6:
                return round(((curr - prev) / abs(prev)) * 100.0, 2)
            if curr > prev:
                return 100.0
            if curr < prev:
                return -100.0
            return 0.0

        health_delta = _compute_delta(c_health, p_health)
        risk_delta = _compute_delta(c_risk, p_risk)
        gov_delta = _compute_delta(c_gov, p_gov)
        out_delta = _compute_delta(c_out, p_out)
        roi_delta = _compute_delta(c_roi, p_roi)

        health_trend = calculate_strategic_trend(health_delta, higher_is_better=True)
        # For risk, higher delta means worse/deteriorating
        risk_trend = calculate_strategic_trend(risk_delta, higher_is_better=False)
        gov_trend = calculate_strategic_trend(gov_delta, higher_is_better=True)
        out_trend = calculate_strategic_trend(out_delta, higher_is_better=True)
        roi_trend = calculate_strategic_trend(roi_delta, higher_is_better=True)

        trajectory_grade = calculate_portfolio_trajectory_grade(
            health_delta=health_delta,
            outcome_delta=out_delta,
            roi_delta=roi_delta,
            risk_delta=risk_delta,
        )

        return {
            "health_trend": {
                "metric_name": "Execution Health",
                "current_value": round(c_health, 2),
                "previous_value": round(p_health, 2),
                "trend_delta_percentage": health_delta,
                "trend": health_trend,
                "higher_is_better": True,
            },
            "risk_trend": {
                "metric_name": "Execution Risk",
                "current_value": round(c_risk, 2),
                "previous_value": round(p_risk, 2),
                "trend_delta_percentage": risk_delta,
                "trend": risk_trend,
                "higher_is_better": False,
            },
            "governance_trend": {
                "metric_name": "Governance Maturity",
                "current_value": round(c_gov, 2),
                "previous_value": round(p_gov, 2),
                "trend_delta_percentage": gov_delta,
                "trend": gov_trend,
                "higher_is_better": True,
            },
            "outcome_trend": {
                "metric_name": "Outcome Achievement",
                "current_value": round(c_out, 2),
                "previous_value": round(p_out, 2),
                "trend_delta_percentage": out_delta,
                "trend": out_trend,
                "higher_is_better": True,
            },
            "roi_trend": {
                "metric_name": "Portfolio ROI",
                "current_value": round(c_roi, 2),
                "previous_value": round(p_roi, 2),
                "trend_delta_percentage": roi_delta,
                "trend": roi_trend,
                "higher_is_better": True,
            },
            "portfolio_trajectory_grade": trajectory_grade,
            "insufficient_history": False,
            "historical_snapshots_count": snapshots_count,
            "data_quality_warnings": warnings,
            "calculated_at": now,
        }
