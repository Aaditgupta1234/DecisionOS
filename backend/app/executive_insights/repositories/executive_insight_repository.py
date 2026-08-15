"""Repository layer for persisting and retrieving Executive Insight Reports."""

import logging
from typing import List, Optional, Union
from uuid import UUID
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.executive_insights.models.executive_insight_report import ExecutiveInsightReport

logger = logging.getLogger(__name__)


class ExecutiveInsightRepository:
    """
    Data access repository for persisting, querying, and managing ExecutiveInsightReport records.
    Seamlessly supports both AsyncSession and synchronous Session.
    """

    def __init__(self, db: Union[AsyncSession, Session]):
        self.db = db

    def _is_async(self) -> bool:
        return isinstance(self.db, AsyncSession)

    async def save(self, report: ExecutiveInsightReport) -> ExecutiveInsightReport:
        """Persists a new or updated ExecutiveInsightReport entity."""
        self.db.add(report)
        if self._is_async():
            await self.db.commit()
            await self.db.refresh(report)
        else:
            self.db.commit()
            self.db.refresh(report)
        return report

    async def get_by_id(self, report_id: UUID) -> Optional[ExecutiveInsightReport]:
        """Retrieves a specific executive insight report by UUID."""
        stmt = select(ExecutiveInsightReport).where(ExecutiveInsightReport.id == report_id)
        if self._is_async():
            result = await self.db.execute(stmt)
        else:
            result = self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_latest_by_dataset(self, dataset_id: UUID) -> Optional[ExecutiveInsightReport]:
        """Retrieves the most recent executive insight report for a dataset."""
        stmt = (
            select(ExecutiveInsightReport)
            .where(ExecutiveInsightReport.dataset_id == dataset_id)
            .order_by(desc(ExecutiveInsightReport.created_at))
            .limit(1)
        )
        if self._is_async():
            result = await self.db.execute(stmt)
        else:
            result = self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_dataset(
        self,
        dataset_id: UUID,
        limit: int = 10,
        offset: int = 0,
    ) -> List[ExecutiveInsightReport]:
        """Retrieves paginated history of executive insight reports for a dataset."""
        stmt = (
            select(ExecutiveInsightReport)
            .where(ExecutiveInsightReport.dataset_id == dataset_id)
            .order_by(desc(ExecutiveInsightReport.created_at))
            .limit(limit)
            .offset(offset)
        )
        if self._is_async():
            result = await self.db.execute(stmt)
        else:
            result = self.db.execute(stmt)
        return list(result.scalars().all())

    async def delete(self, report_id: UUID) -> bool:
        """Deletes an executive insight report by ID."""
        report = await self.get_by_id(report_id)
        if not report:
            return False
        if self._is_async():
            await self.db.delete(report)
            await self.db.commit()
        else:
            self.db.delete(report)
            self.db.commit()
        return True
