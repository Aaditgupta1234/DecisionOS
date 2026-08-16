"""Domain Constants and Enums for Phase 11.5: Strategic Recommendation & Portfolio Optimization Engine."""

from enum import Enum
from typing import Dict

RECOMMENDATION_VERSION = "1.0"
RECOMMENDATION_SCHEMA_VERSION = "1.0"

DEFAULT_RECOMMENDATIONS_LIMIT: int = 25
MAX_RECOMMENDATIONS_LIMIT: int = 100

# Centralized Opportunity & Recommendation Trigger Thresholds
CRITICAL_HEALTH_THRESHOLD: float = 60.0       # Health score < 60.0 -> Critical opportunity
AT_RISK_THRESHOLD: float = 70.0               # Health score < 70.0 -> Underperforming opportunity
EXECUTIVE_ESCALATION_THRESHOLD: float = 60.0   # Score < 60.0 + critical findings -> Escalation
TREND_REVERSAL_THRESHOLD: float = -5.0        # Score drop <= -5.0 -> Trend reversal
PROMOTION_MIN_SCORE: float = 75.0             # Score >= 75.0 & <= 89.9 -> Cusp promotion candidate
PROMOTION_MAX_SCORE: float = 89.9
ELITE_SCORE_THRESHOLD: float = 90.0           # Score >= 90.0 -> Best practice anchor
REBALANCING_SPREAD_THRESHOLD: float = 30.0    # Top-to-bottom performance spread >= 30.0 -> Rebalance

# Optimization Score Categorization Thresholds
OPTIMIZATION_SCORE_HIGH: float = 10.0
OPTIMIZATION_SCORE_MEDIUM: float = 5.0

# Impact Level Evaluation Thresholds
IMPACT_TRANSFORMATIONAL_THRESHOLD: float = 15.0  # Expected impact >= 15.0 -> TRANSFORMATIONAL
IMPACT_HIGH_THRESHOLD: float = 8.0               # Expected impact >= 8.0 -> HIGH
IMPACT_MEDIUM_THRESHOLD: float = 3.0             # Expected impact >= 3.0 -> MEDIUM


class RecommendationType(str, Enum):
    """Categorization of strategic executive recommendations."""
    RISK_REDUCTION = "RISK_REDUCTION"
    PERFORMANCE_ACCELERATION = "PERFORMANCE_ACCELERATION"
    COHORT_PROMOTION = "COHORT_PROMOTION"
    EXECUTIVE_ESCALATION = "EXECUTIVE_ESCALATION"
    BEST_PRACTICE_REPLICATION = "BEST_PRACTICE_REPLICATION"
    TREND_REVERSAL = "TREND_REVERSAL"
    PORTFOLIO_REBALANCING = "PORTFOLIO_REBALANCING"


class RecommendationPriority(str, Enum):
    """Execution priority horizon for leadership actions."""
    CRITICAL = "CRITICAL"  # Immediate Actions (Weight = 4)
    HIGH = "HIGH"          # Near-Term Actions (Weight = 3)
    MEDIUM = "MEDIUM"      # Strategic Actions (Weight = 2)
    LOW = "LOW"            # Continuous Improvement (Weight = 1)


class RecommendationImpactLevel(str, Enum):
    """Expected magnitude of health improvement or risk reduction."""
    TRANSFORMATIONAL = "TRANSFORMATIONAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class ConfidenceLevel(str, Enum):
    """Confidence in recommendation grounding and historical sufficiency."""
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class ImplementationEffort(str, Enum):
    """Estimated managerial and operational difficulty of recommendation execution."""
    LOW = "LOW"        # Effort Weight = 1.0
    MEDIUM = "MEDIUM"  # Effort Weight = 2.0
    HIGH = "HIGH"      # Effort Weight = 3.0


EFFORT_WEIGHTS: Dict[ImplementationEffort, float] = {
    ImplementationEffort.LOW: 1.0,
    ImplementationEffort.MEDIUM: 2.0,
    ImplementationEffort.HIGH: 3.0,
}

PRIORITY_WEIGHTS: Dict[RecommendationPriority, int] = {
    RecommendationPriority.CRITICAL: 4,
    RecommendationPriority.HIGH: 3,
    RecommendationPriority.MEDIUM: 2,
    RecommendationPriority.LOW: 1,
}
