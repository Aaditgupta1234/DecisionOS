"""Unit tests for ScenarioRuleRegistry dependency-ordered propagation and cycle protection."""

import pytest
from app.scenario_simulation.engines.scenario_rule_registry import (
    ScenarioRule,
    ScenarioRuleRegistry,
)


@pytest.fixture
def base_metrics():
    return {
        "total_revenue": 100000.0,
        "average_revenue": 100.0,
        "total_orders": 1000.0,
        "completed_orders": 850.0,
        "cancelled_orders": 150.0,
        "completion_rate": 85.0,
        "unique_customers": 500.0,
        "revenue_per_customer": 200.0,
        "customer_churn_rate": 20.0,
        "customer_retention_rate": 80.0,
    }


def test_scenario_rule_registry_churn_to_retention_propagation(base_metrics):
    """Verifies that directly modifying churn propagates to retention rate."""
    registry = ScenarioRuleRegistry()
    working = dict(base_metrics)
    working["customer_churn_rate"] = 15.0  # Directly assumed

    updated, sources = registry.apply_propagation(
        current_metrics=working,
        directly_assumed_keys={"customer_churn_rate"},
    )

    assert updated["customer_churn_rate"] == 15.0
    assert updated["customer_retention_rate"] == 85.0
    assert sources["customer_retention_rate"] == "rule_churn_to_retention"


def test_scenario_rule_registry_retention_to_churn_propagation(base_metrics):
    """Verifies that directly modifying retention propagates to churn rate."""
    registry = ScenarioRuleRegistry()
    working = dict(base_metrics)
    working["customer_retention_rate"] = 92.0  # Directly assumed

    updated, sources = registry.apply_propagation(
        current_metrics=working,
        directly_assumed_keys={"customer_retention_rate"},
    )

    assert updated["customer_retention_rate"] == 92.0
    assert updated["customer_churn_rate"] == 8.0
    assert sources["customer_churn_rate"] == "rule_retention_to_churn"


def test_scenario_rule_registry_circular_cycle_protection(base_metrics):
    """
    CRITICAL TEST: Proves that bidirectional rules (churn <-> retention) evaluate in a Directed
    Acyclic manner and NEVER overwrite the directly assumed root metric or create an infinite loop.
    """
    registry = ScenarioRuleRegistry()
    working = dict(base_metrics)
    working["customer_churn_rate"] = 12.0  # Direct assumption

    updated, sources = registry.apply_propagation(
        current_metrics=working,
        directly_assumed_keys={"customer_churn_rate"},
    )

    # Directly assumed churn must remain exactly 12.0
    assert updated["customer_churn_rate"] == 12.0
    assert updated["customer_retention_rate"] == 88.0

    # Running propagation a second time on the result produces identical deterministic state
    updated_again, sources_again = registry.apply_propagation(
        current_metrics=updated,
        directly_assumed_keys={"customer_churn_rate"},
    )
    assert updated_again["customer_churn_rate"] == 12.0
    assert updated_again["customer_retention_rate"] == 88.0


def test_scenario_rule_registry_orders_and_completion_propagation(base_metrics):
    """Verifies chained dependency: total_orders + completion_rate -> completed_orders -> cancelled_orders."""
    registry = ScenarioRuleRegistry()
    working = dict(base_metrics)
    working["total_orders"] = 2000.0  # Assumed
    working["completion_rate"] = 90.0  # Assumed

    updated, sources = registry.apply_propagation(
        current_metrics=working,
        directly_assumed_keys={"total_orders", "completion_rate"},
    )

    assert updated["completed_orders"] == 1800.0
    assert updated["cancelled_orders"] == 200.0
    assert sources["completed_orders"] == "rule_orders_completion"
    assert sources["cancelled_orders"] == "rule_orders_cancellation"


def test_scenario_rule_registry_revenue_average_and_per_customer(base_metrics):
    """Verifies total_revenue propagation to average_revenue and revenue_per_customer."""
    registry = ScenarioRuleRegistry()
    working = dict(base_metrics)
    working["total_revenue"] = 200000.0  # Doubled revenue

    updated, sources = registry.apply_propagation(
        current_metrics=working,
        directly_assumed_keys={"total_revenue"},
    )

    assert updated["average_revenue"] == 200.0  # 200,000 / 1,000 orders
    assert updated["revenue_per_customer"] == 400.0  # 200,000 / 500 customers
    assert sources["average_revenue"] == "rule_revenue_average"
    assert sources["revenue_per_customer"] == "rule_revenue_per_customer"


def test_scenario_rule_registry_no_unsupported_causal_propagation(base_metrics):
    """
    Verifies that changing churn does NOT magically modify unrelated metrics (e.g. revenue)
    without an explicit deterministic rule.
    """
    registry = ScenarioRuleRegistry()
    working = dict(base_metrics)
    working["customer_churn_rate"] = 5.0  # Big churn drop

    updated, sources = registry.apply_propagation(
        current_metrics=working,
        directly_assumed_keys={"customer_churn_rate"},
    )

    # Revenue must remain completely unchanged
    assert updated["total_revenue"] == base_metrics["total_revenue"]
    assert "total_revenue" not in sources
