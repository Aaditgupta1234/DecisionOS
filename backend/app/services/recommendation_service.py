"""Service layer orchestrating Recommendation Engine execution, persistence, and AI summaries."""

import logging
from collections import defaultdict
from typing import Dict, List, Optional, Union
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.core.constants import RecommendationPriority, RecommendationStatus
from app.diagnostics.diagnostic_engine import DiagnosticEngine
from app.models.dataset import Dataset
from app.models.diagnostic_finding import DiagnosticFinding
from app.models.recommendation import Recommendation
from app.models.root_cause_analysis import RootCauseAnalysis
from app.repositories.diagnostic_repository import DiagnosticRepository
from app.repositories.recommendation_repository import RecommendationRepository
from app.repositories.root_cause_repository import RootCauseRepository
from app.recommendations.engine import RecommendationEngine
from app.root_cause.engine import RootCauseEngine
from app.schemas.recommendation import (
    DatasetRecommendationsResponse,
    RecommendationItem,
    RecommendationResponse,
    RecommendationSummary,
)

logger = logging.getLogger(__name__)


class RecommendationService:
    """
    Business service coordinating diagnostic finding retrieval, root cause inputs,
    recommendation synthesis, and lifecycle transitions.
    """

    def __init__(self, db: Union[AsyncSession, Session]):
        self.db = db
        self.rec_repo = RecommendationRepository(db)
        self.diag_repo = DiagnosticRepository(db)
        self.rca_repo = RootCauseRepository(db)
        self.engine = RecommendationEngine()

    def _is_async(self) -> bool:
        return isinstance(self.db, AsyncSession)

    async def _get_dataset_or_404(self, dataset_id: UUID) -> Dataset:
        """Retrieves a dataset or raises 404."""
        stmt = select(Dataset).where(Dataset.id == dataset_id)
        if self._is_async():
            result = await self.db.execute(stmt)
        else:
            result = self.db.execute(stmt)

        dataset = result.scalar_one_or_none()
        if not dataset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Dataset '{dataset_id}' not found",
            )
        return dataset

    async def generate_recommendations(
        self,
        dataset_id: UUID,
        recalculate_upstream: bool = False,
    ) -> DatasetRecommendationsResponse:
        """
        Synthesizes actionable recommendations for a dataset's findings and root causes.
        """
        dataset = await self._get_dataset_or_404(dataset_id)

        # 1. Optionally recalculate diagnostics and root causes
        findings = await self.diag_repo.get_dataset_findings(dataset_id)
        if recalculate_upstream or not findings:
            diag_engine = DiagnosticEngine(self.db)
            findings = await diag_engine.run(dataset_id)

        root_causes = await self.rca_repo.get_by_dataset(dataset_id)
        if (recalculate_upstream or not root_causes) and len(findings) >= 2:
            rca_engine = RootCauseEngine()
            rca_models, _ = rca_engine.analyze(findings, dataset_id=dataset_id)
            await self.rca_repo.delete_by_dataset(dataset_id)
            root_causes = await self.rca_repo.create_many(rca_models)

        # 2. Clear old recommendations for clean idempotency
        await self.rec_repo.delete_by_dataset(dataset_id)

        if not findings:
            return DatasetRecommendationsResponse(
                dataset_id=dataset_id,
                total_recommendations=0,
                recommendations=[],
                summaries=[],
            )

        # 3. Generate candidate recommendations
        rec_models = self.engine.generate_recommendations(
            findings=findings,
            root_causes=root_causes,
        )

        # 4. Bulk persist
        persisted_recs = await self.rec_repo.create_many(rec_models)

        # 5. Commit session
        if self._is_async():
            await self.db.commit()
        else:
            self.db.commit()

        # 6. Build AI-ready summaries
        summaries = self._build_summaries(persisted_recs, findings)

        response_recs = [RecommendationResponse.model_validate(r) for r in persisted_recs]

        return DatasetRecommendationsResponse(
            dataset_id=dataset_id,
            total_recommendations=len(persisted_recs),
            recommendations=response_recs,
            summaries=summaries,
        )

    async def get_dataset_recommendations(
        self,
        dataset_id: UUID,
        status: Optional[RecommendationStatus] = None,
        priority: Optional[RecommendationPriority] = None,
    ) -> DatasetRecommendationsResponse:
        """
        Retrieves existing recommendations for a dataset, generating on-demand if empty.
        """
        dataset = await self._get_dataset_or_404(dataset_id)
        recs = await self.rec_repo.get_by_dataset(dataset_id, status=status, priority=priority)

        if not recs and status is None and priority is None:
            # Generate on demand
            return await self.generate_recommendations(dataset_id, recalculate_upstream=False)

        findings = await self.diag_repo.get_dataset_findings(dataset_id)
        summaries = self._build_summaries(recs, findings)

        return DatasetRecommendationsResponse(
            dataset_id=dataset_id,
            total_recommendations=len(recs),
            recommendations=[RecommendationResponse.model_validate(r) for r in recs],
            summaries=summaries,
        )

    async def get_recommendation_by_id(
        self,
        recommendation_id: UUID,
    ) -> RecommendationResponse:
        """Retrieves a single Recommendation by ID or raises 404."""
        rec = await self.rec_repo.get_by_id(recommendation_id)
        if not rec:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Recommendation '{recommendation_id}' not found",
            )
        return RecommendationResponse.model_validate(rec)

    async def update_recommendation_status(
        self,
        recommendation_id: UUID,
        new_status: RecommendationStatus,
    ) -> RecommendationResponse:
        """Updates lifecycle status (e.g. ACCEPTED, IMPLEMENTED)."""
        updated = await self.rec_repo.update_status(recommendation_id, new_status)
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Recommendation '{recommendation_id}' not found",
            )
        if self._is_async():
            await self.db.commit()
        else:
            self.db.commit()
        return RecommendationResponse.model_validate(updated)

    async def get_recommendation_summary(
        self,
        dataset_id: UUID,
    ) -> List[RecommendationSummary]:
        """Returns consolidated AI-ready problem summaries for a dataset."""
        dataset_res = await self.get_dataset_recommendations(dataset_id)
        return dataset_res.summaries

    def _build_summaries(
        self,
        recommendations: List[Recommendation],
        findings: List[DiagnosticFinding],
    ) -> List[RecommendationSummary]:
        """
        Groups recommendations by primary finding into structured AI-ready problem summaries.
        """
        findings_map = {f.id: f for f in findings}
        grouped: Dict[UUID, List[Recommendation]] = defaultdict(list)

        for r in recommendations:
            grouped[r.finding_id].append(r)

        summaries: List[RecommendationSummary] = []

        for finding_id, rec_list in grouped.items():
            finding = findings_map.get(finding_id)
            if not finding:
                continue

            # Convert to RecommendationItem schemas
            items = [
                RecommendationItem(
                    id=r.id,
                    title=r.title,
                    recommendation_type=r.recommendation_type.value,
                    priority=r.priority.value,
                    status=r.status.value,
                    estimated_impact_score=r.estimated_impact_score,
                    estimated_effort_score=r.estimated_effort_score,
                    expected_time_to_value=r.expected_time_to_value.value,
                    action_plan=list(r.action_plan),
                    success_metrics=list(r.success_metrics),
                    why_recommended=r.why_recommended,
                )
                for r in rec_list
            ]

            overall_conf = max((r.confidence_score for r in rec_list), default=0.80)
            highest_impact = max((r.estimated_impact_score for r in rec_list), default=0.70)
            earliest_ttv = rec_list[0].expected_time_to_value.value if rec_list else "SHORT_TERM"

            # Formulate strategic summary narrative
            expected_impact_desc = (
                f"Executing these {len(rec_list)} prioritized initiatives is projected to yield "
                f"high-magnitude business performance recovery (peak impact {highest_impact:.2f}) "
                f"addressing '{finding.title}'."
            )

            summaries.append(
                RecommendationSummary(
                    primary_issue=finding.title,
                    top_recommendations=items,
                    expected_business_impact=expected_impact_desc,
                    estimated_time_to_value=earliest_ttv,
                    overall_confidence=overall_conf,
                )
            )

        # Sort summaries by highest peak impact descending
        summaries.sort(key=lambda s: s.overall_confidence, reverse=True)
        return summaries
