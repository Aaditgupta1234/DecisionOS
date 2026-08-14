"""Priority scoring engine for business recommendations."""

from typing import Optional, Tuple

from app.core.constants import FindingSeverity, RecommendationPriority
from app.models.diagnostic_finding import DiagnosticFinding
from app.recommendations.constants import (
    PRIORITY_CRITICAL_THRESHOLD,
    PRIORITY_HIGH_THRESHOLD,
    PRIORITY_MEDIUM_THRESHOLD,
    SEVERITY_WEIGHTS,
    priority_score_to_enum,
)


class PriorityEngine:
    """
    Computes deterministic priority score and assigns discrete RecommendationPriority tiers.
    
    Formula:
        Score = (Impact * 0.40) + (Confidence * 0.30) + ((1.0 - Effort) * 0.20) + (Severity_Weight * 0.10)
    
    Principles:
        - Rewards high business impact and high statistical confidence.
        - Provides a "quick-win boost" via (1.0 - Effort), elevating lower-effort, high-impact strategies.
        - Accounts for finding severity in business prioritization.
    """

    @classmethod
    def evaluate_priority(
        cls,
        impact_score: float,
        confidence_score: float,
        effort_score: float,
        finding: Optional[DiagnosticFinding] = None,
        severity_override: Optional[FindingSeverity | str] = None,
    ) -> Tuple[RecommendationPriority, float]:
        """
        Calculates priority score and returns (RecommendationPriority enum, numeric composite score).
        """
        # Determine finding severity weight
        if severity_override is not None:
            sev_str = severity_override.value if hasattr(severity_override, "value") else str(severity_override)
        elif finding is not None:
            sev_str = finding.severity.value if hasattr(finding.severity, "value") else str(finding.severity)
        else:
            sev_str = "HIGH"

        sev_wt = SEVERITY_WEIGHTS.get(sev_str.upper(), 0.80)

        # Compute composite score
        score = (
            (0.40 * impact_score)
            + (0.30 * confidence_score)
            + (0.20 * (1.0 - effort_score))
            + (0.10 * sev_wt)
        )
        score = round(max(0.0, min(1.0, score)), 4)

        priority_enum = priority_score_to_enum(score)
        return priority_enum, score
