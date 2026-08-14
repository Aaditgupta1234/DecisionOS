"""Strict reject-only deterministic validator for Scenario Simulation assumptions."""

from typing import Dict, List, Optional, Set
from app.scenario_simulation.constants import (
    ALLOWED_ADJUSTMENT_TYPES,
    METRIC_BOUNDARIES,
    SUPPORTED_SIMULATION_METRICS,
)
from app.scenario_simulation.schemas.scenario_schema import ScenarioAssumption


class ScenarioValidationError(Exception):
    """Raised when scenario assumptions violate deterministic simulation constraints or boundaries."""
    pass


class ScenarioValidator:
    """
    Pure deterministic validation engine enforcing strict metric existence,
    adjustment compatibility, and physical boundary constraints without silent repair.
    """

    @classmethod
    def validate_assumptions(
        cls,
        assumptions: List[ScenarioAssumption],
        dataset_metrics: Dict[str, float],
    ) -> None:
        """
        Validates a list of scenario assumptions against available dataset metrics.
        Raises ScenarioValidationError on any violation.
        """
        if not assumptions or len(assumptions) == 0:
            raise ScenarioValidationError("Scenario must contain at least one assumption.")

        seen_keys: Set[str] = set()

        for idx, assumption in enumerate(assumptions):
            key = assumption.metric_key
            adj_type = assumption.adjustment_type
            adj_val = assumption.adjustment_value

            # 1. Duplicate metric check
            if key in seen_keys:
                raise ScenarioValidationError(
                    f"Duplicate assumption detected for metric '{key}'. Each metric may only be adjusted once per scenario."
                )
            seen_keys.add(key)

            # 2. Metric support check
            if key not in SUPPORTED_SIMULATION_METRICS:
                raise ScenarioValidationError(
                    f"Metric '{key}' does not support scenario simulation. Supported metrics: {sorted(list(SUPPORTED_SIMULATION_METRICS))}."
                )

            # 3. Metric presence in dataset check
            if key not in dataset_metrics:
                raise ScenarioValidationError(
                    f"Metric '{key}' was not found in the baseline dataset metrics."
                )

            # 4. Adjustment type compatibility check
            allowed_types = ALLOWED_ADJUSTMENT_TYPES.get(key, set())
            if adj_type not in allowed_types:
                allowed_str = ", ".join([t.value for t in allowed_types])
                raise ScenarioValidationError(
                    f"Adjustment type '{adj_type.value}' is not supported for metric '{key}'. Allowed types: [{allowed_str}]."
                )

            # 5. Boundary calculation check
            baseline_val = dataset_metrics[key]
            boundary_rules = METRIC_BOUNDARIES.get(key, {})
            min_bound = boundary_rules.get("min")
            max_bound = boundary_rules.get("max")
            allow_float = boundary_rules.get("allow_float", True)

            # Calculate projected test value
            if adj_type.value == "RELATIVE_PERCENT":
                projected_test = baseline_val * (1.0 + (adj_val / 100.0))
            elif adj_type.value == "PERCENTAGE_POINTS":
                projected_test = baseline_val + adj_val
            elif adj_type.value == "ABSOLUTE_VALUE":
                projected_test = baseline_val + adj_val
            else:
                raise ScenarioValidationError(f"Unknown adjustment type '{adj_type}'.")

            if min_bound is not None and projected_test < min_bound:
                raise ScenarioValidationError(
                    f"Adjustment for '{key}' yields projected value {projected_test:.4f}, which breaches minimum boundary of {min_bound}."
                )

            if max_bound is not None and projected_test > max_bound:
                raise ScenarioValidationError(
                    f"Adjustment for '{key}' yields projected value {projected_test:.4f}, which breaches maximum boundary of {max_bound}."
                )
