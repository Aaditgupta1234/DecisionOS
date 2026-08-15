"""Repository layer for persisting and retrieving AI Narrative Reports."""

import logging
from typing import List, Optional, Union
from uuid import UUID
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.models.narrative_report import NarrativeReport

logger = logging.getLogger(__name__)


class NarrativeRepository:
    """
    Data access repository for persisting, retrieving, and managing AI Narrative Reports.
    Supports both AsyncSession and sync Session.
    """

    def __init__(self, db: Union[AsyncSession, Session]):
        self.db = db

    def _is_async(self) -> bool:
        return isinstance(self.db, AsyncSession)

    async def save(self, report: NarrativeReport) -> NarrativeReport:
        """Persists a new or updated NarrativeReport entity."""
        self.db.add(report)
        if self._is_async():
            await self.db.commit()
            await self.db.refresh(report)
        else:
            self.db.commit()
            self.db.refresh(report)
        return report

    async def get_by_id(self, report_id: UUID) -> Optional[NarrativeReport]:
        """Retrieves a specific narrative report by its primary key UUID."""
        stmt = select(NarrativeReport).where(NarrativeReport.id == report_id)
        if self._is_async():
            result = await self.db.execute(stmt)
        else:
            result = self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_latest_by_dataset(self, dataset_id: UUID) -> Optional[NarrativeReport]:
        """Retrieves the most recent narrative report for a dataset."""
        stmt = (
            select(NarrativeReport)
            .where(NarrativeReport.dataset_id == dataset_id)
            .order_by(desc(NarrativeReport.created_at))
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
    ) -> List[NarrativeReport]:
        """Retrieves paginated history of narrative reports for a dataset."""
        stmt = (
            select(NarrativeReport)
            .where(NarrativeReport.dataset_id == dataset_id)
            .order_by(desc(NarrativeReport.created_at))
            .limit(limit)
            .offset(offset)
        )
        if self._is_async():
            result = await self.db.execute(stmt)
        else:
            result = self.db.execute(stmt)
        return list(result.scalars().all())

    async def delete(self, report_id: UUID) -> bool:
        """Deletes a narrative report by ID."""
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
