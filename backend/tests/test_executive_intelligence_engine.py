"""Unit tests for Phase 12.7 Executive Intelligence Engine."""

import uuid
import pytest
from app.execution.constants import (
    ExecutiveAttentionLevel,
    ExecutiveFindingSeverity,
    StrategicPriority,
)
from app.execution.services.executive_intelligence_engine import ExecutiveIntelligenceEngine


def test_executive_intelligence_generation():
    """Validates deterministic findings with severity, opportunities, risks, and recommendations."""
    id1 = uuid.uuid4()
    diagnostics = {
        "high_value_initiatives": [{"initiative_id": id1, "title": "Init 1"}],
        "high_roi_initiatives": [{"initiative_id": id1, "title": "Init 1"}],
        "underperforming_initiatives": [{"initiative_id": id1, "title": "Init 1"}],
        "governance_bottlenecks": [],
        "critical_outcome_exposures": [],
        "value_concentration": {
            "top_10_percent_value_share": 60.0,
            "top_20_percent_value_share": 85.0,
            "herfindahl_index": 2500.0,
        },
        "dependency_concentration": {
            "single_point_of_failure_count": 2,
            "max_dependent_initiatives": 4,
        },
    }

    res = ExecutiveIntelligenceEngine.generate_executive_intelligence(
        initiatives=[{"id": id1, "title": "Core Init"}],
        diagnostics=diagnostics,
        attention_score=80.0,
        portfolio_maturity_score=85.0,
        total_value_at_risk=600000.0,
    )

    assert res["executive_attention_level"] == ExecutiveAttentionLevel.CRITICAL
    assert len(res["top_findings"]) >= 2
    assert any(f["severity"] == ExecutiveFindingSeverity.CRITICAL for f in res["top_findings"])
    assert len(res["top_opportunities"]) >= 1
    assert len(res["top_risks"]) >= 1
    assert len(res["recommendations"]) >= 1
    assert any(r["priority"] == StrategicPriority.ESCALATE for r in res["recommendations"])
