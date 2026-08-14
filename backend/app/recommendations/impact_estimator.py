"""Impact estimation engine for business recommendations."""

from typing import Optional

from app.models.diagnostic_finding import DiagnosticFinding
from app.models.root_cause_analysis import RootCauseAnalysis
from app.recommendations.constants import SEVERITY_WEIGHTS, STRENGTH_WEIGHTS
from app.recommendations.rule_model import RecommendationRule
from app.recommendations.template_model import RecommendationTemplate


class ImpactEstimator:
    """
    Estimates top-line and operational business impact score [0.0 - 1.0]
    for an actionable recommendation template.
    
    Factors considered:
        1. Finding Severity (magnitude of the problem addressed).
        2. Template Baseline Impact (intrinsic strategic value of the action).
        3. Rule Impact Weight (domain rule potency).
        4. Root Cause Relationship Strength (influence of the causal link).
        5. Statistical Confidence (confidence of diagnostic detection).
    """

    @classmethod
    def estimate(
        cls,
        template: RecommendationTemplate,
        finding: DiagnosticFinding,
        rule: RecommendationRule,
        rca: Optional[RootCauseAnalysis] = None,
    ) -> float:
        """
        Computes composite business impact score bounded strictly in [0.10, 1.00].
        """
        # 1. Finding Severity
        sev_str = finding.severity.value if hasattr(finding.severity, "value") else str(finding.severity)
        sev_wt = SEVERITY_WEIGHTS.get(sev_str.upper(), 0.50)

        # 2. Template baseline impact
        tmpl_impact = template.default_impact

        # 3. Rule impact weight
        rule_impact = rule.impact_weight

        # 4. RCA relationship strength
        if rca is not None and hasattr(rca, "relationship_strength"):
            strength_str = rca.relationship_strength.value if hasattr(rca.relationship_strength, "value") else str(rca.relationship_strength)
            rca_strength = STRENGTH_WEIGHTS.get(strength_str.upper(), 0.80)
        else:
            rca_strength = 0.70

        # 5. Combined Confidence
        finding_conf = getattr(finding, "confidence_score", 0.90)
        rca_conf = getattr(rca, "confidence_score", 1.00) if rca else 1.00
        combined_conf = finding_conf * rca_conf

        # Weighted calculation
        composite_impact = (
            (0.35 * sev_wt)
            + (0.35 * tmpl_impact)
            + (0.15 * rule_impact)
            + (0.10 * rca_strength)
            + (0.05 * combined_conf)
        )

        return round(max(0.10, min(1.00, composite_impact)), 4)
