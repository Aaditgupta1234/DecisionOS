"""Domain Constants and Enums for Phase 11.3: Executive Portfolio Intelligence & Strategic Decision Center."""

from enum import Enum
from typing import Literal

EXECUTIVE_INTELLIGENCE_VERSION = "1.0"

# Trend Confidence Levels
TrendConfidence = Literal["LOW", "MEDIUM", "HIGH"]
CONFIDENCE_LOW_THRESHOLD = 3      # <= 3 points -> LOW
CONFIDENCE_MEDIUM_THRESHOLD = 9   # 4-9 points -> MEDIUM, 10+ -> HIGH

# Risk Concentration Thresholds (%)
LOW_RISK_THRESHOLD: float = 0.0
MODERATE_RISK_THRESHOLD: float = 5.0
HIGH_RISK_THRESHOLD: float = 15.0
CRITICAL_RISK_THRESHOLD: float = 25.0

RISK_CONCENTRATION_CRITICAL_PCT: float = CRITICAL_RISK_THRESHOLD
RISK_CONCENTRATION_HIGH_PCT: float = HIGH_RISK_THRESHOLD
RISK_CONCENTRATION_MODERATE_PCT: float = MODERATE_RISK_THRESHOLD

# Intervention Score Thresholds
P1_THRESHOLD: float = 60.0   # < 60.0 -> P1 Immediate Attention
P2_THRESHOLD: float = 70.0   # 60.0-69.9 -> P2 High Attention
P3_THRESHOLD: float = 80.0   # 70.0-79.9 -> P3 Monitor
P4_THRESHOLD: float = 80.0   # >= 80.0 -> P4 Healthy

INTERVENTION_P1_SCORE_THRESHOLD: float = P1_THRESHOLD
INTERVENTION_P2_SCORE_THRESHOLD: float = P2_THRESHOLD
INTERVENTION_P3_SCORE_THRESHOLD: float = P3_THRESHOLD

# Intervention Score Delta Degradation Thresholds
INTERVENTION_P1_DELTA_THRESHOLD: float = -10.0  # Dropped >= 10 points -> P1
INTERVENTION_P2_DELTA_THRESHOLD: float = -5.0   # Dropped >= 5 points -> P2
INTERVENTION_P3_DELTA_THRESHOLD: float = -2.0   # Dropped >= 2 points -> P3


class ExecutiveInsightType(str, Enum):
    """Categorization of strategic executive insights."""
    PORTFOLIO_STRENGTH = "PORTFOLIO_STRENGTH"
    PORTFOLIO_RISK = "PORTFOLIO_RISK"
    PERFORMANCE_CONCENTRATION = "PERFORMANCE_CONCENTRATION"
    COHORT_MOBILITY = "COHORT_MOBILITY"
    MOMENTUM = "MOMENTUM"
    INTERVENTION_PRIORITY = "INTERVENTION_PRIORITY"


class RiskLevel(str, Enum):
    """Overall portfolio or business unit operational/financial risk level."""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MODERATE = "MODERATE"
    LOW = "LOW"


class PriorityLevel(str, Enum):
    """Action priority level for leadership intervention."""
    P1 = "P1"  # Immediate Attention (< 60.0 or severe degradation)
    P2 = "P2"  # High Attention (60.0-69.9 or moderate degradation)
    P3 = "P3"  # Monitor (70.0-79.9 or mild degradation)
    P4 = "P4"  # Healthy (>= 80.0 and stable/improving)
