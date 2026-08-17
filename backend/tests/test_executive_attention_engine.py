"""Unit tests for Phase 12.7 Executive Attention Engine."""

import uuid
from datetime import datetime, timedelta, timezone
import pytest
from app.execution.constants import ExecutiveAttentionLevel, StrategicTrend
from app.execution.services.executive_attention_engine import ExecutiveAttentionEngine


def test_executive_attention_5_factor_explainability():
    """Validates that 5-factor contributions sum precisely to the attention score."""
    init_id = uuid.uuid4()
    now = datetime.now(timezone.utc)
    first_triggered = now - timedelta(days=45)

    item = ExecutiveAttentionEngine.calculate_attention_item(
        initiative_id=init_id,
        initiative_title="Critical Delivery",
        risk_score=80.0,            # 0.30 * 80 = 24.0
        timeline_exposure=60.0,     # 0.25 * 60 = 15.0
        outcome_gap=50.0,           # 0.20 * 50 = 10.0
        governance_deficit=40.0,    # 0.15 * 40 = 6.0
        health_score=50.0,          # deficit = 50 -> 0.10 * 50 = 5.0
        previous_attention_score=40.0,
        first_triggered_at=first_triggered,
    )

    # 24.0 + 15.0 + 10.0 + 6.0 + 5.0 = 60.0
    expected_sum = (
        item["risk_contribution"]
        + item["timeline_contribution"]
        + item["outcome_contribution"]
        + item["governance_contribution"]
        + item["health_contribution"]
    )
    assert round(expected_sum, 2) == item["attention_score"]
    assert item["attention_score"] == 60.0
    assert item["attention_level"] == ExecutiveAttentionLevel.HIGH
    assert item["attention_trend"] == StrategicTrend.DETERIORATING  # Score increased from 40 to 60
    assert item["attention_age_days"] == 45
    assert len(item["primary_drivers"]) >= 3


def test_executive_attention_queue_sorting_and_filtering():
    """Validates deterministic descending queue sorting and level filtering."""
    id1, id2, id3 = uuid.uuid4(), uuid.uuid4(), uuid.uuid4()
    items = [
        ExecutiveAttentionEngine.calculate_attention_item(
            initiative_id=id1,
            initiative_title="Low Priority",
            risk_score=10.0,
            health_score=90.0,
        ),
        ExecutiveAttentionEngine.calculate_attention_item(
            initiative_id=id2,
            initiative_title="Critical Emergency",
            risk_score=90.0,
            timeline_exposure=90.0,
            health_score=30.0,
        ),
        ExecutiveAttentionEngine.calculate_attention_item(
            initiative_id=id3,
            initiative_title="Medium Issue",
            risk_score=50.0,
            health_score=70.0,
        ),
    ]

    queue_res = ExecutiveAttentionEngine.generate_attention_queue(items)
    assert queue_res["total_items_count"] == 3
    # Top item must be id2 (Critical Emergency)
    assert queue_res["queue"][0]["initiative_id"] == id2
    assert queue_res["queue"][1]["initiative_id"] == id3
    assert queue_res["queue"][2]["initiative_id"] == id1

    # Filtering by HIGH minimum level
    filtered = ExecutiveAttentionEngine.generate_attention_queue(items, min_level=ExecutiveAttentionLevel.HIGH)
    assert filtered["total_items_count"] >= 1
    assert all(i["attention_level"] in (ExecutiveAttentionLevel.HIGH, ExecutiveAttentionLevel.CRITICAL) for i in filtered["queue"])
