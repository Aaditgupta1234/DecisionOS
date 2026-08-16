"""Domain Constants and Enums for Phase 11.6: Executive Decision Simulation & Strategic Roadmap Intelligence."""

from enum import Enum
from typing import Dict

ROADMAP_ENGINE_VERSION = "1.0"
ROADMAP_SCHEMA_VERSION = "1.0"
ROADMAP_VERSION = "1.0"
DECISION_ENGINE_VERSION = "1.0"
DECISION_PACKAGE_VERSION = "1.0"

# Quarterly Horizon Capacity Limits (Effort Weight Points)
SHORT_TERM_CAPACITY: float = 10.0     # Q1 Capacity
MEDIUM_TERM_CAPACITY: float = 8.0     # Q2 Capacity
LONG_TERM_CAPACITY: float = 6.0       # Q3 Capacity
OPTIMIZATION_CAPACITY: float = 5.0    # Q4 Capacity

HORIZON_EFFORT_CAPACITIES: Dict[str, float] = {
    "Q1": SHORT_TERM_CAPACITY,
    "Q2": MEDIUM_TERM_CAPACITY,
    "Q3": LONG_TERM_CAPACITY,
    "Q4": OPTIMIZATION_CAPACITY,
}

# Confidence Evaluation Bounds based on Affected Workspace Count
CONFIDENCE_LOW_WORKSPACES: int = 3    # < 3 -> LOW
CONFIDENCE_HIGH_WORKSPACES: int = 10  # >= 10 -> HIGH, else MEDIUM


class InitiativeHorizon(str, Enum):
    """Quarterly execution sequencing horizon for strategic initiatives."""
    Q1 = "Q1"
    Q2 = "Q2"
    Q3 = "Q3"
    Q4 = "Q4"


class InitiativeCategory(str, Enum):
    """Strategic classification of bundled executive programs."""
    RISK_REMEDIATION = "RISK_REMEDIATION"
    PERFORMANCE_GROWTH = "PERFORMANCE_GROWTH"
    CAPABILITY_EXPANSION = "CAPABILITY_EXPANSION"
    GOVERNANCE_ESCALATION = "GOVERNANCE_ESCALATION"
    PORTFOLIO_BALANCING = "PORTFOLIO_BALANCING"


class DecisionPackageType(str, Enum):
    """Categorization of simulated decision packages."""
    RISK_REDUCTION_ONLY = "RISK_REDUCTION_ONLY"      # Option A
    TURNAROUND_ACCELERATION = "TURNAROUND_ACCELERATION"  # Option B
    FULL_TRANSFORMATION = "FULL_TRANSFORMATION"      # Option C
    CUSTOM = "CUSTOM"                                # User Selected
