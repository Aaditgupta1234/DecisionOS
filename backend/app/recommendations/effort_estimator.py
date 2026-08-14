"""Effort estimation engine for business recommendations."""

from typing import Optional

from app.models.diagnostic_finding import DiagnosticFinding
from app.recommendations.rule_model import RecommendationRule
from app.recommendations.template_model import RecommendationTemplate


class EffortEstimator:
    """
    Estimates implementation effort and resource intensity score [0.0 - 1.0]
    for an actionable recommendation template.
    
    Factors considered:
        1. Template Baseline Effort (intrinsic operational complexity).
        2. Rule Effort Weight (domain rule benchmark).
    """

    @classmethod
    def estimate(
        cls,
        template: RecommendationTemplate,
        rule: RecommendationRule,
        finding: Optional[DiagnosticFinding] = None,
    ) -> float:
        """
        Computes composite execution effort score bounded strictly in [0.10, 1.00].
        """
        tmpl_effort = template.default_effort
        rule_effort = rule.effort_weight

        composite_effort = (0.70 * tmpl_effort) + (0.30 * rule_effort)
        return round(max(0.10, min(1.00, composite_effort)), 4)
