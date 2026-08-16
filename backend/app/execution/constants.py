"""Domain Constants and Enums for Phase 12: Strategic Execution Layer."""

from enum import Enum
from typing import Dict, List, Optional

EXECUTION_ENGINE_VERSION = "1.0"
EXECUTION_SCHEMA_VERSION = "1.0"
EXECUTION_SNAPSHOT_VERSION = "1.0"
PROGRAM_ROLLUP_VERSION = "1.0"
EXECUTION_HEALTH_SCORE_VERSION = "1.0"
EXECUTION_RISK_ENGINE_VERSION = "1.0"
OUTCOME_ENGINE_VERSION = "1.0"
BENEFITS_ENGINE_VERSION = "1.0"
REALIZATION_ENGINE_VERSION = "1.0"
ROI_ENGINE_VERSION = "1.0"
ALIGNMENT_ENGINE_VERSION = "1.0"
OUTCOME_SNAPSHOT_METRIC_VERSION = "1.0"
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
    REVIEW_SCHEDULED = "REVIEW_SCHEDULED"
    REVIEW_STARTED = "REVIEW_STARTED"
    REVIEW_COMPLETED = "REVIEW_COMPLETED"
    REVIEW_CANCELLED = "REVIEW_CANCELLED"
    ACTION_CREATED = "ACTION_CREATED"
    ACTION_ASSIGNED = "ACTION_ASSIGNED"
    ACTION_COMPLETED = "ACTION_COMPLETED"
    ACTION_OVERDUE = "ACTION_OVERDUE"
    ESCALATION_TRIGGERED = "ESCALATION_TRIGGERED"
    ESCALATION_RESOLVED = "ESCALATION_RESOLVED"
    OUTCOME_RECORDED = "OUTCOME_RECORDED"
    OUTCOME_CREATED = "OUTCOME_CREATED"
    OUTCOME_UPDATED = "OUTCOME_UPDATED"
    OUTCOME_ACHIEVED = "OUTCOME_ACHIEVED"
    OUTCOME_PARTIALLY_ACHIEVED = "OUTCOME_PARTIALLY_ACHIEVED"
    OUTCOME_MISSED = "OUTCOME_MISSED"
    OUTCOME_TARGET_ACHIEVED = "OUTCOME_TARGET_ACHIEVED"
    OUTCOME_TARGET_MISSED = "OUTCOME_TARGET_MISSED"
    BENEFIT_REALIZED = "BENEFIT_REALIZED"
    ROI_RECALCULATED = "ROI_RECALCULATED"
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
    APPROVED_WITH_CONDITIONS = "APPROVED_WITH_CONDITIONS"
    DEFERRED = "DEFERRED"
    REJECTED = "REJECTED"
    ESCALATED = "ESCALATED"
    CONDITIONALLY_APPROVED = "CONDITIONALLY_APPROVED"  # Compatibility alias
    REQUIRES_REWORK = "REQUIRES_REWORK"  # Compatibility alias


class GovernanceDecisionOutcome(str, Enum):
    """Normalized 3-tier governance decision outcome classification."""
    POSITIVE = "POSITIVE"
    NEUTRAL = "NEUTRAL"
    NEGATIVE = "NEGATIVE"


class GovernanceReviewStatus(str, Enum):
    """Lifecycle status for formal governance reviews."""
    SCHEDULED = "SCHEDULED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class EscalationLevel(str, Enum):
    """Formal escalation tiers for execution risks and blockers."""
    NONE = "NONE"
    LEVEL_1 = "LEVEL_1"      # Operational Lead / Manager
    LEVEL_2 = "LEVEL_2"      # Program Director / Delivery Head
    EXECUTIVE = "EXECUTIVE"  # Executive Steering Committee / Board


class ReviewReadinessLevel(str, Enum):
    """Readiness classification evaluating preparedness for governance review."""
    READY = "READY"                              # Score >= 80.0
    REVIEW_REQUIRED = "REVIEW_REQUIRED"          # Score 60.0 - 79.9
    ESCALATION_REQUIRED = "ESCALATION_REQUIRED"  # Score 40.0 - 59.9
    EXECUTIVE_ATTENTION = "EXECUTIVE_ATTENTION"  # Score < 40.0


