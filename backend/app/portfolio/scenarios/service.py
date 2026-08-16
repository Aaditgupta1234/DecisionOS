"""Scenario Planning Service for Phase 11.4: Executive Scenario Modeling & Strategic Planning Intelligence."""

import uuid
from datetime import datetime, timezone
from typing import List, Optional, Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.portfolio.constants.benchmark_constants import PeerGroup
from app.portfolio.executive.services import PortfolioExecutiveService
from app.portfolio.repositories.portfolio_repository import PortfolioRepository
from app.portfolio.scenarios.analyzers import StrategicImpactAnalyzer
from app.portfolio.scenarios.constants import (
    SCENARIO_ENGINE_VERSION,
    SCENARIO_SCHEMA_VERSION,
    ScenarioType,
)
from app.portfolio.scenarios.engine import ScenarioModelingEngine
from app.portfolio.scenarios.observability.scenario_metrics import scenario_metrics
from app.portfolio.scenarios.schemas import (
    ScenarioAdjustment,
    ScenarioComparisonResponse,
    ScenarioInput,
    ScenarioResponse,
    ScenarioTemplate,
)
from app.portfolio.services.portfolio_benchmark_service import PortfolioBenchmarkService
from app.portfolio.trends.constants import DEFAULT_TREND_WINDOW
from app.portfolio.trends.services.portfolio_trends_service import PortfolioTrendsService


