"""Constants, default scoring weights, and strength mapping for Root Cause Analysis."""

from app.core.constants import RelationshipStrength, RelationshipType

# Numeric weight mapping for qualitative relationship strengths
STRENGTH_WEIGHT_MAP = {
    RelationshipStrength.VERY_WEAK: 0.2,
    RelationshipStrength.WEAK: 0.4,
    RelationshipStrength.MODERATE: 0.6,
    RelationshipStrength.STRONG: 0.8,
    RelationshipStrength.VERY_STRONG: 1.0,
}

# Reverse mapping from float to nearest discrete RelationshipStrength enum
def numeric_to_relationship_strength(val: float) -> RelationshipStrength:
    """Maps a float score [0.0 - 1.0] to the nearest discrete RelationshipStrength enum."""
    if val >= 0.90:
        return RelationshipStrength.VERY_STRONG
    if val >= 0.70:
        return RelationshipStrength.STRONG
    if val >= 0.50:
        return RelationshipStrength.MODERATE
    if val >= 0.30:
        return RelationshipStrength.WEAK
    return RelationshipStrength.VERY_WEAK


# Severity weights for impact calculations
SEVERITY_WEIGHTS = {
    "CRITICAL": 1.00,
    "HIGH": 0.80,
    "MEDIUM": 0.50,
    "LOW": 0.20,
}

# Default correlation confidence adjustments
CORRELATION_SUPPORT_BONUS = 0.08      # Bonus when empirical data confirms the rule
CORRELATION_CONTRADICTION_PENALTY = 0.20  # Penalty when empirical data contradicts the rule
EVIDENCE_COUNT_BONUS_PER_ITEM = 0.02   # Additional small boost per supporting evidence point (max +0.06)