class GovernanceTrend(str, Enum):
    """Longitudinal trajectory of governance compliance and readiness."""
    IMPROVING = "IMPROVING"
    STABLE = "STABLE"
    DETERIORATING = "DETERIORATING"


class ReviewType(str, Enum):
    """Categories of governance and executive reviews."""
    GOVERNANCE_REVIEW = "GOVERNANCE_REVIEW"
    RISK_REVIEW = "RISK_REVIEW"
    MILESTONE_REVIEW = "MILESTONE_REVIEW"
    EXECUTIVE_REVIEW = "EXECUTIVE_REVIEW"
    PROGRAM_REVIEW = "PROGRAM_REVIEW"


class GovernanceStatus(str, Enum):
    """Executive governance operational posture classification."""
    HEALTHY = "HEALTHY"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    ESCALATION_REQUIRED = "ESCALATION_REQUIRED"
    EXECUTIVE_ATTENTION = "EXECUTIVE_ATTENTION"


class ActionPriority(str, Enum):
    """Priority urgency classification for governance review actions."""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class GovernanceActionStatus(str, Enum):
    """Operational lifecycle status of governance remediation actions."""
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    OVERDUE = "OVERDUE"
    CANCELLED = "CANCELLED"


class GovernanceMaturityLevel(str, Enum):
    """Overall organizational governance maturity level."""
    OPTIMIZED = "OPTIMIZED"    # Composite maturity score >= 90.0
    MANAGED = "MANAGED"        # Composite maturity score 75.0 - 89.9
    DEVELOPING = "DEVELOPING"  # Composite maturity score 60.0 - 74.9
    AD_HOC = "AD_HOC"          # Composite maturity score < 60.0


GOVERNANCE_ENGINE_VERSION = "1.0"
REVIEW_ENGINE_VERSION = "1.0"
ACTION_ENGINE_VERSION = "1.0"
COMPLIANCE_ENGINE_VERSION = "1.0"
EFFECTIVENESS_ENGINE_VERSION = "1.0"
MATURITY_ENGINE_VERSION = "1.0"


class TargetDirection(str, Enum):
    """Directional target orientation for initiative target metrics."""
    INCREASE = "INCREASE"
    DECREASE = "DECREASE"
    MAINTAIN = "MAINTAIN"


class OutcomeStatus(str, Enum):
    """Execution outcome realization status."""
    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    ACHIEVED = "ACHIEVED"
    PARTIALLY_ACHIEVED = "PARTIALLY_ACHIEVED"
    MISSED = "MISSED"


class OutcomeMetricType(str, Enum):
    """Categorical type classification for outcome metrics."""
    FINANCIAL = "FINANCIAL"
    OPERATIONAL = "OPERATIONAL"
    CUSTOMER = "CUSTOMER"
    PRODUCT = "PRODUCT"
    STRATEGIC = "STRATEGIC"


class OutcomeCriticality(str, Enum):
    """Strategic criticality rating for outcome measurements."""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class OutcomeHealth(str, Enum):
    """Synthesized health classification for an individual outcome."""
    HEALTHY = "HEALTHY"
    WATCH = "WATCH"
    AT_RISK = "AT_RISK"
    CRITICAL = "CRITICAL"


class PortfolioOutcomeHealthGrade(str, Enum):
    """Executive portfolio-wide outcome health grading."""
    HEALTHY = "HEALTHY"
    WATCH = "WATCH"
    AT_RISK = "AT_RISK"
    CRITICAL = "CRITICAL"


class OutcomeExecutionStatus(str, Enum):
    """Operational pace and schedule execution status for an outcome."""
    ON_TRACK = "ON_TRACK"
    AT_RISK = "AT_RISK"
    OFF_TRACK = "OFF_TRACK"
    COMPLETED = "COMPLETED"


class TargetDateStatus(str, Enum):
    """Calendar timeline status relative to the target achievement date."""
    ON_TIME = "ON_TIME"
    APPROACHING = "APPROACHING"
    OVERDUE = "OVERDUE"


class OutcomeConfidenceLevel(str, Enum):
    """Confidence classification for post-execution outcome measurements."""
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


