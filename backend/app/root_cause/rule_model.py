"""Root Cause Rule data model representing a domain-validated causal relationship."""

from dataclasses import dataclass, field
from typing import Optional

from app.core.constants import FindingSubtype, RelationshipStrength, RelationshipType
from app.root_cause.constants import numeric_to_relationship_strength


@dataclass(frozen=True)
class RootCauseRule:
    """
    Defines a validated causal relationship connecting a source anomaly/driver (cause)
    to a target business outcome (effect).
    
    Attributes:
        cause_subtype: Subtype of the driver finding (e.g. CHURN_INCREASE, COST_SPIKE).
        effect_subtype: Subtype of the impacted finding (e.g. DECLINE, MARGIN_COMPRESSION).
        relationship_type: Classification (CAUSES, CONTRIBUTES_TO, AMPLIFIES, etc.).
        relationship_strength: Float weight [0.0 - 1.0] reflecting intrinsic causal power.
        description: Authoritative explanation of the causal mechanism.
        expected_correlation: Expected empirical time-series correlation ("POSITIVE", "NEGATIVE", "ANY").
        min_confidence: Threshold below which candidate findings will not trigger this rule.
    """

    cause_subtype: FindingSubtype
    effect_subtype: FindingSubtype
    relationship_type: RelationshipType
    relationship_strength: float
    description: str
    expected_correlation: str = "NEGATIVE"
    min_confidence: float = 0.50

    @property
    def strength_enum(self) -> RelationshipStrength:
        """Returns the discrete RelationshipStrength enum for this rule."""
        return numeric_to_relationship_strength(self.relationship_strength)

    def matches(
        self,
        candidate_cause: FindingSubtype | str,
        candidate_effect: FindingSubtype | str,
    ) -> bool:
        """Evaluates whether the candidate finding subtypes match this causal rule."""
        c_cause = candidate_cause.value if hasattr(candidate_cause, "value") else str(candidate_cause)
        c_effect = candidate_effect.value if hasattr(candidate_effect, "value") else str(candidate_effect)
        return (c_cause == self.cause_subtype.value) and (c_effect == self.effect_subtype.value)
