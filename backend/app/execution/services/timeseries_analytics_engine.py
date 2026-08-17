"""Time-Series Analytics Engine for Phase 12.8."""

import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
from app.execution.constants import (
    STRATEGIC_SNAPSHOT_METRIC_VERSION,
    TIMESERIES_ANALYTICS_ENGINE_VERSION,
    TimeWindowDays,
    calculate_rolling_stats,
)


class TimeseriesAnalyticsEngine:
    """
    Deterministic rolling time-series analytics engine across 7d, 30d, 90d, 180d, and 365d windows.
    Computes statistical moments: average, median, min, max, variance, volatility (CV), and growth rate.
    """

    ENGINE_VERSION = TIMESERIES_ANALYTICS_ENGINE_VERSION
    SNAPSHOT_METRIC_VERSION = STRATEGIC_SNAPSHOT_METRIC_VERSION

    WINDOWS = [
        TimeWindowDays.WINDOW_7D,
        TimeWindowDays.WINDOW_30D,
        TimeWindowDays.WINDOW_90D,
        TimeWindowDays.WINDOW_180D,
        TimeWindowDays.WINDOW_365D,
    ]

    @classmethod
    def calculate_timeseries_analytics(
        cls,
        organization_id: uuid.UUID,
        snapshots: List[Dict[str, Any]],
        as_of: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Computes rolling window statistical analytics across Health, ROI, Outcomes, Governance, and Maturity.
        Snapshots are expected to have a 'snapshot_timestamp' or 'created_at'.
        """
        now = as_of or datetime.now(timezone.utc)
        warnings: List[str] = []

        if not snapshots:
            warnings.append("No historical snapshots available for time-series analytics.")

        # Ensure tz-aware timestamps
        def _get_ts(s: Dict[str, Any]) -> datetime:
            ts = s.get("snapshot_timestamp") or s.get("created_at")
            if isinstance(ts, str):
                ts = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            if ts is None:
                ts = now
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
            return ts

        # Domain extractors
        domain_extractors = {
            "health": lambda s: float(s.get("portfolio_health_score", s.get("health_score", 100.0))),
            "roi": lambda s: float(s.get("portfolio_roi_score", s.get("roi_score", 0.0))),
            "outcomes": lambda s: float(s.get("portfolio_outcome_attainment_rate", s.get("outcome_score", 0.0))),
            "governance": lambda s: float(s.get("portfolio_governance_score", s.get("governance_score", 100.0))),
            "maturity": lambda s: float(s.get("portfolio_strategic_maturity_score", s.get("maturity_score", 0.0))),
        }

        domain_results: Dict[str, Any] = {}

        for domain, extractor in domain_extractors.items():
            current_val = extractor(snapshots[-1]) if snapshots else 0.0
            windows_dict: Dict[str, Any] = {}

            for w_enum in cls.WINDOWS:
                w_days = w_enum.value
                w_key = f"{w_days}d"
                cutoff = now - timedelta(days=w_days)

                # Filter snapshots within window
                window_snapshots = [s for s in snapshots if _get_ts(s) >= cutoff]
                vals = [extractor(s) for s in window_snapshots]

                if len(vals) < 2 and len(snapshots) >= 2:
                    warnings.append(f"Sparse snapshot history for {domain} in {w_key} window ({len(vals)} data points).")

                stats = calculate_rolling_stats(vals)
                windows_dict[w_key] = {
                    "window_days": w_days,
                    "sample_count": len(vals),
                    "average": stats["average"],
                    "median": stats["median"],
                    "minimum": stats["minimum"],
                    "maximum": stats["maximum"],
                    "variance": stats["variance"],
                    "volatility": stats["volatility"],
                    "growth_rate": stats["growth_rate"],
                }

            domain_results[f"{domain}_timeseries"] = {
                "domain": domain,
                "current_value": current_val,
                "windows": windows_dict,
            }

        # Deduplicate warnings
        unique_warnings = list(dict.fromkeys(warnings))

        return {
            "organization_id": organization_id,
            "health_timeseries": domain_results["health_timeseries"],
            "roi_timeseries": domain_results["roi_timeseries"],
            "outcomes_timeseries": domain_results["outcomes_timeseries"],
            "governance_timeseries": domain_results["governance_timeseries"],
            "maturity_timeseries": domain_results["maturity_timeseries"],
            "data_quality_warnings": unique_warnings,
            "calculated_at": now,
        }