# Backward compatibility alias
OutcomeMeasurementConfidence = OutcomeConfidenceLevel


class MeasurementStability(str, Enum):
    """Deterministic stability rating derived from measurement variance / volatility."""
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class MeasurementQuality(str, Enum):
    """Deterministic measurement quality rating derived from confidence, stability, and freshness."""
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class MeasurementRecency(str, Enum):
    """Data freshness category based on elapsed days since latest measurement."""
    CURRENT = "CURRENT"      # 0 - 30 days
    RECENT = "RECENT"        # 31 - 90 days
    STALE = "STALE"          # 91 - 180 days
    OUTDATED = "OUTDATED"    # > 180 days


class OutcomeValueClassification(str, Enum):
    """Strategic monetary value tier classification for delivered benefits."""
    TRANSFORMATIONAL = "TRANSFORMATIONAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class ConfidenceTrend(str, Enum):
    """Longitudinal trajectory of outcome/benefit confidence scores."""
    IMPROVING = "IMPROVING"
    STABLE = "STABLE"
    DECLINING = "DECLINING"


class MeasurementFrequency(str, Enum):
    """Cadence for tracking and sampling outcome metrics."""
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    QUARTERLY = "QUARTERLY"
    ANNUALLY = "ANNUALLY"
    AD_HOC = "AD_HOC"


class BenefitType(str, Enum):
    """Structured categories of strategic business benefits."""
    REVENUE_GROWTH = "REVENUE_GROWTH"
    COST_REDUCTION = "COST_REDUCTION"
    RISK_REDUCTION = "RISK_REDUCTION"
    PRODUCTIVITY_GAIN = "PRODUCTIVITY_GAIN"
    CUSTOMER_IMPROVEMENT = "CUSTOMER_IMPROVEMENT"
    OPERATIONAL_EFFICIENCY = "OPERATIONAL_EFFICIENCY"
    STRATEGIC_VALUE = "STRATEGIC_VALUE"


class BenefitRealizationStatus(str, Enum):
    """Executive categorical realization status for expected benefits."""
    EXCEEDED = "EXCEEDED"
    ACHIEVED = "ACHIEVED"
    PARTIAL = "PARTIAL"
    MISSED = "MISSED"


