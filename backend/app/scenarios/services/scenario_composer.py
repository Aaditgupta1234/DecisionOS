"""Scenario Composer Engine for Phase 6.4."""

from typing import Any, Dict


class ScenarioComposer:
    """Composes baseline deltas and sets candidate parameters for scenario modeling."""

    @classmethod
    def compose_scenario_parameters(cls, scenario_type: str, custom_params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Composes default parameters based on strategic scenario archetype."""
        custom_params = custom_params or {}

        if scenario_type == "RETENTION_FIRST":
            base = {
                "retention_lift_pct": 5.0,
                "courier_sla_penalty_rate": 15.0,
                "winback_discount_spend": 25800.0,
                "logistics_cost_reduction_pct": 10.0,
            }
        elif scenario_type == "GROWTH_OPTIMIZATION":
            base = {
                "marketing_budget_increase_pct": 20.0,
                "paid_acquisition_expansion_pct": 15.0,
                "logistics_cost_reduction_pct": 5.0,
                "retention_lift_pct": 2.5,
            }
        elif scenario_type == "EFFICIENCY_BOOST":
            base = {
                "logistics_cost_reduction_pct": 18.0,
                "inventory_velocity_lift_pct": 15.0,
                "support_automation_pct": 25.0,
                "retention_lift_pct": 1.0,
            }
        else:
            base = {
                "retention_lift_pct": 3.0,
                "marketing_budget_increase_pct": 10.0,
                "logistics_cost_reduction_pct": 8.0,
            }

        base.update(custom_params)
        return base
