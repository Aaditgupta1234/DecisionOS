"""Constants, threshold tiers, and penalty mappings for Business Health and Intelligence Layer."""

from typing import Dict
from app.core.constants import BusinessHealthStatus, FindingSeverity

# Health Score Threshold Tiers (0 - 100)
HEALTH_EXCELLENT_THRESHOLD = 90
HEALTH_HEALTHY_THRESHOLD = 75
HEALTH_WATCH_LIST_THRESHOLD = 60
HEALTH_AT_RISK_THRESHOLD = 40

# Diagnostic Finding Severity Deductions
FINDING_SEVERITY_PENALTIES: Dict[str, int] = {
    FindingSeverity.CRITICAL.value: 18,
    FindingSeverity.HIGH.value: 10,
    FindingSeverity.MEDIUM.value: 5,
    FindingSeverity.LOW.value: 2,
}

# Catastrophic Finding & Systemic Failure Modifiers
CATASTROPHIC_EXTRA_PENALTY = 6
SYSTEMIC_FAILURE_THRESHOLD = 3
SYSTEMIC_FAILURE_PENALTY = 10

# Root Cause Impact Deductions
RCA_HIGH_IMPACT_THRESHOLD = 0.80
RCA_HIGH_IMPACT_PENALTY = 8

RCA_MODERATE_IMPACT_THRESHOLD = 0.60
RCA_MODERATE_IMPACT_PENALTY = 4

# Maximum Total Penalty Cap for Category Groups
MAX_FINDING_PENALTY = 70
MAX_RCA_PENALTY = 25

# Quick-Win Recovery Bonus (for high-impact, low/medium-effort recommendations)
RECOMMENDATION_RECOVERY_BONUS_PER_ITEM = 2
MAX_RECOMMENDATION_RECOVERY_BONUS = 6

# Canonical Report Version
CANONICAL_REPORT_VERSION = "1.0"


def health_score_to_status(score: int) -> BusinessHealthStatus:
    """Maps integer health score [0 - 100] to BusinessHealthStatus enum."""
    if score >= HEALTH_EXCELLENT_THRESHOLD:
        return BusinessHealthStatus.EXCELLENT
    elif score >= HEALTH_HEALTHY_THRESHOLD:
        return BusinessHealthStatus.HEALTHY
    elif score >= HEALTH_WATCH_LIST_THRESHOLD:
        return BusinessHealthStatus.WATCH_LIST
    elif score >= HEALTH_AT_RISK_THRESHOLD:
        return BusinessHealthStatus.AT_RISK
    return BusinessHealthStatus.CRITICAL