class ScenarioPlanningService:
    """
    Central orchestration service for executive scenario modeling, evaluation, and comparisons.
    """

    def __init__(self, db: Union[AsyncSession, Session]) -> None:
        self.db = db
        self.repo = PortfolioRepository(db)
        self.benchmark_service = PortfolioBenchmarkService(db)
        self.trends_service = PortfolioTrendsService(db)
        self.executive_service = PortfolioExecutiveService(db)

    @classmethod
    def get_templates(cls) -> List[ScenarioTemplate]:
        """Returns standard pre-configured strategic scenario templates."""
        scenario_metrics.record_template_requested()
        return [
            ScenarioTemplate(
                template_id="underperforming-recovery",
                name="Underperforming Business Unit Recovery",
                description="Simulates a +15.0 point operational recovery across all business units currently performing below 70.0 points.",
                scenario_type=ScenarioType.HEALTH_IMPROVEMENT,
                default_input=ScenarioInput(
                    name="Underperforming Recovery (+15 pts)",
                    description="Remediation uplift for units with health score < 70.0",
                    scenario_type=ScenarioType.HEALTH_IMPROVEMENT,
                    adjustments=[
                        ScenarioAdjustment(
                            target_type="THRESHOLD",
                            max_score_cutoff=69.9,
                            score_delta=15.0,
                        )
                    ],
                ),
            ),
            ScenarioTemplate(
                template_id="critical-risk-remediation",
                name="Critical Risk Elimination",
                description="Simulates targeted turnaround of all CRITICAL_ATTENTION units to baseline stability (75.0 points).",
                scenario_type=ScenarioType.RISK_REDUCTION,
                default_input=ScenarioInput(
                    name="Critical Risk Elimination (Override to 75.0)",
                    description="Turnaround of all critical units to mid-tier stability",
                    scenario_type=ScenarioType.RISK_REDUCTION,
                    adjustments=[
                        ScenarioAdjustment(
                            target_type="COHORT",
                            target_value=PeerGroup.CRITICAL_ATTENTION.value,
                            override_score=75.0,
                        )
                    ],
                ),
            ),
            ScenarioTemplate(
                template_id="downside-stress-test",
                name="Portfolio Downside Stress Test",
                description="Simulates a macroeconomic or operational market shock reducing health scores by -10.0 points across all business units.",
                scenario_type=ScenarioType.HEALTH_DECLINE,
                default_input=ScenarioInput(
                    name="Downside Stress Test (-10 pts)",
                    description="Macroeconomic downside shock across entire portfolio",
                    scenario_type=ScenarioType.HEALTH_DECLINE,
                    adjustments=[
                        ScenarioAdjustment(
                            target_type="ALL",
                            score_delta=-10.0,
                        )
                    ],
                ),
            ),
            ScenarioTemplate(
                template_id="elite-expansion",
                name="Elite Performance Acceleration",
                description="Simulates expanding best practices to boost top and strong performers by +5.0 points.",
                scenario_type=ScenarioType.COHORT_PROMOTION,
                default_input=ScenarioInput(
                    name="Elite Performance Acceleration (+5 pts)",
                    description="Uplift across top and strong performing units",
                    scenario_type=ScenarioType.COHORT_PROMOTION,
                    adjustments=[
                        ScenarioAdjustment(
                            target_type="COHORT",
                            target_value=PeerGroup.TOP_PERFORMERS.value,
                            score_delta=5.0,
                        ),
                        ScenarioAdjustment(
                            target_type="COHORT",
                            target_value=PeerGroup.HIGH_PERFORMERS.value,
                            score_delta=5.0,
                        ),
                    ],
                ),
            ),
        ]

    async def evaluate_scenario(
        self, organization_id: uuid.UUID, scenario_input: ScenarioInput
    ) -> ScenarioResponse:
        """
        Evaluates a deterministic scenario against the current portfolio state in-memory.
        """
        scenario_metrics.record_scenario_evaluated(scenario_input.scenario_type.value)

        # 1. Fetch baseline data
        details, avg_score, _, total_portfolio = await self.benchmark_service._build_workspace_details(
            organization_id
        )
        risk_summary = await self.executive_service.get_risk_summary(
            organization_id, window_days=scenario_input.lookback_days
        )
        momentum = await self.trends_service.get_portfolio_momentum(
            organization_id, window_days=scenario_input.lookback_days
        )

        # 2. Run simulation engine
        projected_states = ScenarioModelingEngine.apply_adjustments(
            details, scenario_input.adjustments
        )

        # 3. Analyze impacts
        ws_impacts = StrategicImpactAnalyzer.analyze_workspace_impacts(projected_states)
        port_impact = StrategicImpactAnalyzer.analyze_portfolio_impact(
            details, projected_states, risk_summary, momentum.portfolio_momentum_score
        )
        impact_level = StrategicImpactAnalyzer.evaluate_impact_level(
            port_impact.health_score_delta, port_impact.risk_concentration_delta_pct
        )
        result_status = StrategicImpactAnalyzer.evaluate_result_status(
            port_impact.health_score_delta, port_impact.risk_concentration_delta_pct
        )
        assumptions = StrategicImpactAnalyzer.generate_assumptions(scenario_input.adjustments)

        # 4. Coverage metrics
        analyzed_count = len(details)
        affected_count = sum(1 for w in ws_impacts if abs(w.score_delta) > 0.001)
        affected_pct = round((affected_count / max(1, analyzed_count)) * 100.0, 1)

        # 5. Baseline snapshot provenance
        snapshots = await self.repo.get_snapshots_by_org(
            organization_id, limit=365, lookback_days=scenario_input.lookback_days
        )
        baseline_snap = snapshots[-1] if snapshots else None
        baseline_snap_id = baseline_snap.id if baseline_snap else None
        baseline_snap_gen = None
        if baseline_snap:
            baseline_snap_gen = getattr(baseline_snap, "snapshot_date", None) or getattr(
                baseline_snap, "created_at", None
            )

        now = datetime.now(timezone.utc)
        return ScenarioResponse(
            scenario_id=uuid.uuid4(),
            organization_id=organization_id,
            name=scenario_input.name,
            description=scenario_input.description,
            scenario_type=scenario_input.scenario_type,
            portfolio_size=total_portfolio,
            analyzed_workspaces=analyzed_count,
            affected_workspace_count=affected_count,
            affected_percentage=affected_pct,
            baseline_snapshot_id=baseline_snap_id,
            baseline_snapshot_generated_at=baseline_snap_gen,
            assumptions=assumptions,
            portfolio_impact=port_impact,
            workspace_impacts=ws_impacts,
            impact_level=impact_level,
            result_status=result_status,
            scenario_version=SCENARIO_ENGINE_VERSION,
            scenario_schema_version=SCENARIO_SCHEMA_VERSION,
            scenario_generated_at=now,
        )

    async def compare_scenarios(
        self, organization_id: uuid.UUID, inputs: List[ScenarioInput]
    ) -> ScenarioComparisonResponse:
        """
        Evaluates and ranks multiple scenarios side-by-side with strategic trade-off analysis.
        """
        scenario_metrics.record_comparison_executed()

        evaluated: List[ScenarioResponse] = []
        for inp in inputs:
            res = await self.evaluate_scenario(organization_id, inp)
            evaluated.append(res)

        # Sort scenarios: highest projected health score DESC, then lowest projected risk concentration ASC
        sorted_scenarios = sorted(
            evaluated,
            key=lambda s: (
                -(s.portfolio_impact.projected_health_score or 0.0),
                s.portfolio_impact.projected_risk_concentration_pct,
            ),
        )

        rankings = [s.scenario_id for s in sorted_scenarios]
        best_case_id = sorted_scenarios[0].scenario_id if sorted_scenarios else None
        worst_case_id = sorted_scenarios[-1].scenario_id if sorted_scenarios else None

        # Strategic recommendation synthesis
        if sorted_scenarios:
            best = sorted_scenarios[0]
            rec = (
                f"Scenario '{best.name}' yields the highest portfolio return (+{best.portfolio_impact.health_score_delta:+.1f} pts) "
                f"and projects risk concentration at {best.portfolio_impact.projected_risk_concentration_pct}%."
            )
        else:
            rec = "No scenarios provided for comparison."

        return ScenarioComparisonResponse(
            organization_id=organization_id,
            scenarios=evaluated,
            scenario_rankings=rankings,
            best_case_scenario_id=best_case_id,
            worst_case_scenario_id=worst_case_id,
            strategic_recommendation=rec,
            comparison_generated_at=datetime.now(timezone.utc),
        )

    async def get_examples(self, organization_id: uuid.UUID) -> List[ScenarioResponse]:
        """Evaluates and returns standard pre-built scenario examples."""
        templates = self.get_templates()
        results: List[ScenarioResponse] = []
        for t in templates:
            res = await self.evaluate_scenario(organization_id, t.default_input)
            results.append(res)
        return results