class BenefitConcentrationRisk(str, Enum):
    """Pareto concentration risk level assessing dependence on top 20% initiatives."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class BenefitTrend(str, Enum):
    """Longitudinal trajectory of realized benefit value delivery."""
    IMPROVING = "IMPROVING"
    STABLE = "STABLE"
    DECLINING = "DECLINING"


class ROITrend(str, Enum):
    """Longitudinal trajectory of financial return on investment."""
    IMPROVING = "IMPROVING"
    STABLE = "STABLE"
    DECLINING = "DECLINING"


class ROIClassification(str, Enum):
    """Categorical financial ROI tier classification."""
    EXCEPTIONAL = "EXCEPTIONAL"  # ROI >= 200%
    STRONG = "STRONG"            # ROI 100% - 199.9%
    ACCEPTABLE = "ACCEPTABLE"    # ROI 0% - 99.9%
    POOR = "POOR"                # ROI -50% - -0.1%
    NEGATIVE = "NEGATIVE"        # ROI < -50%


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


def calculate_review_readiness_level(readiness_score: float) -> ReviewReadinessLevel:
    """Deterministically maps a review readiness score (0-100) to a ReviewReadinessLevel."""
    if readiness_score >= 80.0:
        return ReviewReadinessLevel.READY
    if readiness_score >= 60.0:
        return ReviewReadinessLevel.REVIEW_REQUIRED
    if readiness_score >= 40.0:
        return ReviewReadinessLevel.ESCALATION_REQUIRED
    return ReviewReadinessLevel.EXECUTIVE_ATTENTION


def calculate_governance_decision_outcome(decision: Optional[GovernanceDecision]) -> Optional[GovernanceDecisionOutcome]:
    """Deterministically classifies a governance decision into POSITIVE, NEUTRAL, or NEGATIVE."""
    if not decision:
        return None
    if decision == GovernanceDecision.APPROVED:
        return GovernanceDecisionOutcome.POSITIVE
    if decision in (GovernanceDecision.APPROVED_WITH_CONDITIONS, GovernanceDecision.DEFERRED, GovernanceDecision.CONDITIONALLY_APPROVED):
        return GovernanceDecisionOutcome.NEUTRAL
    if decision in (GovernanceDecision.REJECTED, GovernanceDecision.ESCALATED, GovernanceDecision.REQUIRES_REWORK):
        return GovernanceDecisionOutcome.NEGATIVE
    return GovernanceDecisionOutcome.NEUTRAL


def calculate_governance_maturity_level(
    compliance_score: float,
    effectiveness_score: float,
    action_closure_rate: float,
    escalation_resolution_rate: float,
) -> GovernanceMaturityLevel:
    """Deterministically calculates organization governance maturity from 4 composite factors."""
    composite = (
        (0.35 * compliance_score)
        + (0.35 * effectiveness_score)
        + (0.15 * action_closure_rate)
        + (0.15 * escalation_resolution_rate)
    )
    if composite >= 90.0:
        return GovernanceMaturityLevel.OPTIMIZED
    if composite >= 75.0:
        return GovernanceMaturityLevel.MANAGED
    if composite >= 60.0:
        return GovernanceMaturityLevel.DEVELOPING
    return GovernanceMaturityLevel.AD_HOC


def calculate_outcome_status(achievement_percentage: float) -> OutcomeStatus:
    """Deterministically maps achievement percentage to an OutcomeStatus."""
    if achievement_percentage >= 100.0:
        return OutcomeStatus.ACHIEVED
    if achievement_percentage >= 70.0:
        return OutcomeStatus.PARTIALLY_ACHIEVED
    if achievement_percentage > 0.0:
        return OutcomeStatus.MISSED
    return OutcomeStatus.NOT_STARTED


def calculate_outcome_confidence_level(score: float) -> OutcomeConfidenceLevel:
    """Deterministically maps confidence score (0-100) to OutcomeConfidenceLevel."""
    if score >= 80.0:
        return OutcomeConfidenceLevel.HIGH
    if score >= 60.0:
        return OutcomeConfidenceLevel.MEDIUM
    return OutcomeConfidenceLevel.LOW


def calculate_measurement_stability(stability_score: float) -> MeasurementStability:
    """Deterministically maps measurement stability score (0-100) to MeasurementStability."""
    if stability_score >= 80.0:
        return MeasurementStability.HIGH
    if stability_score >= 60.0:
        return MeasurementStability.MEDIUM
    return MeasurementStability.LOW


def calculate_measurement_recency(age_days: Optional[int]) -> MeasurementRecency:
    """Deterministically maps elapsed age in days to a MeasurementRecency classification."""
    if age_days is None or age_days <= 30:
        return MeasurementRecency.CURRENT
    if age_days <= 90:
        return MeasurementRecency.RECENT
    if age_days <= 180:
        return MeasurementRecency.STALE
    return MeasurementRecency.OUTDATED


def calculate_target_date_status(days_until_target: Optional[int], is_achieved: bool = False) -> TargetDateStatus:
    """Deterministically maps calendar days remaining until target achievement date."""
    if is_achieved:
        return TargetDateStatus.ON_TIME
    if days_until_target is None:
        return TargetDateStatus.ON_TIME
    if days_until_target < 0:
        return TargetDateStatus.OVERDUE
    if days_until_target <= 30:
        return TargetDateStatus.APPROACHING
    return TargetDateStatus.ON_TIME


def calculate_measurement_quality(
    confidence_score: float,
    stability_score: float,
    age_days: Optional[int] = None,
) -> MeasurementQuality:
    """Deterministically evaluates measurement quality from confidence, stability, and recency."""
    effective_age = age_days if age_days is not None else 0
    recency_factor = max(0.0, 100.0 - (effective_age * 1.5))
    quality_score = (0.45 * confidence_score) + (0.35 * stability_score) + (0.20 * recency_factor)
    if quality_score >= 80.0:
        return MeasurementQuality.HIGH
    if quality_score >= 60.0:
        return MeasurementQuality.MEDIUM
    return MeasurementQuality.LOW


def calculate_measurement_reliability_score(
    quality_score: float,
    stability_score: float,
    confidence_score: float,
) -> float:
    """Deterministically synthesizes a single executive measurement reliability score (0-100)."""
    score = (0.40 * quality_score) + (0.35 * stability_score) + (0.25 * confidence_score)
    return round(max(0.0, min(100.0, score)), 2)


def calculate_outcome_data_reliability_score(
    confidence_score: float,
    stability_score: float,
    quality_score: float,
    completeness_score: float,
) -> float:
    """Synthesizes comprehensive outcome data reliability from 4 core metadata dimensions."""
    score = (
        (0.35 * confidence_score)
        + (0.25 * stability_score)
        + (0.25 * quality_score)
        + (0.15 * completeness_score)
    )
    return round(max(0.0, min(100.0, score)), 2)


def calculate_outcome_predictability_score(
    stability_score: float,
    quality_score: float,
    confidence_score: float,
    age_days: Optional[int] = None,
) -> float:
    """Deterministically calculates outcome predictability score (0-100) without forecasting."""
    effective_age = age_days if age_days is not None else 0
    recency_factor = max(0.0, 100.0 - (effective_age * 1.5))
    score = (
        (0.35 * stability_score)
        + (0.30 * quality_score)
        + (0.20 * confidence_score)
        + (0.15 * recency_factor)
    )
    return round(max(0.0, min(100.0, score)), 2)


def calculate_outcome_health(
    achievement_pct: float,
    confidence_score: float,
    stability_score: float,
    age_days: Optional[int] = None,
) -> OutcomeHealth:
    """Deterministically derives outcome health classification from achievement, confidence, stability, and freshness."""
    effective_age = age_days if age_days is not None else 0
    recency_factor = max(0.0, 100.0 - (effective_age * 1.5))
    bounded_achievement = min(100.0, max(0.0, achievement_pct))
    score = (
        (0.40 * bounded_achievement)
        + (0.25 * confidence_score)
        + (0.20 * stability_score)
        + (0.15 * recency_factor)
    )
    if score >= 85.0:
        return OutcomeHealth.HEALTHY
    if score >= 70.0:
        return OutcomeHealth.WATCH
    if score >= 50.0:
        return OutcomeHealth.AT_RISK
    return OutcomeHealth.CRITICAL


def calculate_portfolio_outcome_health_grade(
    healthy: int,
    watch: int,
    at_risk: int,
    critical: int,
) -> PortfolioOutcomeHealthGrade:
    """Deterministically calculates portfolio outcome health grade from weighted distribution."""
    total = healthy + watch + at_risk + critical
    if total == 0:
        return PortfolioOutcomeHealthGrade.HEALTHY
    score = (
        (healthy * 100.0)
        + (watch * 75.0)
        + (at_risk * 50.0)
        + (critical * 20.0)
    ) / total
    if score >= 85.0:
        return PortfolioOutcomeHealthGrade.HEALTHY
    if score >= 70.0:
        return PortfolioOutcomeHealthGrade.WATCH
    if score >= 50.0:
        return PortfolioOutcomeHealthGrade.AT_RISK
    return PortfolioOutcomeHealthGrade.CRITICAL


def calculate_outcome_execution_status(
    achievement_pct: float,
    outcome_health: OutcomeHealth,
    recency: MeasurementRecency,
    velocity: float,
) -> OutcomeExecutionStatus:
    """Deterministically synthesizes operational pace and execution status for an outcome."""
    if achievement_pct >= 100.0:
        return OutcomeExecutionStatus.COMPLETED
    if outcome_health == OutcomeHealth.HEALTHY and recency in (MeasurementRecency.CURRENT, MeasurementRecency.RECENT):
        return OutcomeExecutionStatus.ON_TRACK
    if outcome_health in (OutcomeHealth.HEALTHY, OutcomeHealth.WATCH) and achievement_pct >= 50.0:
        return OutcomeExecutionStatus.AT_RISK
    return OutcomeExecutionStatus.OFF_TRACK


def calculate_outcome_value_classification(
    realized_value: float,
    benefit_score: Optional[float] = None,
) -> OutcomeValueClassification:
    """Deterministically classifies monetary/strategic importance of delivered benefits."""
    if realized_value >= 1_000_000.0 or (benefit_score is not None and benefit_score >= 90.0):
        return OutcomeValueClassification.TRANSFORMATIONAL
    if realized_value >= 500_000.0 or (benefit_score is not None and benefit_score >= 75.0):
        return OutcomeValueClassification.HIGH
    if realized_value >= 100_000.0 or (benefit_score is not None and benefit_score >= 50.0):
        return OutcomeValueClassification.MEDIUM
    return OutcomeValueClassification.LOW


def calculate_benefit_realization_status(realization_percentage: float) -> BenefitRealizationStatus:
    """Deterministically maps realization percentage to BenefitRealizationStatus."""
    if realization_percentage >= 120.0:
        return BenefitRealizationStatus.EXCEEDED
    if realization_percentage >= 90.0:
        return BenefitRealizationStatus.ACHIEVED
    if realization_percentage >= 60.0:
        return BenefitRealizationStatus.PARTIAL
    return BenefitRealizationStatus.MISSED


def calculate_benefit_concentration_risk(top_20_concentration_pct: float) -> BenefitConcentrationRisk:
    """Deterministically classifies Pareto top-20% value concentration risk."""
    if top_20_concentration_pct < 40.0:
        return BenefitConcentrationRisk.LOW
    if top_20_concentration_pct < 60.0:
        return BenefitConcentrationRisk.MEDIUM
    if top_20_concentration_pct < 80.0:
        return BenefitConcentrationRisk.HIGH
    return BenefitConcentrationRisk.CRITICAL


def calculate_roi_classification(roi_percentage: float) -> ROIClassification:
    """Deterministically classifies ROI percentage into standard financial tiers."""
    if roi_percentage >= 200.0:
        return ROIClassification.EXCEPTIONAL
    if roi_percentage >= 100.0:
        return ROIClassification.STRONG
    if roi_percentage >= 0.0:
        return ROIClassification.ACCEPTABLE
    if roi_percentage >= -50.0:
        return ROIClassification.POOR
    return ROIClassification.NEGATIVE


def calculate_confidence_trend(
    current_val: float,
    previous_val: Optional[float] = None,
    threshold: float = 5.0,
) -> ConfidenceTrend:
    """Deterministically calculates confidence trend from historical delta."""
    if previous_val is None:
        return ConfidenceTrend.STABLE
    delta = current_val - previous_val
    if delta >= threshold:
        return ConfidenceTrend.IMPROVING
    if delta <= -threshold:
        return ConfidenceTrend.DECLINING
    return ConfidenceTrend.STABLE


def calculate_benefit_trend(
    current_val: float,
    previous_val: Optional[float] = None,
    threshold: float = 5.0,
) -> BenefitTrend:
    """Deterministically calculates benefit realization trend from historical delta."""
    if previous_val is None:
        return BenefitTrend.STABLE
    delta = current_val - previous_val
    if delta >= threshold:
        return BenefitTrend.IMPROVING
    if delta <= -threshold:
        return BenefitTrend.DECLINING
    return BenefitTrend.STABLE


def calculate_roi_trend(
    current_val: float,
    previous_val: Optional[float] = None,
    threshold: float = 5.0,
) -> ROITrend:
    """Deterministically calculates ROI trend from historical delta."""
    if previous_val is None:
        return ROITrend.STABLE
    delta = current_val - previous_val
    if delta >= threshold:
        return ROITrend.IMPROVING
    if delta <= -threshold:
        return ROITrend.DECLINING
    return ROITrend.STABLE


def calculate_governance_trend(
    current_val: float,
    previous_val: Optional[float] = None,
    threshold: float = 5.0,
) -> GovernanceTrend:
    """Deterministically calculates governance compliance trend from historical delta."""
    if previous_val is None:
        return GovernanceTrend.STABLE
    delta = current_val - previous_val
    if delta >= threshold:
        return GovernanceTrend.IMPROVING
    if delta <= -threshold:
        return GovernanceTrend.DETERIORATING
    return GovernanceTrend.STABLE


