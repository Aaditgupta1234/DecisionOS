"""Unit tests for StrategyValidator deterministic trust boundary."""

import pytest
from app.strategy_planner.validators.strategy_validator import (
    StrategyValidationError,
    StrategyValidator,
)


@pytest.fixture
def allowed_recs():
    return {"rec-aaa-111", "rec-bbb-222"}


@pytest.fixture
def allowed_kpis():
    return {"recurring_revenue", "customer_retention_rate"}


@pytest.fixture
def valid_plan():
    return {
        "title": "Turnaround Strategy",
        "objective": "Reverse churn",
        "executive_summary": "Summary...",
        "strategic_priorities": [
            {
                "title": "Priority 1",
                "priority": "HIGH",
                "source_recommendation_ids": ["rec-aaa-111"],
                "rationale": "High impact",
            }
        ],
        "action_items": [
            {
                "title": "Immediate Action",
                "description": "Do this now",
                "time_horizon": "IMMEDIATE",
                "source_recommendation_id": "rec-aaa-111",
                "dependencies": [],
            },
            {
                "title": "30 Day Action",
                "description": "Deploy workflow",
                "time_horizon": "30_DAYS",
                "source_recommendation_id": "rec-bbb-222",
                "dependencies": [],
            },
        ],
        "milestones": [
            {
                "title": "Day 30 Checkpoint",
                "time_horizon": "30_DAYS",
                "focus_area": "Retention",
            }
        ],
        "success_criteria": [
            {
                "metric_key": "customer_retention_rate",
                "target_direction": "IMPROVE",
                "source": "existing_kpi",
            }
        ],
        "source_recommendation_ids": ["rec-aaa-111", "rec-bbb-222"],
    }


def test_strategy_validator_valid_plan_passes(valid_plan, allowed_recs, allowed_kpis):
    """Verifies that a valid plan strictly complying with allowlists passes validation without error."""
    StrategyValidator.validate(
        plan_dict=valid_plan,
        allowed_recommendation_ids=allowed_recs,
        allowed_metric_keys=allowed_kpis,
    )


def test_strategy_validator_rejects_unknown_recommendation_id(valid_plan, allowed_recs, allowed_kpis):
    """Verifies strict rejection when an action item references an unknown or unallowed recommendation ID."""
    invalid_plan = dict(valid_plan)
    invalid_plan["action_items"] = [
        {
            "title": "Hallucinated Action",
            "time_horizon": "IMMEDIATE",
            "source_recommendation_id": "rec-fake-999",  # Not in allowlist
        }
    ]

    with pytest.raises(StrategyValidationError) as exc:
        StrategyValidator.validate(
            plan_dict=invalid_plan,
            allowed_recommendation_ids=allowed_recs,
            allowed_metric_keys=allowed_kpis,
        )
    assert "references invalid or unallowed source recommendation ID" in str(exc.value)


def test_strategy_validator_rejects_missing_source_recommendation(valid_plan, allowed_recs, allowed_kpis):
    """Verifies strict rejection when an action item lacks a source_recommendation_id."""
    invalid_plan = dict(valid_plan)
    invalid_plan["action_items"] = [
        {
            "title": "Unlinked Action",
            "time_horizon": "IMMEDIATE",
            "source_recommendation_id": None,
        }
    ]

    with pytest.raises(StrategyValidationError) as exc:
        StrategyValidator.validate(
            plan_dict=invalid_plan,
            allowed_recommendation_ids=allowed_recs,
            allowed_metric_keys=allowed_kpis,
        )
    assert "references invalid or unallowed source recommendation ID" in str(exc.value)


def test_strategy_validator_rejects_unknown_kpi_key(valid_plan, allowed_recs, allowed_kpis):
    """Verifies strict rejection when a success criterion cites a fabricated metric_key."""
    invalid_plan = dict(valid_plan)
    invalid_plan["success_criteria"] = [
        {
            "metric_key": "hallucinated_roi_index",  # Not in allowed_kpis
            "target_direction": "IMPROVE",
            "source": "existing_kpi",
        }
    ]

    with pytest.raises(StrategyValidationError) as exc:
        StrategyValidator.validate(
            plan_dict=invalid_plan,
            allowed_recommendation_ids=allowed_recs,
            allowed_metric_keys=allowed_kpis,
        )
    assert "references unknown or unallowed metric_key" in str(exc.value)


def test_strategy_validator_rejects_invalid_time_horizon(valid_plan, allowed_recs, allowed_kpis):
    """Verifies strict rejection when an invalid time horizon is provided."""
    invalid_plan = dict(valid_plan)
    invalid_plan["action_items"] = [
        {
            "title": "Action",
            "time_horizon": "INVALID_HORIZON_120_DAYS",
            "source_recommendation_id": "rec-aaa-111",
        }
    ]

    with pytest.raises(StrategyValidationError) as exc:
        StrategyValidator.validate(
            plan_dict=invalid_plan,
            allowed_recommendation_ids=allowed_recs,
            allowed_metric_keys=allowed_kpis,
        )
    assert "specifies invalid time horizon" in str(exc.value)


def test_strategy_validator_rejects_invalid_priority_recommendation_id(valid_plan, allowed_recs, allowed_kpis):
    """Verifies strict rejection when strategic priorities cite non-existent recommendation IDs."""
    invalid_plan = dict(valid_plan)
    invalid_plan["strategic_priorities"] = [
        {
            "title": "Invalid Priority",
            "priority": "HIGH",
            "source_recommendation_ids": ["rec-not-allowed-777"],
        }
    ]

    with pytest.raises(StrategyValidationError) as exc:
        StrategyValidator.validate(
            plan_dict=invalid_plan,
            allowed_recommendation_ids=allowed_recs,
            allowed_metric_keys=allowed_kpis,
        )
    assert "references invalid recommendation ID" in str(exc.value)


def test_strategy_validator_rejects_invalid_json_type(allowed_recs, allowed_kpis):
    """Verifies rejection when input is not a dictionary."""
    with pytest.raises(StrategyValidationError) as exc:
        StrategyValidator.validate(
            plan_dict="not a dict",
            allowed_recommendation_ids=allowed_recs,
            allowed_metric_keys=allowed_kpis,
        )
    assert "not a valid JSON dictionary" in str(exc.value)
