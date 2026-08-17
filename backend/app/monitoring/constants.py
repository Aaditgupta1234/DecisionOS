"""Domain constants, enums, reason codes, and operational thresholds for Phase 13."""

import hashlib
import uuid
from datetime import date, datetime, timezone
from enum import Enum
from typing import Optional, Tuple

# Engine Versions
MONITORING_VERSION = "1.0"
ALERT_RULE_ENGINE_VERSION = "1.0"
OPERATIONAL_INTELLIGENCE_ENGINE_VERSION = "1.0"
EXECUTIVE_ESCALATION_ENGINE_VERSION = "1.0"
OPERATIONAL_HEALTH_ENGINE_VERSION = "1.0"
SNAPSHOT_LINEAGE_ENGINE_VERSION = "1.0"


# ==============================================================================
# 1. Enums
# ==============================================================================

class MonitoringSeverity(str, Enum):
    """Severity tier for Phase 13 enterprise operational alerts."""
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class MonitoringStatus(str, Enum):
    """Lifecycle state of an operational monitoring alert."""
    ACTIVE = "ACTIVE"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    RESOLVED = "RESOLVED"
    SUPPRESSED = "SUPPRESSED"


class MonitoringCategory(str, Enum):
    """Domain category for operational and strategic monitoring."""
    KPI = "KPI"
    RISK = "RISK"
    GOVERNANCE = "GOVERNANCE"
    BENEFITS = "BENEFITS"
    PORTFOLIO = "PORTFOLIO"
    EXECUTIVE = "EXECUTIVE"
    DATA_QUALITY = "DATA_QUALITY"
    SNAPSHOT = "SNAPSHOT"


class EscalationLevel(str, Enum):
    """Executive prioritization tier for actionable alerts and initiatives."""
    WATCH = "WATCH"
    ACTION_REQUIRED = "ACTION_REQUIRED"
    EXECUTIVE_REVIEW = "EXECUTIVE_REVIEW"
    EXECUTIVE_ESCALATION = "EXECUTIVE_ESCALATION"


class OperationalHealthGrade(str, Enum):
    """Overall deterministic operational health tier."""
    EXCELLENT = "EXCELLENT"
    GOOD = "GOOD"
    DEGRADED = "DEGRADED"
    CRITICAL = "CRITICAL"


class AlertConfidenceLevel(str, Enum):
    """Confidence tier for monitoring alert evidence."""
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class AlertSourceEntityType(str, Enum):
    """Source entity generating the monitoring alert."""
    INITIATIVE = "INITIATIVE"
    PROGRAM = "PROGRAM"
    DATASET = "DATASET"
    SNAPSHOT = "SNAPSHOT"
    GOVERNANCE_REVIEW = "GOVERNANCE_REVIEW"
    BENEFIT = "BENEFIT"
    SYSTEM = "SYSTEM"


# Phase 10.5 Backward Compatibility Enums
class SystemHealthStatus(str, Enum):
    """Overall health state of the DecisionOS platform."""
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    UNHEALTHY = "UNHEALTHY"


class ComponentStatus(str, Enum):
    """Health state of an individual platform subsystem."""
    UP = "UP"
    DEGRADED = "DEGRADED"
    DOWN = "DOWN"


class ComponentCategory(str, Enum):
    """Categorization of system components for UI grouping."""
    DATABASE = "DATABASE"
    OPERATIONAL = "OPERATIONAL"
    ANALYTICS = "ANALYTICS"
    INFRASTRUCTURE = "INFRASTRUCTURE"
    GOVERNANCE = "GOVERNANCE"


class AlertSeverity(str, Enum):
    """Legacy severity tier."""
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class AlertSource(str, Enum):
    """Originating subsystem for operational alerts."""
    DATABASE = "DATABASE"
    JOBS = "JOBS"
    SCHEDULES = "SCHEDULES"
    NOTIFICATIONS = "NOTIFICATIONS"
    AUDIT = "AUDIT"
    SYSTEM = "SYSTEM"
    REDIS = "REDIS"
    WORKERS = "WORKERS"
    QUEUE = "QUEUE"
    STORAGE = "STORAGE"


# ==============================================================================
# 2. Machine-Readable Reason Codes
# ==============================================================================

REASON_REVENUE_DROP_THRESHOLD_EXCEEDED = "REVENUE_DROP_THRESHOLD_EXCEEDED"
REASON_HEALTH_SCORE_DEGRADATION = "HEALTH_SCORE_DEGRADATION"
REASON_BENEFIT_REALIZATION_LAG = "BENEFIT_REALIZATION_LAG"
REASON_COMPLIANCE_FAILURE_DETECTED = "COMPLIANCE_FAILURE_DETECTED"
REASON_CRITICAL_BLOCKER_PRESENT = "CRITICAL_BLOCKER_PRESENT"
REASON_PORTFOLIO_IMBALANCE_DETECTED = "PORTFOLIO_IMBALANCE_DETECTED"
REASON_SPOF_CLUSTER_DETECTED = "SPOF_CLUSTER_DETECTED"
REASON_SNAPSHOT_RECENCY_BREACH = "SNAPSHOT_RECENCY_BREACH"
REASON_METRIC_COVERAGE_DEFICIT = "METRIC_COVERAGE_DEFICIT"
REASON_RISK_POSTURE_ESCALATION = "RISK_POSTURE_ESCALATION"
REASON_TIMELINE_SLIPPAGE_DETECTED = "TIMELINE_SLIPPAGE_DETECTED"


# ==============================================================================
# 3. Operational Health & Alert Weight Constants
# ==============================================================================

