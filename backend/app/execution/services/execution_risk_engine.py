"""
Deterministic Execution Risk Engine for Phase 12.4.3.
Computes multi-factor initiative execution risk scores (0-100), risk severities (LOW to CRITICAL),
risk trends (IMPROVING, STABLE, DETERIORATING), and extracts typed ExecutionRiskFactor classifications.
"""

from datetime import datetime, timezone
from typing import List, Optional

from app.execution.constants import (
    EXECUTION_RISK_ENGINE_VERSION,
    BudgetHealth,
    ExecutionRiskFactor,
    ExecutionRiskSeverity,
    MilestoneCriticality,
    MilestoneStatus,
    RiskTrend,
    calculate_risk_severity,
)
from app.execution.models.initiative import StrategicInitiative
from app.execution.models.milestone import InitiativeMilestone
from app.execution.models.milestone_dependency import MilestoneDependency
from app.execution.schemas.health import ExecutionHealthMetrics, ExecutionRiskMetrics
from app.execution.schemas.progress import (
    BudgetIntelligenceMetrics,
    ExecutionVelocityMetrics,
    ScheduleAdherenceMetrics,
)
from app.execution.schemas.timeline import (
    CriticalPathMetrics,
    MilestoneMetrics,
    TimelineRiskMetrics,
)
from app.execution.services.budget_engine import BudgetIntelligenceEngine
from app.execution.services.critical_path_engine import CriticalPathEngine
from app.execution.services.milestone_engine import MilestoneIntelligenceEngine
from app.execution.services.schedule_engine import ScheduleAdherenceEngine
from app.execution.services.timeline_risk_engine import TimelineRiskEngine
from app.execution.services.velocity_engine import ExecutionVelocityEngine


class ExecutionRiskEngine:
    """Deterministic mathematical engine for measuring initiative failure risk."""

    @classmethod
    def calculate_risk(
        cls,
        initiative: StrategicInitiative,
        milestones: Optional[List[InitiativeMilestone]] = None,
        dependencies: Optional[List[MilestoneDependency]] = None,
        timeline_risk_metrics: Optional[TimelineRiskMetrics] = None,
        critical_path_metrics: Optional[CriticalPathMetrics] = None,
        schedule_metrics: Optional[ScheduleAdherenceMetrics] = None,
        velocity_metrics: Optional[ExecutionVelocityMetrics] = None,
        budget_metrics: Optional[BudgetIntelligenceMetrics] = None,
        health_metrics: Optional[ExecutionHealthMetrics] = None,
        previous_risk_score: Optional[float] = None,
        as_of_date: Optional[datetime] = None,
    ) -> ExecutionRiskMetrics:
        """
        Calculates multi-factor future execution failure risk score and severity tier.
        """
        now = as_of_date or datetime.now(timezone.utc)
        ms_list = milestones or []
        dep_list = dependencies or []

        # 1. Telemetry resolution
        ms_m = MilestoneIntelligenceEngine.calculate_milestone_metrics(ms_list, as_of_date=now)
        cp_m = critical_path_metrics or CriticalPathEngine.calculate_critical_path(ms_list, dep_list, as_of_date=now)
        tr_m = timeline_risk_metrics or TimelineRiskEngine.calculate_timeline_risk(
            ms_list, dep_list, ms_m, cp_m, as_of_date=now
        )
        s_m = schedule_metrics or ScheduleAdherenceEngine.calculate_schedule_adherence(initiative, ms_list, as_of_date=now)
        v_m = velocity_metrics or ExecutionVelocityEngine.calculate_velocity(initiative, ms_list, as_of_date=now)
        b_m = budget_metrics or BudgetIntelligenceEngine.calculate_budget_health(initiative, as_of_date=now)

        # 2. Risk Sub-Component Calculations (0-100)
        # Component A: Timeline Risk Score (35% weight)
        timeline_comp = float(tr_m.timeline_risk_score)

        # Component B: Critical Path Delay Impact (25% weight)
        cp_delay_days = cp_m.projected_delay_days
        cp_instability = 100.0 - float(cp_m.critical_path_stability_score)
        cp_comp = min(100.0, max(0.0, (cp_delay_days * 5.0) + (cp_instability * 0.5)))

        # Component C: Active Blocker Penalty (20% weight)
        blocked_critical_count = sum(
            1 for m in ms_list
            if m.status == MilestoneStatus.BLOCKED and m.criticality in (MilestoneCriticality.CRITICAL, MilestoneCriticality.HIGH)
        )
        blocked_other_count = sum(
            1 for m in ms_list
            if m.status == MilestoneStatus.BLOCKED and m.criticality not in (MilestoneCriticality.CRITICAL, MilestoneCriticality.HIGH)
        )
        blocker_comp = min(100.0, (blocked_critical_count * 40.0) + (blocked_other_count * 15.0))

        # Component D: Dependency Coupling Risk (10% weight)
        dep_comp = min(100.0, len(dep_list) * 15.0)

        # Component E: Budget Overrun Risk (10% weight)
        budget_comp = max(0.0, 100.0 - float(b_m.budget_score))

        # 3. Multi-Factor Composite Risk Formula
        composite_risk = (
            (0.35 * timeline_comp)
            + (0.25 * cp_comp)
            + (0.20 * blocker_comp)
            + (0.10 * dep_comp)
            + (0.10 * budget_comp)
        )

        final_risk_score = round(min(100.0, max(0.0, composite_risk)), 1)
        risk_severity = calculate_risk_severity(final_risk_score)

        # 4. Typed Execution Risk Factor Identification
        typed_factors: List[ExecutionRiskFactor] = []

        if timeline_comp >= 50.0 or s_m.schedule_variance <= -10.0:
            typed_factors.append(ExecutionRiskFactor.TIMELINE_DELAY)

        if cp_delay_days > 0 or cp_m.critical_path_stability_score < 70.0:
            typed_factors.append(ExecutionRiskFactor.CRITICAL_PATH_EXPOSURE)

        if (blocked_critical_count + blocked_other_count) > 0:
            typed_factors.append(ExecutionRiskFactor.BLOCKED_MILESTONE)

        if len(dep_list) >= 3:
            typed_factors.append(ExecutionRiskFactor.DEPENDENCY_RISK)

        if v_m.velocity_score < 40.0 and v_m.data_sufficient:
            typed_factors.append(ExecutionRiskFactor.VELOCITY_DECLINE)

        if b_m.budget_health in (BudgetHealth.OVER_BUDGET, BudgetHealth.AT_RISK):
            typed_factors.append(ExecutionRiskFactor.BUDGET_OVERRUN)

        if health_metrics and health_metrics.health_score < 50.0:
            typed_factors.append(ExecutionRiskFactor.HEALTH_DETERIORATION)

        # 5. Risk Trend
        if previous_risk_score is not None:
            diff = final_risk_score - previous_risk_score
            if diff >= 3.0:
                trend = RiskTrend.DETERIORATING
            elif diff <= -3.0:
                trend = RiskTrend.IMPROVING
            else:
                trend = RiskTrend.STABLE
        else:
            trend = RiskTrend.STABLE

        return ExecutionRiskMetrics(
            risk_score=final_risk_score,
            risk_severity=risk_severity,
            risk_trend=trend,
            risk_factors=typed_factors,
            blocked_milestone_count=blocked_critical_count + blocked_other_count,
            critical_delay_count=ms_m.delayed_milestones,
            critical_path_exposure=cp_m.critical_path_length,
            metric_version="1.0",
            calculated_at=now,
            engine_version=EXECUTION_RISK_ENGINE_VERSION,
            snapshot_compatible=True,
        )
