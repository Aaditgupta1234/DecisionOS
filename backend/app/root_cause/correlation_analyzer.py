"""Statistical correlation analyzer evaluating empirical trend alignment between diagnostic findings."""

import math
from dataclasses import dataclass
from typing import List, Optional, Sequence

from app.models.diagnostic_finding import DiagnosticFinding
from app.root_cause.rule_model import RootCauseRule


@dataclass(frozen=True)
class CorrelationResult:
    """
    Empirical statistical analysis of metric trends between two findings.
    
    Attributes:
        coefficient: Pearson correlation coefficient [-1.0 to 1.0], or None if unavailable.
        correlation_direction: Directional trend alignment ("POSITIVE", "NEGATIVE", "NEUTRAL").
        correlation_strength: Categorical strength ("STRONG", "MODERATE", "WEAK", "NONE").
        supports_rule: True if empirical data corroborates the rule, False if contradictory,
                       None if time-series data is absent.
        sample_size: Number of aligned time periods or observation points analyzed.
    """

    coefficient: Optional[float]
    correlation_direction: str
    correlation_strength: str
    supports_rule: Optional[bool]
    sample_size: int

    def to_dict(self) -> dict:
        """Serializes the result to a clean dictionary for supporting_evidence."""
        return {
            "coefficient": self.coefficient,
            "correlation_direction": self.correlation_direction,
            "correlation_strength": self.correlation_strength,
            "supports_rule": self.supports_rule,
            "sample_size": self.sample_size,
        }


class CorrelationAnalyzer:
    """
    Evaluates empirical correlation and trend alignment across time-series observations.
    
    CRITICAL ARCHITECTURAL PRINCIPLE:
    Correlation alone NEVER creates causality. High correlation only acts as a corroborating
    or penalizing signal when an established domain causal rule is already present.
    """

    @classmethod
    def analyze_finding_pair(
        cls,
        cause_finding: DiagnosticFinding,
        effect_finding: DiagnosticFinding,
        rule: Optional[RootCauseRule] = None,
    ) -> CorrelationResult:
        """
        Extracts temporal data from finding supporting_data payloads and evaluates correlation.
        """
        cause_data = cause_finding.supporting_data or {}
        effect_data = effect_finding.supporting_data or {}

        cause_ctx = cause_data.get("context", {})
        effect_ctx = effect_data.get("context", {})

        # Attempt to extract time-series points if present
        cause_series = cause_ctx.get("time_series", [])
        effect_series = effect_ctx.get("time_series", [])

        if isinstance(cause_series, list) and isinstance(effect_series, list):
            if len(cause_series) >= 3 and len(cause_series) == len(effect_series):
                r = cls.compute_pearson_correlation(cause_series, effect_series)
                if r is not None:
                    return cls._build_result_from_pearson(r, len(cause_series), rule)

        # Fallback: Directional delta comparison from observed / change_percent
        cause_change = cause_ctx.get("change_percent") or cause_data.get("observed")
        effect_change = effect_ctx.get("change_percent") or effect_data.get("observed")

        if (
            isinstance(cause_change, (int, float))
            and isinstance(effect_change, (int, float))
            and not math.isnan(cause_change)
            and not math.isnan(effect_change)
        ):
            return cls._build_result_from_deltas(float(cause_change), float(effect_change), rule)

        # Neutral result when empirical time-series data is absent
        return CorrelationResult(
            coefficient=None,
            correlation_direction="NEUTRAL",
            correlation_strength="NONE",
            supports_rule=None,
            sample_size=0,
        )

    @classmethod
    def compute_pearson_correlation(
        cls,
        x: Sequence[float],
        y: Sequence[float],
    ) -> Optional[float]:
        """Calculates Pearson correlation coefficient r between two numerical sequences."""
        n = len(x)
        if n < 3 or len(y) != n:
            return None

        try:
            mean_x = sum(x) / n
            mean_y = sum(y) / n

            numer = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y))
            denom_x = sum((xi - mean_x) ** 2 for xi in x)
            denom_y = sum((yi - mean_y) ** 2 for yi in y)

            denom = math.sqrt(denom_x * denom_y)
            if denom == 0:
                return 0.0

            r = numer / denom
            return round(max(-1.0, min(1.0, r)), 4)
        except Exception:
            return None

    @classmethod
    def _build_result_from_pearson(
        cls,
        r: float,
        sample_size: int,
        rule: Optional[RootCauseRule],
    ) -> CorrelationResult:
        """Classifies strength and direction from Pearson r coefficient."""
        abs_r = abs(r)
        if abs_r >= 0.70:
            strength = "STRONG"
        elif abs_r >= 0.40:
            strength = "MODERATE"
        elif abs_r >= 0.15:
            strength = "WEAK"
        else:
            strength = "NONE"

        direction = "POSITIVE" if r > 0.05 else ("NEGATIVE" if r < -0.05 else "NEUTRAL")

        # Evaluate if empirical direction matches rule expectation
        supports_rule: Optional[bool] = None
        if rule is not None:
            if rule.expected_correlation == "ANY":
                supports_rule = strength in ("STRONG", "MODERATE")
            elif rule.expected_correlation == "POSITIVE":
                supports_rule = (direction == "POSITIVE" and strength in ("STRONG", "MODERATE"))
            elif rule.expected_correlation == "NEGATIVE":
                supports_rule = (direction == "NEGATIVE" and strength in ("STRONG", "MODERATE"))

        return CorrelationResult(
            coefficient=r,
            correlation_direction=direction,
            correlation_strength=strength,
            supports_rule=supports_rule,
            sample_size=sample_size,
        )

    @classmethod
    def _build_result_from_deltas(
        cls,
        cause_delta: float,
        effect_delta: float,
        rule: Optional[RootCauseRule],
    ) -> CorrelationResult:
        """Classifies directional alignment when only aggregate period deltas are available."""
        # Both moving in same direction (e.g. + + or - -) -> POSITIVE alignment
        # Opposite directions (e.g. Cause + and Effect -) -> NEGATIVE alignment
        if (cause_delta > 0 and effect_delta > 0) or (cause_delta < 0 and effect_delta < 0):
            direction = "POSITIVE"
            pseudo_r = 0.60
            strength = "MODERATE"
        elif (cause_delta > 0 and effect_delta < 0) or (cause_delta < 0 and effect_delta > 0):
            direction = "NEGATIVE"
            pseudo_r = -0.60
            strength = "MODERATE"
        else:
            direction = "NEUTRAL"
            pseudo_r = 0.0
            strength = "WEAK"

        supports_rule: Optional[bool] = None
        if rule is not None:
            if rule.expected_correlation == "ANY":
                supports_rule = True
            elif rule.expected_correlation == direction:
                supports_rule = True
            else:
                supports_rule = False

        return CorrelationResult(
            coefficient=pseudo_r,
            correlation_direction=direction,
            correlation_strength=strength,
            supports_rule=supports_rule,
            sample_size=2,
        )
