"""Domain Constants and Enums for Phase 12: Strategic Execution Layer."""

from enum import Enum
from typing import Dict, List

EXECUTION_ENGINE_VERSION = "1.0"
EXECUTION_SCHEMA_VERSION = "1.0"
EXECUTION_SNAPSHOT_VERSION = "1.0"
PROGRAM_ROLLUP_VERSION = "1.0"
EXECUTION_HEALTH_SCORE_VERSION = "1.0"
EXECUTION_RISK_ENGINE_VERSION = "1.0"
OUTCOME_ENGINE_VERSION = "1.0"
LINEAGE_GRAPH_VERSION = "1.0"


class ProgramTemplateCode(str, Enum):
    """Pre-configured strategic program template codes."""
    OPERATIONAL_TURNAROUND = "OPERATIONAL_TURNAROUND"
    CRITICAL_RISK_REMEDIATION = "CRITICAL_RISK_REMEDIATION"
    GROWTH_EXPANSION = "GROWTH_EXPANSION"
    COST_OPTIMIZATION = "COST_OPTIMIZATION"
    PLAYBOOK_STANDARDIZATION = "PLAYBOOK_STANDARDIZATION"
    CUSTOM = "CUSTOM"


class ProgramStatus(str, Enum):
    """Lifecycle status of a multi-initiative strategic program."""
    PLANNED = "PLANNED"
    ACTIVE = "ACTIVE"
    ON_TRACK = "ON_TRACK"
    AT_RISK = "AT_RISK"
    COMPLETED = "COMPLETED"
    ARCHIVED = "ARCHIVED"


class InitiativeStatus(str, Enum):
    """Lifecycle status of an individual strategic initiative."""
    PLANNED = "PLANNED"
    ACTIVE = "ACTIVE"
    AT_RISK = "AT_RISK"
    BLOCKED = "BLOCKED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class InitiativePriority(str, Enum):
    """Strategic priority categorization for execution queue sorting."""
    P1 = "P1"  # Critical / Immediate Intervention
    P2 = "P2"  # High Priority
    P3 = "P3"  # Medium Priority
    P4 = "P4"  # Low / Steady State Monitoring


class ExecutionHealthGrade(str, Enum):
    """Execution Health Grade evaluating initiative delivery quality."""
    EXCELLENT = "EXCELLENT"  # 90.0 - 100.0
    GOOD = "GOOD"            # 80.0 - 89.9
    STABLE = "STABLE"        # 70.0 - 79.9
    AT_RISK = "AT_RISK"      # 60.0 - 69.9
    CRITICAL = "CRITICAL"    # < 60.0


