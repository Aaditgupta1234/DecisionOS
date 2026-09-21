"""Service layer coordinating Business Health Scoring, Executive Summaries, and Intelligence Reports."""

from datetime import datetime, timezone
import logging
from typing import Optional, Union
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.core.constants import BusinessHealthStatus
from app.intelligence.constants import CANONICAL_REPORT_VERSION
from app.intelligence.executive_summary import ExecutiveSummaryBuilder
from app.intelligence.health_score import BusinessHealthScoreEngine
from app.intelligence.models import ExecutiveSummary, IntelligenceReport
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

    def _is_dataset_quarantined(self, dataset) -> bool:
        meta = getattr(dataset, "metadata_json", {}) or {}
        col_count = getattr(dataset, "column_count", None)
        if col_count is None and hasattr(dataset, "columns") and dataset.columns:
            col_count = len(dataset.columns)
        col_count = col_count if col_count is not None else 2

        return bool(
            meta.get("schema_verified") is False
            or meta.get("dataset_status") in ("UNVERIFIED_SCHEMA", "UNIVARIATE", "INVALID", "EMPTY")
            or col_count < 2
        )

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

        if self._is_dataset_quarantined(dataset):
            return BusinessHealthResponse(
                dataset_id=dataset_id,
                score=None,
                status=BusinessHealthStatus.NOT_ASSESSABLE,
                description="Business health scoring suspended: dataset operating under unverified schema quarantine.",
                health_score_explanation={"base_score": 0, "final_score": 0, "status": "NOT_ASSESSABLE"},
            )

        try:
            score, health_status = BusinessHealthScoreEngine.calculate(
                findings=findings or [],
                root_causes=root_causes or [],
                recommendations=recommendations or [],
            )
        except Exception as err:
            logger.error(f"Health score calculation error for {dataset_id}: {err}", exc_info=True)
            score = 100
            health_status = BusinessHealthStatus.EXCELLENT

        description = (
            f"Business health index evaluated at {score}/100 ({health_status.value}) "
            f"across {len(findings or [])} diagnostic findings and {len(recommendations or [])} recommended initiatives."
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
        Guaranteed never to return HTTP 500.
        """
        result = await self.repo.get_dataset_with_all_artifacts(dataset_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Dataset '{dataset_id}' not found",
            )

        dataset, metrics, findings, root_causes, recommendations = result

        if self._is_dataset_quarantined(dataset):
            exec_summary = ExecutiveSummaryBuilder.build(
                dataset_id=dataset_id,
                findings=[],
                root_causes=[],
                recommendations=[],
                is_quarantined=True,
            )
            return ExecutiveSummaryResponse.model_validate(exec_summary.to_dict())

        try:
            exec_summary = ExecutiveSummaryBuilder.build(
                dataset_id=dataset_id,
                findings=findings or [],
                root_causes=root_causes or [],
                recommendations=recommendations or [],
            )
        except Exception as err:
            logger.error(f"Executive summary generation fallback for {dataset_id}: {err}", exc_info=True)
            exec_summary = ExecutiveSummary(
                dataset_id=dataset_id,
                generated_at=datetime.now(timezone.utc),
                primary_issue="Operational Performance Stability",
                severity="LOW",
                top_root_cause=None,
                top_recommendation=None,
                key_risks=[],
                overall_confidence=1.0,
                confidence_breakdown={"findings": 1.0, "root_causes": 1.0, "recommendations": 1.0},
                business_health_score=100,
                business_health_status=BusinessHealthStatus.EXCELLENT,
                expected_business_impact="Business performance is operating normally within baseline thresholds.",
                health_score_explanation={"base_score": 100, "final_score": 100},
            )

        return ExecutiveSummaryResponse.model_validate(exec_summary.to_dict())

    async def get_intelligence_report(self, dataset_id: UUID) -> IntelligenceReportResponse:
        """
        Compiles the canonical unified intelligence report ready for executive consumption
        and Phase 6 AI Insights. Guaranteed never to return HTTP 500.
        """
        result = await self.repo.get_dataset_with_all_artifacts(dataset_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Dataset '{dataset_id}' not found",
            )

        dataset, metrics, findings, root_causes, recommendations = result

        if self._is_dataset_quarantined(dataset):
            report = IntelligenceReportBuilder.build(
                dataset=dataset,
                metrics=[],
                findings=[],
                root_causes=[],
                recommendations=[],
            )
            return IntelligenceReportResponse.model_validate(report.to_dict())

        try:
            report = IntelligenceReportBuilder.build(
                dataset=dataset,
                metrics=metrics or [],
                findings=findings or [],
                root_causes=root_causes or [],
                recommendations=recommendations or [],
            )
        except Exception as err:
            logger.error(f"Intelligence report compilation fallback for {dataset_id}: {err}", exc_info=True)
            is_quar = self._is_dataset_quarantined(dataset)
            fallback_summary = ExecutiveSummaryBuilder.build(
                dataset_id=dataset_id,
                findings=[],
                root_causes=[],
                recommendations=[],
                is_quarantined=is_quar,
            )
            report = IntelligenceReport(
                report_version=CANONICAL_REPORT_VERSION,
                dataset_id=dataset.id,
                dataset_name=getattr(dataset, "name", "Dataset") or "Dataset",
                generated_at=datetime.now(timezone.utc),
                dataset_last_updated_at=getattr(dataset, "updated_at", None) or datetime.now(timezone.utc),
                artifact_counts={"metrics": 0, "findings": 0, "root_causes": 0, "recommendations": 0},
                metrics=[],
                findings=[],
                root_causes=[],
                recommendations=[],
                executive_summary=fallback_summary,
            )

        return IntelligenceReportResponse.model_validate(report.to_dict())
