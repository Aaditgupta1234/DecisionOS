"""Repository for managing ReportExport and ReportTemplate database records."""

import logging
from typing import List, Optional, Union
from uuid import UUID
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.reporting.constants import ExportFormat, ReportType
from app.reporting.models.report_export import ReportExport
from app.reporting.models.report_template import ReportTemplate

logger = logging.getLogger(__name__)


class ReportRepository:
    """
    Data access repository for ReportExport and ReportTemplate entities.
    Supports both AsyncSession and sync Session.
    """

    def __init__(self, db: Union[AsyncSession, Session]):
        self.db = db

    def _is_async(self) -> bool:
        return isinstance(self.db, AsyncSession)

    async def save(self, report: ReportExport) -> ReportExport:
        """Persists a new or updated ReportExport entity."""
        self.db.add(report)
        if self._is_async():
            await self.db.commit()
            await self.db.refresh(report)
        else:
            self.db.commit()
            self.db.refresh(report)
        return report

    async def get_by_id(
        self,
        report_id: UUID,
        organization_id: Optional[UUID] = None,
    ) -> Optional[ReportExport]:
        """Retrieves a report export by UUID with optional tenant isolation."""
        stmt = select(ReportExport).where(ReportExport.id == report_id)
        if organization_id:
            stmt = stmt.where(ReportExport.organization_id == organization_id)

        if self._is_async():
            result = await self.db.execute(stmt)
        else:
            result = self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_dataset(
        self,
        dataset_id: UUID,
        organization_id: Optional[UUID] = None,
        report_type: Optional[ReportType] = None,
        export_format: Optional[ExportFormat] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> List[ReportExport]:
        """Lists historical reports for a dataset ordered newest first."""
        stmt = (
            select(ReportExport)
            .where(ReportExport.dataset_id == dataset_id)
            .order_by(desc(ReportExport.created_at))
            .limit(limit)
            .offset(offset)
        )
        if organization_id:
            stmt = stmt.where(ReportExport.organization_id == organization_id)
        if report_type:
            stmt = stmt.where(ReportExport.report_type == report_type)
        if export_format:
            stmt = stmt.where(ReportExport.export_format == export_format)

        if self._is_async():
            result = await self.db.execute(stmt)
        else:
            result = self.db.execute(stmt)
        return list(result.scalars().all())

    async def count_by_dataset(
        self,
        dataset_id: UUID,
        organization_id: Optional[UUID] = None,
        report_type: Optional[ReportType] = None,
        export_format: Optional[ExportFormat] = None,
    ) -> int:
        """Counts total reports matching filter for a dataset."""
        stmt = (
            select(func.count())
            .select_from(ReportExport)
            .where(ReportExport.dataset_id == dataset_id)
        )
        if organization_id:
            stmt = stmt.where(ReportExport.organization_id == organization_id)
        if report_type:
            stmt = stmt.where(ReportExport.report_type == report_type)
        if export_format:
            stmt = stmt.where(ReportExport.export_format == export_format)

        if self._is_async():
            result = await self.db.execute(stmt)
        else:
            result = self.db.execute(stmt)
        return int(result.scalar_one() or 0)

    async def delete(self, report_id: UUID) -> bool:
        """Deletes a report export record from database."""
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

    # -----------------------------------------------------------------------
    # ReportTemplate Operations
    # -----------------------------------------------------------------------

    async def get_default_template(self, report_type: ReportType) -> Optional[ReportTemplate]:
        """Retrieves the default layout template for a report type."""
        stmt = (
            select(ReportTemplate)
            .where(
                ReportTemplate.report_type == report_type,
                ReportTemplate.is_default == True,
            )
            .limit(1)
        )
        if self._is_async():
            result = await self.db.execute(stmt)
        else:
            result = self.db.execute(stmt)
        return result.scalar_one_or_none()
