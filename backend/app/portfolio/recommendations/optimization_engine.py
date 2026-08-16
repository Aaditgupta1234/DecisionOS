"""Portfolio Optimization Engine for Phase 11.5: Strategic Recommendation & Portfolio Optimization."""

from datetime import datetime, timezone
from typing import Dict, List, Optional, Set, Tuple
from uuid import UUID

from app.portfolio.recommendations.constants import (
    EFFORT_WEIGHTS,
    IMPACT_HIGH_THRESHOLD,
    IMPACT_MEDIUM_THRESHOLD,
    IMPACT_TRANSFORMATIONAL_THRESHOLD,
    PRIORITY_WEIGHTS,
    RECOMMENDATION_VERSION,
    RecommendationImpactLevel,
    RecommendationPriority,
)
from app.portfolio.recommendations.schemas import (
    ExecutiveActionPlan,
    PortfolioOptimizationResponse,
    StrategicRecommendation,
)


class PortfolioOptimizationEngine:
    """
    Evaluates ROI optimization scores, applies 4-factor deterministic tie-breaking ranking,
    and triages recommendations into executive action plans.
    """

    @staticmethod
    def classify_impact_level(expected_impact: float) -> RecommendationImpactLevel:
        """Classifies expected health score improvement into strategic impact tiers."""
        if expected_impact >= IMPACT_TRANSFORMATIONAL_THRESHOLD:
            return RecommendationImpactLevel.TRANSFORMATIONAL
        elif expected_impact >= IMPACT_HIGH_THRESHOLD:
            return RecommendationImpactLevel.HIGH
        elif expected_impact >= IMPACT_MEDIUM_THRESHOLD:
            return RecommendationImpactLevel.MEDIUM
        return RecommendationImpactLevel.LOW

    @classmethod
    def optimize_and_rank(
        cls, recommendations: List[StrategicRecommendation]
    ) -> List[StrategicRecommendation]:
        """
        Computes optimization scores, classifies impact tiers, and applies 4-factor tie-breaking sorting:
        1. optimization_score DESC
        2. priority weight DESC
        3. expected_health_impact DESC
        4. recommendation_type ASC
        """
        for r in recommendations:
            effort_weight = EFFORT_WEIGHTS.get(r.implementation_effort, 2.0)
            r.optimization_score = round(r.expected_health_impact / effort_weight, 2)
            r.impact_level = cls.classify_impact_level(r.expected_health_impact)

        # 4-Factor Deterministic Tie-Breaking Sort
        recommendations.sort(
            key=lambda r: (
                -r.optimization_score,
                -PRIORITY_WEIGHTS.get(r.priority, 1),
                -r.expected_health_impact,
                r.recommendation_type.value,
            )
        )

        # Assign 1-indexed sequential optimization ranks
        for idx, r in enumerate(recommendations, start=1):
            r.optimization_rank = idx

        return recommendations

    @classmethod
    def build_executive_action_plan(
        cls,
        organization_id: UUID,
        ranked_recommendations: List[StrategicRecommendation],
        total_portfolio: int,
        analyzed_count: int,
        source_snapshot_id: Optional[UUID] = None,
        source_snapshot_generated_at: Optional[datetime] = None,
    ) -> ExecutiveActionPlan:
        """Partitions ranked recommendations into Immediate, Near-Term, and Strategic execution horizons."""
        immediate = [r for r in ranked_recommendations if r.priority == RecommendationPriority.CRITICAL]
        near_term = [r for r in ranked_recommendations if r.priority == RecommendationPriority.HIGH]
        strategic = [
            r for r in ranked_recommendations
            if r.priority in [RecommendationPriority.MEDIUM, RecommendationPriority.LOW]
        ]

        crit_count = len(immediate)
        high_count = len(near_term)
        med_count = sum(1 for r in strategic if r.priority == RecommendationPriority.MEDIUM)
        low_count = sum(1 for r in strategic if r.priority == RecommendationPriority.LOW)

        all_affected: Set[UUID] = set()
        for r in ranked_recommendations:
            all_affected.update(r.affected_workspaces)

        affected_total = len(all_affected)
        coverage_pct = round((affected_total / max(1, analyzed_count)) * 100.0, 1)

        now = datetime.now(timezone.utc)
        return ExecutiveActionPlan(
            organization_id=organization_id,
            portfolio_size=total_portfolio,
            analyzed_workspaces=analyzed_count,
            affected_workspaces_total=affected_total,
            affected_percentage=coverage_pct,
            recommendation_coverage_percent=coverage_pct,
            critical_count=crit_count,
            high_count=high_count,
            medium_count=med_count,
            low_count=low_count,
            immediate_actions=immediate,
            near_term_actions=near_term,
            strategic_actions=strategic,
            total_recommendations=len(ranked_recommendations),
            source_snapshot_id=source_snapshot_id,
            source_snapshot_generated_at=source_snapshot_generated_at,
            recommendation_version=RECOMMENDATION_VERSION,
            recommendation_generated_at=now,
            generated_at=now,
        )

    @classmethod
    def build_optimization_response(
        cls,
        organization_id: UUID,
        ranked_recommendations: List[StrategicRecommendation],
        total_portfolio: int,
        analyzed_count: int,
        source_snapshot_id: Optional[UUID] = None,
        source_snapshot_generated_at: Optional[datetime] = None,
    ) -> PortfolioOptimizationResponse:
        """Constructs comprehensive portfolio optimization overview response."""
        top_rec = ranked_recommendations[0] if ranked_recommendations else None
        avg_opt_score = (
            round(sum(r.optimization_score for r in ranked_recommendations) / len(ranked_recommendations), 2)
            if ranked_recommendations
            else 0.0
        )
        total_impact = round(sum(r.expected_health_impact for r in ranked_recommendations), 1)

        all_affected: Set[UUID] = set()
        for r in ranked_recommendations:
            all_affected.update(r.affected_workspaces)

        affected_total = len(all_affected)
        coverage_pct = round((affected_total / max(1, analyzed_count)) * 100.0, 1)

        now = datetime.now(timezone.utc)
        return PortfolioOptimizationResponse(
            organization_id=organization_id,
            portfolio_size=total_portfolio,
            analyzed_workspaces=analyzed_count,
            affected_workspaces_total=affected_total,
            affected_percentage=coverage_pct,
            recommendation_coverage_percent=coverage_pct,
            recommendations=ranked_recommendations,
            top_recommendation=top_rec,
            average_optimization_score=avg_opt_score,
            total_potential_health_impact=total_impact,
            source_snapshot_id=source_snapshot_id,
            source_snapshot_generated_at=source_snapshot_generated_at,
            recommendation_version=RECOMMENDATION_VERSION,
            recommendation_generated_at=now,
            generated_at=now,
        )
