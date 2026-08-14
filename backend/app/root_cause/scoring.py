"""Root cause confidence and business impact scoring algorithms."""

from typing import Optional

from app.models.diagnostic_finding import DiagnosticFinding
from app.root_cause.constants import (
    CORRELATION_CONTRADICTION_PENALTY,
    CORRELATION_SUPPORT_BONUS,
    EVIDENCE_COUNT_BONUS_PER_ITEM,
    SEVERITY_WEIGHTS,
)
from app.root_cause.correlation_analyzer import CorrelationResult
from app.root_cause.rule_model import RootCauseRule


def calculate_root_cause_confidence(
    cause_finding: DiagnosticFinding,
    effect_finding: DiagnosticFinding,
    rule: RootCauseRule,
    correlation_result: Optional[CorrelationResult] = None,
    evidence_count: int = 1,
) -> float:
    """
    Computes statistical and domain confidence score for a candidate causal link.
    
    Formula:
        Confidence = (Rule_Strength * Cause_Conf * Effect_Conf)
                     + Correlation_Adjustment + Evidence_Bonus
    
    Guarantees:
        Output is bounded in [0.10, 1.00].
    """
    cause_conf = getattr(cause_finding, "confidence_score", 1.0)
    effect_conf = getattr(effect_finding, "confidence_score", 1.0)

    # 1. Base Prior Confidence
    base_confidence = rule.relationship_strength * cause_conf * effect_conf

    # 2. Empirical Correlation Modulator
    corr_adjustment = 0.0
    if correlation_result is not None:
        if correlation_result.supports_rule is True:
            corr_adjustment = CORRELATION_SUPPORT_BONUS
        elif correlation_result.supports_rule is False:
            corr_adjustment = -CORRELATION_CONTRADICTION_PENALTY

    # 3. Evidence Count Bonus
    evidence_bonus = min(0.06, max(0, (evidence_count - 1) * EVIDENCE_COUNT_BONUS_PER_ITEM))

    total_conf = base_confidence + corr_adjustment + evidence_bonus
    return round(max(0.10, min(1.00, total_conf)), 4)


def calculate_impact_score(
    effect_finding: DiagnosticFinding,
    cause_finding: DiagnosticFinding,
    rule: RootCauseRule,
) -> float:
    """
    Computes the downstream business impact magnitude of the causal relationship.
    
    Weights:
        - 50% Effect Severity (the criticality of the problem being explained)
        - 25% Cause Severity (the intensity of the driver)
        - 25% Causal Relationship Strength (the degree of influence)
    
    Guarantees:
        Output is bounded in [0.10, 1.00].
    """
    effect_sev_str = effect_finding.severity.value if hasattr(effect_finding.severity, "value") else str(effect_finding.severity)
    cause_sev_str = cause_finding.severity.value if hasattr(cause_finding.severity, "value") else str(cause_finding.severity)

    effect_wt = SEVERITY_WEIGHTS.get(effect_sev_str.upper(), 0.50)
    cause_wt = SEVERITY_WEIGHTS.get(cause_sev_str.upper(), 0.50)
    strength_wt = rule.relationship_strength

    composite_impact = (0.50 * effect_wt) + (0.25 * cause_wt) + (0.25 * strength_wt)
    return round(max(0.10, min(1.00, composite_impact)), 4)
