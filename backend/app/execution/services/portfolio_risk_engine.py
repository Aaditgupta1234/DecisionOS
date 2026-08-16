"""
Deterministic Portfolio Execution Risk Engine for Phase 12.4.6.
Aggregates organization-wide portfolio health and risk, calculates 4-tier risk distribution buckets,
P1/P2 intervention counts, and Pareto risk concentration percentages.
"""

from datetime import datetime, timezone
import math
from typing import Dict, List, Optional
import uuid

from app.execution.constants import (
    PORTFOLIO_RISK_ENGINE_VERSION,
    ExecutionHealthGrade,
    ExecutionRiskSeverity,
    InterventionPriority,
    PortfolioRiskGrade,
    calculate_health_grade,
    calculate_portfolio_risk_grade,
)
from app.execution.schemas.health import (
    ExecutionHealthMetrics,
    ExecutionRiskMetrics,
    InterventionRecommendation,
    PortfolioExecutionHealthSummary,
)


class PortfolioExecutionRiskEngine:
    """Deterministic mathematical engine for aggregate portfolio health and risk analytics."""

    @classmethod
    def calculate_portfolio_health_summary(
        cls,
        organization_id: uuid.UUID,
        initiative_health_map: Dict[uuid.UUID, ExecutionHealthMetrics],
        initiative_risk_map: Dict[uuid.UUID, ExecutionRiskMetrics],
        interventions: List[InterventionRecommendation],
        as_of_date: Optional[datetime] = None,
    ) -> PortfolioExecutionHealthSummary:
        """
        Computes portfolio-wide health, risk, 4-tier risk distribution, and Pareto risk concentration.
        """
        now = as_of_date or datetime.now(timezone.utc)
        init_ids = list(initiative_health_map.keys())
        total_inits = len(init_ids)

        if total_inits == 0:
            return PortfolioExecutionHealthSummary(
                organization_id=organization_id,
                total_initiatives=0,
                average_health_score=100.0,
                average_risk_score=0.0,
                portfolio_health_grade=ExecutionHealthGrade.EXCELLENT,
                portfolio_risk_grade=PortfolioRiskGrade.LOW,
                healthy_initiatives_count=0,
                at_risk_initiatives_count=0,
                critical_initiatives_count=0,
                low_risk_count=0,
                medium_risk_count=0,
                high_risk_count=0,
                critical_risk_count=0,
                p1_interventions_count=0,
                p2_interventions_count=0,
                risk_concentration_percentage=0.0,
                calculated_at=now,
                engine_version=PORTFOLIO_RISK_ENGINE_VERSION,
                snapshot_compatible=True,
            )

        health_scores = [h.health_score for h in initiative_health_map.values()]
        risk_scores = [r.risk_score for r in initiative_risk_map.values()]

        avg_health = round(sum(health_scores) / total_inits, 1)
        avg_risk = round(sum(risk_scores) / total_inits, 1)

        health_grade = calculate_health_grade(avg_health)
        risk_grade = calculate_portfolio_risk_grade(avg_risk)

        # Health Distribution
        healthy_count = sum(1 for s in health_scores if s >= 75.0)
        at_risk_count = sum(1 for s in health_scores if 40.0 <= s < 75.0)
        critical_count = sum(1 for s in health_scores if s < 40.0)

        # 4-Tier Risk Distribution
        low_risk = sum(1 for r in initiative_risk_map.values() if r.risk_severity == ExecutionRiskSeverity.LOW)
        med_risk = sum(1 for r in initiative_risk_map.values() if r.risk_severity == ExecutionRiskSeverity.MEDIUM)
        high_risk = sum(1 for r in initiative_risk_map.values() if r.risk_severity == ExecutionRiskSeverity.HIGH)
        crit_risk = sum(1 for r in initiative_risk_map.values() if r.risk_severity == ExecutionRiskSeverity.CRITICAL)

        # Intervention counts
        p1_count = sum(1 for i in interventions if i.priority_level == InterventionPriority.P1)
        p2_count = sum(1 for i in interventions if i.priority_level == InterventionPriority.P2)

        # Pareto Risk Concentration (% of total risk concentrated in top 20% highest-risk initiatives)
        sorted_risks = sorted(risk_scores, reverse=True)
        total_risk_sum = sum(sorted_risks)
        top_20_count = max(1, math.ceil(0.20 * total_inits))
        top_risk_sum = sum(sorted_risks[:top_20_count])

        if total_risk_sum > 0:
            concentration_pct = round((top_risk_sum / total_risk_sum) * 100.0, 1)
        else:
            concentration_pct = 0.0

        return PortfolioExecutionHealthSummary(
            organization_id=organization_id,
            total_initiatives=total_inits,
            average_health_score=avg_health,
            average_risk_score=avg_risk,
            portfolio_health_grade=health_grade,
            portfolio_risk_grade=risk_grade,
            healthy_initiatives_count=healthy_count,
            at_risk_initiatives_count=at_risk_count,
            critical_initiatives_count=critical_count,
            low_risk_count=low_risk,
            medium_risk_count=med_risk,
            high_risk_count=high_risk,
            critical_risk_count=crit_risk,
            p1_interventions_count=p1_count,
            p2_interventions_count=p2_count,
            risk_concentration_percentage=concentration_pct,
            calculated_at=now,
            engine_version=PORTFOLIO_RISK_ENGINE_VERSION,
            snapshot_compatible=True,
        )
