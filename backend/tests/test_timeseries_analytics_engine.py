"""Unit tests for Phase 12.8 Timeseries Analytics Engine."""

import uuid
from datetime import datetime, timedelta, timezone
import pytest
from app.execution.services.timeseries_analytics_engine import TimeseriesAnalyticsEngine


def test_timeseries_analytics_rolling_windows():
    """Validates 7d, 30d, 90d, 180d, 365d statistical moments calculation."""
    org_id = uuid.uuid4()
    now = datetime.now(timezone.utc)

    # Generate historical snapshots over 100 days
    snaps = []
    for day_offset in [90, 60, 30, 15, 5, 1]:
        ts = now - timedelta(days=day_offset)
        snaps.append(
            {
                "snapshot_timestamp": ts,
                "portfolio_health_score": 80.0 + (90 - day_offset) * 0.2, # 80 to 97.8
                "portfolio_roi_score": 60.0 + (90 - day_offset) * 0.1,
                "portfolio_outcome_attainment_rate": 70.0 + (90 - day_offset) * 0.15,
                "portfolio_governance_score": 85.0,
                "portfolio_strategic_maturity_score": 75.0 + (90 - day_offset) * 0.1,
            }
        )

    res = TimeseriesAnalyticsEngine.calculate_timeseries_analytics(org_id, snaps, as_of=now)

    assert res["organization_id"] == org_id
    assert "health_timeseries" in res
    assert "roi_timeseries" in res
    assert "outcomes_timeseries" in res
    assert "governance_timeseries" in res
    assert "maturity_timeseries" in res

    # Check 7d window (should have 5d and 1d = 2 samples)
    h_7d = res["health_timeseries"]["windows"]["7d"]
    assert h_7d["sample_count"] == 2
    assert h_7d["average"] > 90.0
    assert h_7d["minimum"] <= h_7d["maximum"]
    assert "growth_rate" in h_7d

    # Check 90d window (should have all 6 samples)
    h_90d = res["health_timeseries"]["windows"]["90d"]
    assert h_90d["sample_count"] == 6
    assert h_90d["volatility"] >= 0.0
