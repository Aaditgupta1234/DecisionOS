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


TIMELINE_ENGINE_VERSION = "1.0"
CRITICAL_PATH_ENGINE_VERSION = "1.0"
MILESTONE_ENGINE_VERSION = "1.0"


class MilestoneType(str, Enum):
    """Categorical deliverable type for initiative milestones."""
    DELIVERABLE = "DELIVERABLE"  # Core technical/operational deliverable
    APPROVAL = "APPROVAL"        # Budget or stakeholder sign-off
    GOVERNANCE = "GOVERNANCE"    # Steering committee / compliance review
    OUTCOME = "OUTCOME"          # Target metric achievement validation
    CHECKPOINT = "CHECKPOINT"    # Mid-stage completion audit


class MilestoneCriticality(str, Enum):
    """Criticality level determining milestone impact on initiative critical path."""
    CRITICAL = "CRITICAL"  # On critical path / non-negotiable blocker
    HIGH = "HIGH"          # Major dependency
    MEDIUM = "MEDIUM"      # Standard deliverable
    LOW = "LOW"            # Non-blocking / administrative


class MilestoneDependencyType(str, Enum):
    """Dependency relationship type between sequential/concurrent milestones."""
    FINISH_TO_START = "FINISH_TO_START"  # Successor cannot start until predecessor finishes
    START_TO_START = "START_TO_START"    # Successor cannot start until predecessor starts
    FINISH_TO_FINISH = "FINISH_TO_FINISH"# Successor cannot finish until predecessor finishes
    START_TO_FINISH = "START_TO_FINISH"  # Successor cannot finish until predecessor starts


class MilestoneStatus(str, Enum):
    """Execution lifecycle status for initiative milestones."""
    PLANNED = "PLANNED"
    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    BLOCKED = "BLOCKED"
    COMPLETED = "COMPLETED"
    OVERDUE = "OVERDUE"
    CANCELLED = "CANCELLED"


class TimelineRiskLevel(str, Enum):
    """Risk tier evaluating likelihood and impact of timeline delays."""
    LOW = "LOW"          # Score < 30.0
    MEDIUM = "MEDIUM"    # 30.0 - 59.9
    HIGH = "HIGH"        # 60.0 - 79.9
    CRITICAL = "CRITICAL"# >= 80.0


class ExecutionEventType(str, Enum):
    """Operational event types recorded across the execution timeline."""
    STATUS_CHANGED = "STATUS_CHANGED"
    MILESTONE_CREATED = "MILESTONE_CREATED"
    MILESTONE_STARTED = "MILESTONE_STARTED"
    MILESTONE_COMPLETED = "MILESTONE_COMPLETED"
    MILESTONE_DELAYED = "MILESTONE_DELAYED"
    MILESTONE_BLOCKED = "MILESTONE_BLOCKED"
    MILESTONE_REOPENED = "MILESTONE_REOPENED"
    MILESTONE_REASSIGNED = "MILESTONE_REASSIGNED"
    MILESTONE_RESCHEDULED = "MILESTONE_RESCHEDULED"
    CRITICAL_PATH_CHANGED = "CRITICAL_PATH_CHANGED"
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


def calculate_timeline_risk_level(score: float) -> TimelineRiskLevel:
    """Deterministically maps a timeline risk score (0-100) to a TimelineRiskLevel."""
    if score >= 80.0:
        return TimelineRiskLevel.CRITICAL
    if score >= 60.0:
        return TimelineRiskLevel.HIGH
    if score >= 30.0:
        return TimelineRiskLevel.MEDIUM
    return TimelineRiskLevel.LOW


PROGRESS_ENGINE_VERSION = "1.0"
VELOCITY_ENGINE_VERSION = "1.0"
SCHEDULE_ENGINE_VERSION = "1.0"


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


EXECUTION_HEALTH_ENGINE_VERSION = "1.0"
EXECUTION_RISK_ENGINE_VERSION = "1.0"
EARLY_WARNING_ENGINE_VERSION = "1.0"
INTERVENTION_ENGINE_VERSION = "1.0"
BUSINESS_IMPACT_ENGINE_VERSION = "1.0"
PORTFOLIO_RISK_ENGINE_VERSION = "1.0"


class ExecutionRiskSeverity(str, Enum):
    """Risk severity classification based on probability and impact of failure."""
    LOW = "LOW"          # Risk Score < 30.0
    MEDIUM = "MEDIUM"    # 30.0 - 59.9
    HIGH = "HIGH"        # 60.0 - 79.9
    CRITICAL = "CRITICAL"# >= 80.0


