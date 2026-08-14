"""Service layer coordinating Business Health Scoring, Executive Summaries, and Intelligence Reports."""

import logging
from typing import Optional, Union
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.intelligence.executive_summary import ExecutiveSummaryBuilder
from app.intelligence.health_score import BusinessHealthScoreEngine
from app.intelligence.report_builder import IntelligenceReportBuilder
from app.repositories.intelligence_repository import IntelligenceRepository
from app.schemas.intelligence import (
    BusinessHealthResponse,
    ExecutiveSummaryResponse,
    IntelligenceReportResponse,
)

logger = logging.getLogger(__name__)


class IntelligenceService:
    """
    Business service layer responsible for aggregating multi-domain outputs into
    deterministic health scores, executive briefings, and comprehensive intelligence reports.
    """

    def __init__(self, db: Union[AsyncSession, Session]):
        self.db = db
        self.repo = IntelligenceRepository(db)

    async def get_health_score(self, dataset_id: UUID) -> BusinessHealthResponse:
        """
        Calculates and returns the composite Business Health Score and categorical status.
        """
        result = await self.repo.get_dataset_with_all_artifacts(dataset_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Dataset '{dataset_id}' not found",
            )

        dataset, metrics, findings, root_causes, recommendations = result

        score, health_status = BusinessHealthScoreEngine.calculate(
            findings=findings,
            root_causes=root_causes,
            recommendations=recommendations,
        )

        description = (
            f"Business health index evaluated at {score}/100 ({health_status.value}) "
            f"across {len(findings)} diagnostic findings and {len(recommendations)} recommended initiatives."
        )

        return BusinessHealthResponse(
            dataset_id=dataset_id,
            score=score,
            status=health_status,
            description=description,
        )

    async def get_executive_summary(self, dataset_id: UUID) -> ExecutiveSummaryResponse:
        """
        Synthesizes a high-level executive decision summary for the target dataset.
        """
        result = await self.repo.get_dataset_with_all_artifacts(dataset_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Dataset '{dataset_id}' not found",
            )

        dataset, metrics, findings, root_causes, recommendations = result

        exec_summary = ExecutiveSummaryBuilder.build(
            dataset_id=dataset_id,
            findings=findings,
            root_causes=root_causes,
            recommendations=recommendations,
        )

        return ExecutiveSummaryResponse.model_validate(exec_summary.to_dict())

    async def get_intelligence_report(self, dataset_id: UUID) -> IntelligenceReportResponse:
        """
        Compiles the canonical unified intelligence report ready for executive consumption
        and Phase 6 AI Insights.
        """
        result = await self.repo.get_dataset_with_all_artifacts(dataset_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Dataset '{dataset_id}' not found",
            )

        dataset, metrics, findings, root_causes, recommendations = result

        report = IntelligenceReportBuilder.build(
            dataset=dataset,
            metrics=metrics,
            findings=findings,
            root_causes=root_causes,
            recommendations=recommendations,
        )

        return IntelligenceReportResponse.model_validate(report.to_dict())
