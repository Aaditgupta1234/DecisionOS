"""MetricProjectionEngine computing deterministic direct metric adjustments with boundary enforcement."""

from decimal import Decimal, ROUND_HALF_UP
from typing import Optional
from app.core.constants import ScenarioAdjustmentType
from app.scenario_simulation.constants import METRIC_BOUNDARIES


class MetricBoundaryError(Exception):
    """Raised when a projected metric value breaches physical or logical boundaries."""
    pass


class MetricProjectionEngine:
    """
    Computes precise, deterministic metric projections for direct scenario assumptions.
    """

    @classmethod
    def project_value(
        cls,
        baseline_value: float,
        adjustment_type: ScenarioAdjustmentType,
        adjustment_value: float,
        metric_key: Optional[str] = None,
    ) -> float:
        """
        Applies mathematical adjustment to baseline value using exact decimal arithmetic.
        """
        b_dec = Decimal(str(baseline_value))
        adj_dec = Decimal(str(adjustment_value))

        if adjustment_type == ScenarioAdjustmentType.RELATIVE_PERCENT:
            # projected = baseline * (1 + adj / 100)
            multiplier = Decimal("1.0") + (adj_dec / Decimal("100.0"))
            proj_dec = b_dec * multiplier
        elif adjustment_type in (ScenarioAdjustmentType.PERCENTAGE_POINTS, ScenarioAdjustmentType.ABSOLUTE_VALUE):
            # projected = baseline + adj
            proj_dec = b_dec + adj_dec
        else:
            raise ValueError(f"Unsupported adjustment type: {adjustment_type}")

        # Round to 4 decimal places
        proj_val = float(proj_dec.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP))

        # Check boundaries if metric_key provided
        if metric_key and metric_key in METRIC_BOUNDARIES:
            rules = METRIC_BOUNDARIES[metric_key]
            min_b = rules.get("min")
            max_b = rules.get("max")
            allow_float = rules.get("allow_float", True)

            if min_b is not None and proj_val < min_b:
                raise MetricBoundaryError(
                    f"Projected value {proj_val} for '{metric_key}' breaches minimum boundary of {min_b}."
                )
            if max_b is not None and proj_val > max_b:
                raise MetricBoundaryError(
                    f"Projected value {proj_val} for '{metric_key}' breaches maximum boundary of {max_b}."
                )

            if not allow_float:
                proj_val = round(proj_val)

        return proj_val
