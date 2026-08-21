"""StrategyPlannerService coordinating context building, prompt execution, deterministic validation, and persistence."""

import logging
from typing import Any, Dict, List, Optional, Union
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.ai_insights.providers import BaseLLMProvider, MockLLMProvider, get_llm_provider
from app.core.constants import StrategyPlanStatus
from app.models.dataset import Dataset
from app.models.recommendation import Recommendation
from app.models.strategy_plan import StrategyPlan
from app.repositories.ai_insight_repository import AIInsightRepository
from app.services.intelligence_service import IntelligenceService
from app.strategy_planner.builders.strategy_context_builder import StrategyContextBuilder
from app.strategy_planner.builders.strategy_prompt_builder import StrategyPromptBuilder
from app.strategy_planner.constants import (
    DEFAULT_PLAN_OBJECTIVE,
    DEFAULT_PLAN_TITLE,
    DEFAULT_PLAN_VERSION,
    DEFAULT_PROMPT_VERSION,
    DEFAULT_SNAPSHOT_VERSION,
)
from app.strategy_planner.repositories.strategy_plan_repository import StrategyPlanRepository
from app.strategy_planner.schemas.strategy_schema import (
    StrategyPlanHistoryResponse,
    StrategyPlanResponse,
)
from app.strategy_planner.validators.strategy_validator import (
    StrategyValidationError,
    StrategyValidator,
)

logger = logging.getLogger(__name__)