WEIGHT_HEALTH_ALERT = 0.25
WEIGHT_HEALTH_GOVERNANCE = 0.25
WEIGHT_HEALTH_RISK = 0.25
WEIGHT_HEALTH_DATA_QUALITY = 0.15
WEIGHT_HEALTH_PORTFOLIO = 0.10

ALERT_PENALTY_CRITICAL = 20.0
ALERT_PENALTY_HIGH = 10.0
ALERT_PENALTY_MEDIUM = 4.0
ALERT_PENALTY_LOW = 1.0

# Thresholds
DEFAULT_HEALTHY_SUCCESS_RATE = 95.0
DEFAULT_DEGRADED_SUCCESS_RATE = 80.0
CONSECUTIVE_FAILURE_WARNING_THRESHOLD = 3
CONSECUTIVE_FAILURE_CRITICAL_THRESHOLD = 5
DATABASE_HEALTH_TIMEOUT_SECONDS = 5.0
MONITORING_CACHE_TTL_SECONDS = 30
DEFAULT_LOOKBACK_HOURS = 24
MAX_LOOKBACK_HOURS = 168
MAX_ALERT_ITEMS = 50


# ==============================================================================
# 4. Deterministic Helper Functions
# ==============================================================================

def generate_alert_fingerprint(
    organization_id: uuid.UUID,
    rule_name: str,
    source_entity_type: Optional[str] = None,
    source_entity_id: Optional[uuid.UUID] = None,
) -> str:
    """Generates an immutable SHA-256 fingerprint for alert deduplication."""
    raw = f"{organization_id}:{rule_name}:{source_entity_type or 'SYSTEM'}:{source_entity_id or 'NONE'}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def calculate_alert_confidence(
    metric_coverage: float = 100.0,
    snapshot_completeness: float = 100.0,
    data_quality_score: float = 100.0,
) -> Tuple[float, AlertConfidenceLevel]:
    """Calculates deterministic alert confidence based on empirical data quality."""
    score = (
        0.50 * max(0.0, min(100.0, metric_coverage))
        + 0.30 * max(0.0, min(100.0, snapshot_completeness))
        + 0.20 * max(0.0, min(100.0, data_quality_score))
    )
    score = round(max(0.0, min(100.0, score)), 2)
    if score >= 80.0:
        level = AlertConfidenceLevel.HIGH
    elif score >= 60.0:
        level = AlertConfidenceLevel.MEDIUM
    else:
        level = AlertConfidenceLevel.LOW
    return score, level


def calculate_operational_health(
    active_critical_count: int,
    active_high_count: int,
    active_medium_count: int,
    active_low_count: int,
    governance_score: float = 80.0,
    average_risk_score: float = 20.0,
    metric_coverage: float = 90.0,
    snapshot_completeness: float = 90.0,
    portfolio_balance_score: float = 80.0,
) -> Tuple[float, OperationalHealthGrade, dict]:
    """Calculates composite deterministic operational health score (0-100) and factor breakdown."""
    # 1. Alert Score (100 minus penalty)
    alert_penalty = (
        active_critical_count * ALERT_PENALTY_CRITICAL
        + active_high_count * ALERT_PENALTY_HIGH
        + active_medium_count * ALERT_PENALTY_MEDIUM
        + active_low_count * ALERT_PENALTY_LOW
    )
    alert_score = max(0.0, min(100.0, 100.0 - alert_penalty))

    # 2. Gov Score
    gov_score = max(0.0, min(100.0, governance_score))

    # 3. Risk Posture (100 - avg risk)
    risk_posture = max(0.0, min(100.0, 100.0 - average_risk_score))

    # 4. Data Quality Score
    data_quality_score = max(0.0, min(100.0, (metric_coverage * 0.5) + (snapshot_completeness * 0.5)))

    # 5. Portfolio Balance Score
    port_score = max(0.0, min(100.0, portfolio_balance_score))

    # Composite
    composite = (
        WEIGHT_HEALTH_ALERT * alert_score
        + WEIGHT_HEALTH_GOVERNANCE * gov_score
        + WEIGHT_HEALTH_RISK * risk_posture
        + WEIGHT_HEALTH_DATA_QUALITY * data_quality_score
        + WEIGHT_HEALTH_PORTFOLIO * port_score
    )
    composite = round(max(0.0, min(100.0, composite)), 2)

    if composite >= 85.0:
        grade = OperationalHealthGrade.EXCELLENT
    elif composite >= 70.0:
        grade = OperationalHealthGrade.GOOD
    elif composite >= 50.0:
        grade = OperationalHealthGrade.DEGRADED
    else:
        grade = OperationalHealthGrade.CRITICAL

    factors = {
        "alert_score": round(alert_score, 2),
        "alert_penalty": round(alert_penalty, 2),
        "governance_score": round(gov_score, 2),
        "risk_posture_score": round(risk_posture, 2),
        "data_quality_score": round(data_quality_score, 2),
        "portfolio_balance_score": round(port_score, 2),
    }
    return composite, grade, factors


def calculate_escalation_tier(
    severity: MonitoringSeverity,
    business_impact: str = "MEDIUM",
    has_critical_blockers: bool = False,
    is_governance_non_compliant: bool = False,
) -> EscalationLevel:
    """Determines executive escalation level deterministically."""
    if severity == MonitoringSeverity.CRITICAL or has_critical_blockers or business_impact == "TRANSFORMATIONAL":
        return EscalationLevel.EXECUTIVE_ESCALATION
    if severity == MonitoringSeverity.HIGH or is_governance_non_compliant or business_impact == "HIGH":
        return EscalationLevel.EXECUTIVE_REVIEW
    if severity == MonitoringSeverity.MEDIUM or business_impact == "MEDIUM":
        return EscalationLevel.ACTION_REQUIRED
    return EscalationLevel.WATCH