class ExecutionRiskLevel(str, Enum):
    """Independent risk severity assessment for an initiative or program."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ExecutionBlocker(str, Enum):
    """Structured root-cause categorization for blocked initiatives."""
    RESOURCE_CONSTRAINT = "RESOURCE_CONSTRAINT"
    DEPENDENCY_DELAY = "DEPENDENCY_DELAY"
    GOVERNANCE_PENDING = "GOVERNANCE_PENDING"
    BUDGET_CONSTRAINT = "BUDGET_CONSTRAINT"
    DATA_UNAVAILABLE = "DATA_UNAVAILABLE"
    OTHER = "OTHER"


class DependencyType(str, Enum):
    """Directed dependency relationship between strategic initiatives."""
    BLOCKS = "BLOCKS"
    DEPENDS_ON = "DEPENDS_ON"
    ENABLES = "ENABLES"
    RELATES_TO = "RELATES_TO"


class MilestoneStatus(str, Enum):
    """Execution status for intermediate initiative milestones."""
    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    OVERDUE = "OVERDUE"
    CANCELLED = "CANCELLED"


class ExecutionEventType(str, Enum):
    """Operational event types recorded across the execution timeline."""
    STATUS_CHANGED = "STATUS_CHANGED"
    MILESTONE_STARTED = "MILESTONE_STARTED"
    MILESTONE_COMPLETED = "MILESTONE_COMPLETED"
    MILESTONE_DELAYED = "MILESTONE_DELAYED"
    RISK_ESCALATED = "RISK_ESCALATED"
    BLOCKER_RECORDED = "BLOCKER_RECORDED"
    BLOCKER_RESOLVED = "BLOCKER_RESOLVED"
    OWNER_CHANGED = "OWNER_CHANGED"
    BUDGET_UPDATED = "BUDGET_UPDATED"
    GOVERNANCE_REVIEW_COMPLETED = "GOVERNANCE_REVIEW_COMPLETED"
    OUTCOME_RECORDED = "OUTCOME_RECORDED"
    OUTCOME_TARGET_ACHIEVED = "OUTCOME_TARGET_ACHIEVED"
    OUTCOME_TARGET_MISSED = "OUTCOME_TARGET_MISSED"
    ADMIN_OVERRIDE = "ADMIN_OVERRIDE"


class GovernanceDecision(str, Enum):
    """Formal executive review decision classifications."""
    APPROVED = "APPROVED"
    CONDITIONALLY_APPROVED = "CONDITIONALLY_APPROVED"
    REQUIRES_REWORK = "REQUIRES_REWORK"
    REJECTED = "REJECTED"


class TargetDirection(str, Enum):
    """Directional target orientation for initiative target metrics."""
    INCREASE = "INCREASE"
    DECREASE = "DECREASE"
    MAINTAIN = "MAINTAIN"


class OutcomeMeasurementConfidence(str, Enum):
    """Confidence classification for post-execution outcome measurements."""
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


PROGRESS_ENGINE_VERSION = "1.0"
VELOCITY_ENGINE_VERSION = "1.0"
SCHEDULE_ENGINE_VERSION = "1.0"
BUDGET_ENGINE_VERSION = "1.0"
PORTFOLIO_EXECUTION_VERSION = "1.0"


class VelocityGrade(str, Enum):
    """Execution velocity grade evaluating pace of delivery."""
    EXCELLENT = "EXCELLENT"  # >= 85.0
    GOOD = "GOOD"            # 70.0 - 84.9
    STABLE = "STABLE"        # 50.0 - 69.9
    SLOW = "SLOW"            # 30.0 - 49.9
    CRITICAL = "CRITICAL"    # < 30.0


class ScheduleStatus(str, Enum):
    """Execution schedule adherence status based on planned vs actual variance."""
    AHEAD = "AHEAD"                  # variance >= +5%
    ON_TRACK = "ON_TRACK"            # variance -5% to +5%
    AT_RISK = "AT_RISK"              # variance -15% to -5%
    DELAYED = "DELAYED"              # variance -30% to -15%
    CRITICAL_DELAY = "CRITICAL_DELAY"# variance < -30%


class BudgetHealth(str, Enum):
    """Execution financial budget health status."""
    HEALTHY = "HEALTHY"      # Score >= 80, spend <= allocated
    WATCH = "WATCH"          # Score 60-79, spend 80-95%
    AT_RISK = "AT_RISK"      # Score 40-59, spend 95-105%
    OVER_BUDGET = "OVER_BUDGET" # Score < 40, spend > 105%


# Health Grade Thresholds
HEALTH_GRADE_EXCELLENT_MIN: float = 90.0
HEALTH_GRADE_GOOD_MIN: float = 80.0
HEALTH_GRADE_STABLE_MIN: float = 70.0
HEALTH_GRADE_AT_RISK_MIN: float = 60.0


def calculate_health_grade(health_score: float) -> ExecutionHealthGrade:
    """Deterministically maps an execution health score (0-100) to an ExecutionHealthGrade."""
    if health_score >= HEALTH_GRADE_EXCELLENT_MIN:
        return ExecutionHealthGrade.EXCELLENT
    if health_score >= HEALTH_GRADE_GOOD_MIN:
        return ExecutionHealthGrade.GOOD
    if health_score >= HEALTH_GRADE_STABLE_MIN:
        return ExecutionHealthGrade.STABLE
    if health_score >= HEALTH_GRADE_AT_RISK_MIN:
        return ExecutionHealthGrade.AT_RISK
    return ExecutionHealthGrade.CRITICAL


def calculate_velocity_grade(score: float) -> VelocityGrade:
    """Deterministically maps a velocity score (0-100) to a VelocityGrade."""
    if score >= 85.0:
        return VelocityGrade.EXCELLENT
    if score >= 70.0:
        return VelocityGrade.GOOD
    if score >= 50.0:
        return VelocityGrade.STABLE
    if score >= 30.0:
        return VelocityGrade.SLOW
    return VelocityGrade.CRITICAL


def calculate_schedule_status(variance: float) -> ScheduleStatus:
    """Deterministically maps schedule progress variance (%) to a ScheduleStatus."""
    if variance >= 5.0:
        return ScheduleStatus.AHEAD
    if variance >= -5.0:
        return ScheduleStatus.ON_TRACK
    if variance >= -15.0:
        return ScheduleStatus.AT_RISK
    if variance >= -30.0:
        return ScheduleStatus.DELAYED
    return ScheduleStatus.CRITICAL_DELAY


def calculate_budget_health(score: float, utilization_pct: float) -> BudgetHealth:
    """Deterministically maps budget score and utilization percentage to BudgetHealth."""
    if utilization_pct > 105.0 or score < 40.0:
        return BudgetHealth.OVER_BUDGET
    if utilization_pct >= 95.0 or score < 60.0:
        return BudgetHealth.AT_RISK
    if utilization_pct >= 80.0 or score < 80.0:
        return BudgetHealth.WATCH
    return BudgetHealth.HEALTHY
