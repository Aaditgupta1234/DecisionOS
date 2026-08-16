"""Opportunity Detection Engine for Phase 11.5: Strategic Recommendation & Portfolio Optimization."""

from datetime import datetime, timezone
from typing import Dict, List
from uuid import UUID

from app.portfolio.constants.benchmark_constants import PeerGroup
from app.portfolio.recommendations.constants import (
    CRITICAL_HEALTH_THRESHOLD,
    ELITE_SCORE_THRESHOLD,
    PROMOTION_MAX_SCORE,
    PROMOTION_MIN_SCORE,
    TREND_REVERSAL_THRESHOLD,
)
from app.portfolio.recommendations.schemas import (
    OpportunityCandidate,
    OpportunitySummary,
)
from app.portfolio.schemas.benchmark import WorkspaceBenchmarkDetailResponse
from app.portfolio.trends.schemas import CohortMigrationResponse


class OpportunityDetectionEngine:
    """
    Deterministic opportunity detection engine scanning portfolio telemetry,
    risk profiles, trend trajectories, and cohort positions to identify high-ROI intervention targets.
    """

    @classmethod
    def detect_risk_opportunities(
        cls, details: List[WorkspaceBenchmarkDetailResponse]
    ) -> List[OpportunityCandidate]:
        """Identifies business units in critical condition (< 60.0) requiring risk elimination."""
        candidates: List[OpportunityCandidate] = []
        for ws in details:
            if ws.health_score < CRITICAL_HEALTH_THRESHOLD:
                # Potential impact is uplift needed to cross out of critical/underperforming threshold (to 70.0)
                impact = round(max(5.0, 70.0 - ws.health_score), 1)
                candidates.append(
                    OpportunityCandidate(
                        workspace_id=ws.workspace_id,
                        workspace_name=ws.workspace_name,
                        health_score=ws.health_score,
                        peer_group=ws.peer_group,
                        score_delta=0.0,
                        opportunity_type="CRITICAL_RISK_REMEDIATION",
                        potential_impact=impact,
                    )
                )
        candidates.sort(key=lambda c: (c.health_score, -c.potential_impact))
        return candidates

    @classmethod
    def detect_trend_reversal_opportunities(
        cls,
        details: List[WorkspaceBenchmarkDetailResponse],
        migrations: CohortMigrationResponse,
    ) -> List[OpportunityCandidate]:
        """Identifies business units experiencing rapid active degradation (drop <= -5.0)."""
        migration_map = {m.workspace_id: m for m in migrations.migrations}
        candidates: List[OpportunityCandidate] = []

        for ws in details:
            mig = migration_map.get(ws.workspace_id)
            delta = mig.score_delta if mig else 0.0
            if delta <= TREND_REVERSAL_THRESHOLD:
                impact = round(abs(delta), 1)
                candidates.append(
                    OpportunityCandidate(
                        workspace_id=ws.workspace_id,
                        workspace_name=ws.workspace_name,
                        health_score=ws.health_score,
                        peer_group=ws.peer_group,
                        score_delta=delta,
                        opportunity_type="TREND_REVERSAL",
                        potential_impact=impact,
                    )
                )
        candidates.sort(key=lambda c: (c.score_delta, -c.potential_impact))
        return candidates

    @classmethod
    def detect_cohort_promotion_opportunities(
        cls, details: List[WorkspaceBenchmarkDetailResponse]
    ) -> List[OpportunityCandidate]:
        """Identifies business units on the cusp of crossing into higher peer group cohorts (75.0-89.9)."""
        candidates: List[OpportunityCandidate] = []
        for ws in details:
            if PROMOTION_MIN_SCORE <= ws.health_score <= PROMOTION_MAX_SCORE:
                target_score = 90.0 if ws.health_score >= 80.0 else 80.0
                impact = round(target_score - ws.health_score, 1)
                candidates.append(
                    OpportunityCandidate(
                        workspace_id=ws.workspace_id,
                        workspace_name=ws.workspace_name,
                        health_score=ws.health_score,
                        peer_group=ws.peer_group,
                        score_delta=0.0,
                        opportunity_type="COHORT_PROMOTION_CUSP",
                        potential_impact=impact,
                    )
                )
        candidates.sort(key=lambda c: (-c.health_score, c.potential_impact))
        return candidates

    @classmethod
    def detect_best_practice_candidates(
        cls, details: List[WorkspaceBenchmarkDetailResponse]
    ) -> List[OpportunityCandidate]:
        """Identifies flagship high-performing business units (>= 90.0) suitable for playbook replication."""
        candidates: List[OpportunityCandidate] = []
        for ws in details:
            if ws.health_score >= ELITE_SCORE_THRESHOLD:
                candidates.append(
                    OpportunityCandidate(
                        workspace_id=ws.workspace_id,
                        workspace_name=ws.workspace_name,
                        health_score=ws.health_score,
                        peer_group=ws.peer_group,
                        score_delta=0.0,
                        opportunity_type="BEST_PRACTICE_ANCHOR",
                        potential_impact=0.0,
                    )
                )
        candidates.sort(key=lambda c: -c.health_score)
        return candidates

    @classmethod
    def detect_all_opportunities(
        cls,
        organization_id: UUID,
        details: List[WorkspaceBenchmarkDetailResponse],
        migrations: CohortMigrationResponse,
        total_portfolio: int,
    ) -> OpportunitySummary:
        """Aggregates and synthesizes all detected opportunities across the portfolio."""
        risk_units = cls.detect_risk_opportunities(details)
        declining_units = cls.detect_trend_reversal_opportunities(details, migrations)
        promotion_units = cls.detect_cohort_promotion_opportunities(details)
        best_practice_units = cls.detect_best_practice_candidates(details)

        # High impact opportunities pool
        all_active = risk_units + declining_units + promotion_units
        highest_impact = sorted(all_active, key=lambda c: -c.potential_impact)[:10]

        return OpportunitySummary(
            organization_id=organization_id,
            portfolio_size=total_portfolio,
            analyzed_workspaces=len(details),
            risk_opportunity_count=len(risk_units),
            trend_reversal_count=len(declining_units),
            promotion_candidate_count=len(promotion_units),
            best_practice_candidate_count=len(best_practice_units),
            highest_risk_units=risk_units,
            fastest_declining_units=declining_units,
            best_practice_candidates=best_practice_units,
            cohort_promotion_candidates=promotion_units,
            highest_impact_opportunities=highest_impact,
            generated_at=datetime.now(timezone.utc),
        )
