"""Unit tests for Phase 12.7 Portfolio Rankings Engine."""

import uuid
import pytest
from app.execution.constants import calculate_ranking_percentile
from app.execution.services.portfolio_ranking_engine import PortfolioRankingEngine


def test_ranking_percentile_formula():
    """Validates percentile calculation: 100 * (1 - ((rank - 1) / total_items))."""
    assert calculate_ranking_percentile(rank=1, total_items=100) == 100.0
    assert calculate_ranking_percentile(rank=3, total_items=100) == 98.0
    assert calculate_ranking_percentile(rank=50, total_items=100) == 51.0
    assert calculate_ranking_percentile(rank=100, total_items=100) == 1.0


def test_portfolio_rankings_deterministic_tie_breakers():
    """Validates multi-dimensional rankings consistency and tie-breaking order."""
    id1, id2, id3 = uuid.uuid4(), uuid.uuid4(), uuid.uuid4()
    initiatives = [
        {
            "id": id1,
            "title": "Alpha (Equal Value, Higher Outcome)",
            "strategic_value_score": 85.0,
            "outcome_achievement": 95.0,
            "roi_score": 50.0,
            "risk_score": 10.0,
            "value_efficiency_score": 90.0,
            "governance_maturity_score": 80.0,
        },
        {
            "id": id2,
            "title": "Beta (Equal Value, Lower Outcome)",
            "strategic_value_score": 85.0,
            "outcome_achievement": 80.0,
            "roi_score": 60.0,
            "risk_score": 40.0,
            "value_efficiency_score": 60.0,
            "governance_maturity_score": 95.0,
        },
        {
            "id": id3,
            "title": "Gamma (Highest Risk, Lowest Efficiency)",
            "strategic_value_score": 40.0,
            "outcome_achievement": 30.0,
            "roi_score": 10.0,
            "risk_score": 90.0,
            "value_efficiency_score": 25.0,
            "governance_maturity_score": 50.0,
        },
    ]

    rankings = PortfolioRankingEngine.rank_portfolio(initiatives, limit=5)

    # 1. Top Value: id1 wins tie-break over id2 due to higher outcome_achievement (95 > 80)
    top_val = rankings["top_strategic_value_initiatives"]
    assert top_val[0]["initiative_id"] == id1
    assert top_val[1]["initiative_id"] == id2
    assert top_val[0]["rank"] == 1
    assert top_val[0]["ranking_percentile"] == 100.0

    # 2. Top ROI: id2 (60) > id1 (50) > id3 (10)
    top_roi = rankings["top_roi_initiatives"]
    assert top_roi[0]["initiative_id"] == id2
    assert top_roi[1]["initiative_id"] == id1

    # 3. Highest Risk: id3 (90) > id2 (40) > id1 (10)
    highest_risk = rankings["highest_risk_initiatives"]
    assert highest_risk[0]["initiative_id"] == id3

    # 4. Lowest Value Efficiency: id3 (25) < id2 (60) < id1 (90)
    lowest_eff = rankings["lowest_value_efficiency_initiatives"]
    assert lowest_eff[0]["initiative_id"] == id3

    # 5. Highest Governance: id2 (95) > id1 (80) > id3 (50)
    highest_gov = rankings["highest_governance_maturity_initiatives"]
    assert highest_gov[0]["initiative_id"] == id2
