"""Unit tests for Cross-Workspace Portfolio Governance Enhancement."""

import uuid
import pytest
from app.reporting.services.portfolio_governance_engine import PortfolioGovernanceEngine


def test_portfolio_briefing_generation():
    """Verify portfolio executive briefing aggregates multiple workspace directives and ARR values."""
    portfolio_id = uuid.uuid4()
    briefing = PortfolioGovernanceEngine.generate_portfolio_briefing(portfolio_id=portfolio_id)

    assert briefing["portfolio_id"] == portfolio_id
    assert len(briefing["portfolio_directives"]) == 3
    assert briefing["arr_attribution"]["total_expected_arr"] > 0
    assert briefing["arr_attribution"]["total_actual_arr"] > 0
    assert briefing["governance_scorecard"]["portfolio_governance_index"] > 95.0
    assert briefing["validation"]["can_publish"] is True


def test_portfolio_anti_hallucination_validation_blocks_empty_or_mismatched_contributions():
    """Verify validation engine flags missing workspace evidence or ARR sum mismatches."""
    # Test 1: Directive without workspace contributions
    bad_directives = [
        {
            "portfolio_directive_id": "PORT-DIR-BAD",
            "expected_arr": 100000.0,
            "workspace_contributions": [],
        }
    ]
    val1 = PortfolioGovernanceEngine.validate_portfolio_grounding(bad_directives)
    assert val1["can_publish"] is False
    assert len(val1["blocking_errors"]) > 0

    # Test 2: ARR sum mismatch
    bad_math_directives = [
        {
            "portfolio_directive_id": "PORT-DIR-MATH-ERR",
            "expected_arr": 100000.0,
            "workspace_contributions": [
                {"workspace_id": "ws-1", "arr_contribution": 40000.0}  # 40k != 100k
            ],
        }
    ]
    val2 = PortfolioGovernanceEngine.validate_portfolio_grounding(bad_math_directives)
    assert val2["can_publish"] is False
