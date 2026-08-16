"""Domain Constants and Enums for Phase 11.4: Executive Scenario Modeling & Strategic Planning Intelligence."""

from enum import Enum

SCENARIO_ENGINE_VERSION = "1.0"
SCENARIO_SCHEMA_VERSION = "1.0"

# Operational Bounds and Limits
MAX_SCENARIOS_PER_COMPARISON: int = 10
MAX_ADJUSTMENT_VALUE: float = 100.0
MIN_ADJUSTMENT_VALUE: float = -100.0

# Coverage Confidence Thresholds (%)
COVERAGE_CONFIDENCE_LOW_PCT: float = 25.0    # < 25% -> LOW
COVERAGE_CONFIDENCE_HIGH_PCT: float = 75.0   # > 75% -> HIGH, else MEDIUM

# Impact Level Evaluation Thresholds
IMPACT_CRITICAL_HEALTH_DELTA: float = 15.0      # Abs delta >= 15.0 -> CRITICAL
IMPACT_HIGH_HEALTH_DELTA: float = 8.0          # Abs delta >= 8.0 -> HIGH
IMPACT_MODERATE_HEALTH_DELTA: float = 3.0      # Abs delta >= 3.0 -> MODERATE

IMPACT_CRITICAL_RISK_DELTA_PCT: float = 20.0   # Risk concentration delta >= 20.0% -> CRITICAL
IMPACT_HIGH_RISK_DELTA_PCT: float = 10.0       # Risk concentration delta >= 10.0% -> HIGH
IMPACT_MODERATE_RISK_DELTA_PCT: float = 5.0    # Risk concentration delta >= 5.0% -> MODERATE


class ScenarioType(str, Enum):
    """Categorization of strategic scenario modeling templates and custom runs."""
    HEALTH_IMPROVEMENT = "HEALTH_IMPROVEMENT"
    HEALTH_DECLINE = "HEALTH_DECLINE"
    RISK_REDUCTION = "RISK_REDUCTION"
    COHORT_PROMOTION = "COHORT_PROMOTION"
    COHORT_DEGRADATION = "COHORT_DEGRADATION"
    CUSTOM = "CUSTOM"


class ScenarioImpactLevel(str, Enum):
    """Magnitude of portfolio health or risk concentration shift caused by the scenario."""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MODERATE = "MODERATE"
    LOW = "LOW"


class ScenarioResultStatus(str, Enum):
    """Directional polarity of projected portfolio outcome."""
    POSITIVE = "POSITIVE"
    NEGATIVE = "NEGATIVE"
    NEUTRAL = "NEUTRAL"