class PortfolioRiskGrade(str, Enum):
    """Executive portfolio-wide risk rating."""
    LOW = "LOW"          # Avg Risk < 30.0
    MODERATE = "MODERATE"# 30.0 - 59.9
    HIGH = "HIGH"        # 60.0 - 79.9
    CRITICAL = "CRITICAL"# >= 80.0


class HealthTrend(str, Enum):
    """Directional trend of initiative/program execution health."""
    IMPROVING = "IMPROVING"
    STABLE = "STABLE"
    DETERIORATING = "DETERIORATING"


class RiskTrend(str, Enum):
    """Directional trend of initiative/program execution risk."""
    IMPROVING = "IMPROVING"
    STABLE = "STABLE"
    DETERIORATING = "DETERIORATING"


class ExecutionRiskFactor(str, Enum):
    """Categorical risk factors driving execution vulnerability."""
    TIMELINE_DELAY = "TIMELINE_DELAY"
    CRITICAL_PATH_EXPOSURE = "CRITICAL_PATH_EXPOSURE"
    BLOCKED_MILESTONE = "BLOCKED_MILESTONE"
    DEPENDENCY_RISK = "DEPENDENCY_RISK"
    VELOCITY_DECLINE = "VELOCITY_DECLINE"
    BUDGET_OVERRUN = "BUDGET_OVERRUN"
    HEALTH_DETERIORATION = "HEALTH_DETERIORATION"


class WarningSeverity(str, Enum):
    """Severity tier for early warning alert signals."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class EarlyWarningType(str, Enum):
    """Proactive early warning triggers detecting delivery threats."""
    HEALTH_DETERIORATION = "HEALTH_DETERIORATION"
    TIMELINE_RISK = "TIMELINE_RISK"
    BUDGET_RISK = "BUDGET_RISK"
    VELOCITY_COLLAPSE = "VELOCITY_COLLAPSE"
    CRITICAL_BLOCKER = "CRITICAL_BLOCKER"
    CRITICAL_PATH_INSTABILITY = "CRITICAL_PATH_INSTABILITY"


class InterventionPriority(str, Enum):
    """Action priority tier for executive intervention."""
    P1 = "P1"  # Score >= 90.0 (Immediate Executive Action)
    P2 = "P2"  # Score 75.0 - 89.9 (Escalated Operational Triage)
    P3 = "P3"  # Score 50.0 - 74.9 (Routine Monitoring / Minor Adjustments)
    P4 = "P4"  # Score < 50.0 (Healthy / Low Urgency)


class InterventionCategory(str, Enum):
    """Functional remediation category for strategic interventions."""
    TIMELINE_RECOVERY = "TIMELINE_RECOVERY"
    BLOCKER_RESOLUTION = "BLOCKER_RESOLUTION"
    BUDGET_CORRECTION = "BUDGET_CORRECTION"
    GOVERNANCE_ESCALATION = "GOVERNANCE_ESCALATION"
    RESOURCE_REALLOCATION = "RESOURCE_REALLOCATION"
    EXECUTIVE_ATTENTION = "EXECUTIVE_ATTENTION"


def calculate_risk_severity(risk_score: float) -> ExecutionRiskSeverity:
    """Deterministically maps an execution risk score (0-100) to an ExecutionRiskSeverity."""
    if risk_score >= 80.0:
        return ExecutionRiskSeverity.CRITICAL
    if risk_score >= 60.0:
        return ExecutionRiskSeverity.HIGH
    if risk_score >= 30.0:
        return ExecutionRiskSeverity.MEDIUM
    return ExecutionRiskSeverity.LOW


def calculate_portfolio_risk_grade(avg_risk_score: float) -> PortfolioRiskGrade:
    """Deterministically maps an average portfolio risk score to a PortfolioRiskGrade."""
    if avg_risk_score >= 80.0:
        return PortfolioRiskGrade.CRITICAL
    if avg_risk_score >= 60.0:
        return PortfolioRiskGrade.HIGH
    if avg_risk_score >= 30.0:
        return PortfolioRiskGrade.MODERATE
    return PortfolioRiskGrade.LOW


def calculate_intervention_priority(priority_score: float) -> InterventionPriority:
    """Deterministically maps a priority urgency score (0-100) to an InterventionPriority tier."""
    if priority_score >= 90.0:
        return InterventionPriority.P1
    if priority_score >= 75.0:
        return InterventionPriority.P2
    if priority_score >= 50.0:
        return InterventionPriority.P3
    return InterventionPriority.P4


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
