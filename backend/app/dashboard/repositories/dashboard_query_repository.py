"""Read-Only Domain Aggregation Query Repository for Phase 9.6 Executive Dashboard."""

import uuid
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional, Union
from sqlalchemy import desc, select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.models.dataset import Dataset
from app.models.dataset_metric import DatasetMetric
from app.models.diagnostic_finding import DiagnosticFinding
from app.models.root_cause_analysis import RootCauseAnalysis
from app.models.recommendation import Recommendation
from app.models.forecast import Forecast
from app.models.scenario import Scenario
from app.models.narrative_report import NarrativeReport
from app.models.executive_insight_report import ExecutiveInsightReport
from app.reporting.models.report_export import ReportExport
from app.models.chat_session import ChatSession
from app.dashboard.models.dashboard_telemetry import DashboardViewEvent
from app.dashboard.constants import TELEMETRY_RETENTION_DAYS


class DashboardQueryRepository:
    """
    Read-only aggregation repository for existing DecisionOS intelligence artifacts.
    Strictly queries database rows without executing calculations.
    Supports both AsyncSession and sync Session.
    """

    def __init__(self, db: Union[AsyncSession, Session]):
        self.db = db

    def _is_async(self) -> bool:
        return isinstance(self.db, AsyncSession)

    async def _execute(self, stmt: Any) -> Any:
        if self._is_async():
            return await self.db.execute(stmt)
        return self.db.execute(stmt)

    async def _flush(self) -> None:
        if self._is_async():
            await self.db.flush()
        else:
            self.db.flush()

    async def get_dataset(self, dataset_id: uuid.UUID) -> Optional[Dataset]:
        result = await self._execute(
            select(Dataset).where(Dataset.id == dataset_id)
        )
        return result.scalars().first()

    async def get_metrics(self, dataset_id: uuid.UUID) -> List[DatasetMetric]:
        result = await self._execute(
            select(DatasetMetric)
            .where(DatasetMetric.dataset_id == dataset_id)
            .order_by(DatasetMetric.metric_category, DatasetMetric.metric_name)
        )
        return list(result.scalars().all())

    async def get_findings(self, dataset_id: uuid.UUID) -> List[DiagnosticFinding]:
        result = await self._execute(
            select(DiagnosticFinding)
            .where(DiagnosticFinding.dataset_id == dataset_id)
            .order_by(DiagnosticFinding.confidence_score.desc(), DiagnosticFinding.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_root_causes(self, dataset_id: uuid.UUID) -> List[RootCauseAnalysis]:
        result = await self._execute(
            select(RootCauseAnalysis)
            .where(RootCauseAnalysis.dataset_id == dataset_id)
            .order_by(RootCauseAnalysis.impact_score.desc(), RootCauseAnalysis.confidence_score.desc())
        )
        return list(result.scalars().all())

    async def get_recommendations(self, dataset_id: uuid.UUID) -> List[Recommendation]:
        result = await self._execute(
            select(Recommendation)
            .where(Recommendation.dataset_id == dataset_id)
            .order_by(Recommendation.estimated_impact_score.desc(), Recommendation.confidence_score.desc())
        )
        return list(result.scalars().all())

    async def get_forecasts(self, dataset_id: uuid.UUID) -> List[Forecast]:
        result = await self._execute(
            select(Forecast)
            .where(Forecast.dataset_id == dataset_id)
            .order_by(Forecast.metric_key, Forecast.horizon)
        )
        return list(result.scalars().all())

    async def get_scenarios(self, dataset_id: uuid.UUID) -> List[Scenario]:
        result = await self._execute(
            select(Scenario)
            .where(Scenario.dataset_id == dataset_id)
            .order_by(Scenario.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_narratives(self, dataset_id: uuid.UUID) -> List[NarrativeReport]:
        result = await self._execute(
            select(NarrativeReport)
            .where(NarrativeReport.dataset_id == dataset_id)
            .order_by(NarrativeReport.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_executive_insights(self, dataset_id: uuid.UUID) -> Optional[ExecutiveInsightReport]:
        result = await self._execute(
            select(ExecutiveInsightReport)
            .where(ExecutiveInsightReport.dataset_id == dataset_id)
            .order_by(ExecutiveInsightReport.created_at.desc())
        )
        return result.scalars().first()

    async def get_reports(self, dataset_id: uuid.UUID, limit: int = 10) -> List[ReportExport]:
        result = await self._execute(
            select(ReportExport)
            .where(ReportExport.dataset_id == dataset_id)
            .order_by(ReportExport.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_chat_sessions(self, dataset_id: uuid.UUID) -> List[ChatSession]:
        result = await self._execute(
            select(ChatSession)
            .where(ChatSession.dataset_id == dataset_id)
            .order_by(ChatSession.updated_at.desc())
        )
        return list(result.scalars().all())

    # --- Telemetry Operations ---

    async def record_telemetry_events(
        self,
        dataset_id: uuid.UUID,
        events: List[Dict[str, Any]],
        user_id: Optional[uuid.UUID] = None,
        organization_id: Optional[uuid.UUID] = None,
    ) -> int:
        if not events:
            return 0

        db_events = []
        for e in events:
            viewed_at = e.get("viewed_at") or datetime.now(timezone.utc)
            db_event = DashboardViewEvent(
                dataset_id=dataset_id,
                organization_id=organization_id,
                user_id=user_id,
                section=e["section"],
                viewed_at=viewed_at,
                event_metadata=e.get("event_metadata", {}),
            )
            db_events.append(db_event)

        self.db.add_all(db_events)
        await self._flush()
        if not self._is_async():
            self.db.commit()
        else:
            await self.db.commit()
        return len(db_events)

    async def cleanup_old_telemetry(self, retention_days: int = TELEMETRY_RETENTION_DAYS) -> int:
        cutoff = datetime.now(timezone.utc) - timedelta(days=retention_days)
        stmt = delete(DashboardViewEvent).where(DashboardViewEvent.viewed_at < cutoff)
        result = await self._execute(stmt)
        await self._flush()
        if not self._is_async():
            self.db.commit()
        else:
            await self.db.commit()
        return result.rowcount