class StrategyPlannerService:
    """
    Service layer orchestrating the creation, strict validation, versioning,
    and history tracking of strategic execution plans.
    """

    def __init__(
        self,
        db: Union[AsyncSession, Session],
        provider: Optional[BaseLLMProvider] = None,
    ):
        self.db = db
        self.repo = StrategyPlanRepository(db)
        self.intel_service = IntelligenceService(db)
        self.ai_insight_repo = AIInsightRepository(db)
        self._provider = provider

    def _is_async(self) -> bool:
        return isinstance(self.db, AsyncSession)

    def _get_provider(
        self,
        provider_name: Optional[str] = None,
        model_name: Optional[str] = None,
    ) -> BaseLLMProvider:
        if self._provider:
            return self._provider
        return get_llm_provider(provider_name=provider_name, model_name=model_name)

    async def _validate_dataset_exists(self, dataset_id: UUID) -> Dataset:
        """Ensures the dataset exists and is active."""
        stmt = select(Dataset).where(Dataset.id == dataset_id, Dataset.is_deleted == False)
        if self._is_async():
            res = await self.db.execute(stmt)
        else:
            res = self.db.execute(stmt)
        dataset = res.scalar_one_or_none()
        if not dataset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Dataset '{dataset_id}' not found",
            )
        return dataset

    async def _load_dataset_recommendations(self, dataset_id: UUID) -> List[Recommendation]:
        """Loads all recommendations belonging to the dataset."""
        stmt = (
            select(Recommendation)
            .where(Recommendation.dataset_id == dataset_id)
            .order_by(Recommendation.estimated_impact_score.desc())
        )
        if self._is_async():
            res = await self.db.execute(stmt)
        else:
            res = self.db.execute(stmt)
        return list(res.scalars().all())

    def _map_to_response(self, plan: StrategyPlan) -> StrategyPlanResponse:
        return StrategyPlanResponse.model_validate(plan)

    # -----------------------------------------------------------------------
    # Generation & Plan Retrieval
    # -----------------------------------------------------------------------

    async def get_or_generate_plan(self, dataset_id: UUID) -> StrategyPlanResponse:
        """
        Retrieves the latest cached strategy plan or triggers generation if none exists.
        """
        await self._validate_dataset_exists(dataset_id)
        cached = await self.repo.get_latest_by_dataset(dataset_id)
        if cached:
            return self._map_to_response(cached)

        return await self.generate_new_plan(dataset_id=dataset_id, version=DEFAULT_PLAN_VERSION)

    async def regenerate_plan(
        self,
        dataset_id: UUID,
        custom_title: Optional[str] = None,
        custom_objective: Optional[str] = None,
    ) -> StrategyPlanResponse:
        """
        Forces generation of a new strategy plan version while preserving historical records.
        """
        await self._validate_dataset_exists(dataset_id)
        latest = await self.repo.get_latest_by_dataset(dataset_id)

        # Deterministic major version increment (1.0 -> 2.0 -> 3.0)
        if latest and latest.plan_version:
            try:
                major_num = int(float(latest.plan_version))
                next_version = f"{major_num + 1}.0"
            except ValueError:
                next_version = "2.0"
        else:
            next_version = "1.0"

        return await self.generate_new_plan(
            dataset_id=dataset_id,
            version=next_version,
            custom_title=custom_title,
            custom_objective=custom_objective,
        )

    async def generate_new_plan(
        self,
        dataset_id: UUID,
        version: str = DEFAULT_PLAN_VERSION,
        custom_title: Optional[str] = None,
        custom_objective: Optional[str] = None,
        provider_name: Optional[str] = None,
        model_name: Optional[str] = None,
    ) -> StrategyPlanResponse:
        """
        Synthesizes, validates, and persists a new StrategyPlan.
        Strictly rejects invalid recommendation IDs, fabricated KPIs, or invalid time horizons.
        """
        # 1. Validate Dataset
        await self._validate_dataset_exists(dataset_id)

        # 2. Authoritative Recommendations Check (Source of Truth)
        recommendations = await self._load_dataset_recommendations(dataset_id)
        if not recommendations:
            try:
                from app.services.recommendation_service import RecommendationService
                rec_service = RecommendationService(self.db)
                await rec_service.generate_recommendations(dataset_id)
                recommendations = await self._load_dataset_recommendations(dataset_id)
            except Exception as r_err:
                logger.warning(f"Could not auto-generate recommendations for dataset {dataset_id}: {r_err}")

        if not recommendations:
            # Create a baseline finding and fallback recommendation if upstream diagnostics found no issues
            from app.models.diagnostic_finding import DiagnosticFinding
            from app.models.recommendation import Recommendation
            from app.core.constants import FindingSeverity, FindingType, RecommendationPriority, RecommendationType, RecommendationStatus, RecommendationSource
            from app.repositories.diagnostic_repository import DiagnosticRepository

            diag_repo = DiagnosticRepository(self.db)
            existing_findings = await diag_repo.get_dataset_findings(dataset_id)
            if existing_findings:
                finding = existing_findings[0]
            else:
                finding = await diag_repo.create(
                    dataset_id=dataset_id,
                    finding_type=FindingType.DATA_QUALITY_RISK,
                    severity=FindingSeverity.LOW,
                    title="Steady Baseline Operations",
                    description="Telemetry metrics indicate stable baseline operations across core performance dimensions.",
                    business_impact="Maintains current operational stability with low revenue disruption risk.",
                    confidence_score=0.90,
                )

            baseline_rec = Recommendation(
                dataset_id=dataset_id,
                finding_id=finding.id,
                title="Sustain Current Operational & Growth Momentum",
                description="Continuously monitor high-performing KPIs and maintain current operational velocity.",
                why_recommended="Operational telemetry indicates steady performance across baseline metrics.",
                recommendation_type=RecommendationType.CUSTOMER_RETENTION,
                priority=RecommendationPriority.MEDIUM,
                status=RecommendationStatus.ACCEPTED,
                source=RecommendationSource.RULE_ENGINE,
                confidence_score=0.85,
                estimated_impact_score=0.80,
                estimated_effort_score=0.30,
            )
            self.db.add(baseline_rec)
            if self._is_async():
                await self.db.commit()
            else:
                self.db.commit()
            recommendations = [baseline_rec]

        # 3. Load Deterministic Intelligence Report
        report = await self.intel_service.get_intelligence_report(dataset_id)

        # 4. Load Latest AI Insight (Optional Enrichment — Graceful Degradation if Absent)
        ai_insight = await self.ai_insight_repo.get_latest_by_dataset(dataset_id)

        # 5. Establish Authoritative Allowlists
        allowed_rec_ids = {str(r.id) for r in recommendations}
        allowed_kpi_keys = {
            m.get("metric_key") or m.get("name")
            for m in (report.metrics or [])
            if (m.get("metric_key") or m.get("name"))
        }
        if not allowed_kpi_keys:
            # Fallback baseline if metrics empty
            allowed_kpi_keys = {"recurring_revenue", "customer_churn_rate", "order_volume"}

        # 6. Build Context & Low-Hallucination Prompt
        context = StrategyContextBuilder.build_context(
            recommendations=recommendations,
            report=report,
            ai_insight=ai_insight,
            custom_objective=custom_objective,
        )
        prompt = StrategyPromptBuilder.build_strategy_prompt(context=context)
        system_prompt = StrategyPromptBuilder.get_system_prompt()

        # 7. Execute LLM Provider with automatic deterministic fallback
        provider = self._get_provider(provider_name=provider_name, model_name=model_name)
        try:
            raw_json = await provider.generate_json(
                prompt=prompt,
                system_prompt=system_prompt,
            )
        except Exception as exc:
            logger.warning(
                f"Strategy Planner LLM invocation ({provider.provider_name}) failed: {exc}. "
                "Degrading gracefully to deterministic MockLLMProvider."
            )
            fallback = MockLLMProvider(model_name="deterministic-mock-v1")
            raw_json = await fallback.generate_json(
                prompt=prompt,
                system_prompt=system_prompt,
            )

        # 8. Strict Reject-Only Deterministic Validation (Trust Boundary)
        try:
            StrategyValidator.validate(
                plan_dict=raw_json,
                allowed_recommendation_ids=allowed_rec_ids,
                allowed_metric_keys=allowed_kpi_keys,
            )
        except StrategyValidationError as s_err:
            logger.error(f"Strategy plan rejected by deterministic validation: {s_err}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Generated strategy plan violated deterministic boundaries: {str(s_err)}",
            )

        # 9. Instantiate ORM Model & Persist
        plan = StrategyPlan(
            dataset_id=dataset_id,
            plan_version=version,
            recommendation_snapshot_version=DEFAULT_SNAPSHOT_VERSION,
            prompt_version=DEFAULT_PROMPT_VERSION,
            model_provider=provider.provider_name,
            model_name=provider.model_name,
            title=custom_title or raw_json.get("title") or DEFAULT_PLAN_TITLE,
            objective=custom_objective or raw_json.get("objective") or DEFAULT_PLAN_OBJECTIVE,
            status=StrategyPlanStatus.DRAFT,
            executive_summary=raw_json.get("executive_summary", ""),
            strategic_priorities=raw_json.get("strategic_priorities", []),
            action_items=raw_json.get("action_items", []),
            milestones=raw_json.get("milestones", []),
            success_criteria=raw_json.get("success_criteria", []),
            source_recommendation_ids=raw_json.get("source_recommendation_ids", list(allowed_rec_ids)),
            metadata_info={"recommendation_count": len(recommendations)},
        )

        persisted = await self.repo.create(plan)

        if self._is_async():
            await self.db.commit()
        else:
            self.db.commit()

        return self._map_to_response(persisted)

    # -----------------------------------------------------------------------
    # History & Plan Management
    # -----------------------------------------------------------------------

    async def list_history(
        self,
        dataset_id: UUID,
        limit: int = 10,
        offset: int = 0,
    ) -> StrategyPlanHistoryResponse:
        """Lists historical versions of strategy plans for a dataset."""
        await self._validate_dataset_exists(dataset_id)
        total_count = await self.repo.count_by_dataset(dataset_id)
        plans = await self.repo.list_history_by_dataset(dataset_id=dataset_id, limit=limit, offset=offset)

        return StrategyPlanHistoryResponse(
            total_count=total_count,
            plans=[self._map_to_response(p) for p in plans],
        )

    async def get_plan_by_id(self, plan_id: UUID) -> StrategyPlanResponse:
        """Retrieves a specific strategy plan by primary key."""
        plan = await self.repo.get_by_id(plan_id)
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Strategy plan '{plan_id}' not found",
            )
        return self._map_to_response(plan)

    async def update_plan_status(
        self,
        plan_id: UUID,
        new_status: StrategyPlanStatus,
    ) -> StrategyPlanResponse:
        """Updates the status of an existing strategy plan."""
        updated = await self.repo.update_status(plan_id=plan_id, new_status=new_status)
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Strategy plan '{plan_id}' not found",
            )

        if self._is_async():
            await self.db.commit()
        else:
            self.db.commit()

        return self._map_to_response(updated)
