"""RecommendationRule data model mapping finding/root-cause pairs to recommendation templates."""

from dataclasses import dataclass, field
from typing import List, Optional

from app.core.constants import FindingSubtype, RecommendationType
from app.recommendations.template_model import RecommendationTemplate


@dataclass(frozen=True)
class RecommendationRule:
    """
    Domain rule mapping a specific business symptom (finding subtype) and optional
    root cause causal driver to one or more action templates.
    
    Attributes:
        finding_subtype: Diagnostic symptom subtype (e.g. DECLINE, MARGIN_COMPRESSION).
        root_cause_subtype: Optional causal driver subtype (e.g. CHURN_INCREASE, COST_SPIKE).
                            If None, rule acts as a general fallback for the finding subtype.
        recommendation_type: High-level classification (CUSTOMER_RETENTION, COST_OPTIMIZATION, etc.).
        priority_weight: Weight multiplier for priority calculation [0.0 - 1.0].
        impact_weight: Weight multiplier for impact estimation [0.0 - 1.0].
        effort_weight: Weight multiplier for effort estimation [0.0 - 1.0].
        templates: Collection of distinct actionable templates under this rule.
        description: Rationale and domain justification for this rule.
    """

    finding_subtype: FindingSubtype
    root_cause_subtype: Optional[FindingSubtype]
    recommendation_type: RecommendationType
    priority_weight: float
    impact_weight: float
    effort_weight: float
    templates: List[RecommendationTemplate]
    description: str

    def matches(
        self,
        candidate_finding_subtype: FindingSubtype | str,
        candidate_root_cause_subtype: Optional[FindingSubtype | str] = None,
    ) -> bool:
        """
        Evaluates whether this rule applies to the given finding and optional root cause.
        """
        f_sub = candidate_finding_subtype.value if hasattr(candidate_finding_subtype, "value") else str(candidate_finding_subtype)
        if f_sub != self.finding_subtype.value:
            return False

        # If rule specifies a root cause, candidate must match it
        if self.root_cause_subtype is not None:
            if candidate_root_cause_subtype is None:
                return False
            rc_sub = candidate_root_cause_subtype.value if hasattr(candidate_root_cause_subtype, "value") else str(candidate_root_cause_subtype)
            return rc_sub == self.root_cause_subtype.value

        # If rule does NOT require a specific root cause, it matches any root cause or None
        return True
