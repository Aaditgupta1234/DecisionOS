"""Repository layer providing read-only unified data aggregation for business intelligence."""

from typing import List, Optional, Tuple, Union
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session, selectinload

from app.models.dataset import Dataset
from app.models.dataset_metric import DatasetMetric
from app.models.diagnostic_finding import DiagnosticFinding
from app.models.recommendation import Recommendation
from app.models.root_cause_analysis import RootCauseAnalysis


class IntelligenceRepository:
    """
    Read-only data access repository aggregating dataset metrics, diagnostic findings,
    root cause linkages, and recommendations into unified collections.
    """

    def __init__(self, db: Union[AsyncSession, Session]):
        self.db = db

    def _is_async(self) -> bool:
        return isinstance(self.db, AsyncSession)

    async def get_dataset(self, dataset_id: UUID) -> Optional[Dataset]:
        """Retrieves dataset metadata entity."""
        stmt = select(Dataset).where(Dataset.id == dataset_id)
        if self._is_async():
            result = await self.db.execute(stmt)
        else:
            result = self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_dataset_with_all_artifacts(
        self,
        dataset_id: UUID,
    ) -> Optional[
        Tuple[
            Dataset,
            List[DatasetMetric],
            List[DiagnosticFinding],
            List[RootCauseAnalysis],
            List[Recommendation],
        ]
    ]:
        """
        Retrieves dataset alongside all computed KPIs, findings, RCAs, and recommendations
        using eager relational joins.
        """
        dataset = await self.get_dataset(dataset_id)
        if not dataset:
            return None

        # 1. Fetch Metrics
        metrics_stmt = (
            select(DatasetMetric)
            .options(selectinload(DatasetMetric.metric_definition))
            .where(DatasetMetric.dataset_id == dataset_id)
        )

        # 2. Fetch Findings
        findings_stmt = (
            select(DiagnosticFinding)
            .where(DiagnosticFinding.dataset_id == dataset_id)
            .order_by(DiagnosticFinding.confidence_score.desc())
        )

        # 3. Fetch Root Causes
        rca_stmt = (
            select(RootCauseAnalysis)
            .options(
                selectinload(RootCauseAnalysis.primary_finding),
                selectinload(RootCauseAnalysis.root_cause_finding),
            )
            .where(RootCauseAnalysis.dataset_id == dataset_id)
            .order_by(RootCauseAnalysis.impact_score.desc())
        )

        # 4. Fetch Recommendations
        recs_stmt = (
            select(Recommendation)
            .where(Recommendation.dataset_id == dataset_id)
            .order_by(Recommendation.estimated_impact_score.desc())
        )

        if self._is_async():
            m_res = await self.db.execute(metrics_stmt)
            f_res = await self.db.execute(findings_stmt)
            r_res = await self.db.execute(rca_stmt)
            rec_res = await self.db.execute(recs_stmt)
        else:
            m_res = self.db.execute(metrics_stmt)
            f_res = self.db.execute(findings_stmt)
            r_res = self.db.execute(rca_stmt)
            rec_res = self.db.execute(recs_stmt)

        metrics = list(m_res.scalars().all())
        findings = list(f_res.scalars().all())
        root_causes = list(r_res.scalars().all())
        recommendations = list(rec_res.scalars().all())

        return dataset, metrics, findings, root_causes, recommendations
