"""Workspace health extractor utility for Phase 11.0 Portfolio Intelligence."""

from typing import Any, Dict, Optional


class WorkspaceHealthExtractor:
    """
    Isolates the workspace_json health score and statistics access path.
    Primary canonical path: workspace_json["overview"]["scorecard"]["business_health_score"]
    
    Provides graceful fallback inspection so schema updates never break portfolio aggregation.
    """

    FALLBACK_SCORE: float = 0.0

    @classmethod
    def extract(cls, workspace_json: Optional[Dict[str, Any]]) -> float:
        """
        Extract health score from workspace_json safely.
        Never raises exceptions; returns FALLBACK_SCORE (0.0) if missing or non-numeric.
        """
        if not workspace_json or not isinstance(workspace_json, dict):
            return cls.FALLBACK_SCORE

        # 1. Primary path: workspace_json["overview"]["scorecard"]["business_health_score"]
        try:
            val = workspace_json.get("overview", {}).get("scorecard", {}).get("business_health_score")
            if val is not None:
                return float(val)
        except (ValueError, TypeError, AttributeError):
            pass

        # 2. Alternative path: workspace_json["overview"]["scorecard"]["health_score"]
        try:
            val = workspace_json.get("overview", {}).get("scorecard", {}).get("health_score")
            if val is not None:
                return float(val)
        except (ValueError, TypeError, AttributeError):
            pass

        # 3. Direct scorecard path: workspace_json["scorecard"]["health_score"]
        try:
            val = workspace_json.get("scorecard", {}).get("health_score")
            if val is not None:
                return float(val)
        except (ValueError, TypeError, AttributeError):
            pass

        # 4. Direct business_health_score in scorecard
        try:
            val = workspace_json.get("scorecard", {}).get("business_health_score")
            if val is not None:
                return float(val)
        except (ValueError, TypeError, AttributeError):
            pass

        # 5. Direct overview health_dimensions
        try:
            val = workspace_json.get("overview", {}).get("health_dimensions", {}).get("overall_score")
            if val is not None:
                return float(val)
        except (ValueError, TypeError, AttributeError):
            pass

        return cls.FALLBACK_SCORE

    @classmethod
    def extract_statistics(cls, workspace_json: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Extract diagnostic findings, recommendation counts, and forecast confidence from workspace_json.
        """
        if not workspace_json or not isinstance(workspace_json, dict):
            return {
                "finding_count": 0,
                "critical_finding_count": 0,
                "recommendation_count": 0,
                "kpi_score": None,
                "forecast_confidence": None,
            }

        overview = workspace_json.get("overview", {}) if isinstance(workspace_json.get("overview"), dict) else {}
        statistics = overview.get("statistics", {}) if isinstance(overview.get("statistics"), dict) else {}
        scorecard = overview.get("scorecard", {}) if isinstance(overview.get("scorecard"), dict) else {}

        # Critical findings from active_alerts or findings list
        active_alerts = overview.get("active_alerts", []) if isinstance(overview.get("active_alerts"), list) else []
        critical_alerts = sum(
            1 for a in active_alerts
            if isinstance(a, dict) and str(a.get("severity", "")).upper() == "CRITICAL"
        )

        findings_list = workspace_json.get("findings", []) if isinstance(workspace_json.get("findings"), list) else []
        recs_list = workspace_json.get("recommendations", []) if isinstance(workspace_json.get("recommendations"), list) else []

        finding_count = statistics.get("findings_count", len(findings_list))
        rec_count = statistics.get("recommendations_count", len(recs_list))

        forecast_conf = None
        try:
            fc_val = scorecard.get("forecast_confidence")
            if fc_val is not None:
                forecast_conf = float(fc_val)
        except (ValueError, TypeError):
            pass

        return {
            "finding_count": finding_count,
            "critical_finding_count": critical_alerts,
            "recommendation_count": rec_count,
            "kpi_score": None,
            "forecast_confidence": forecast_conf,
        }
