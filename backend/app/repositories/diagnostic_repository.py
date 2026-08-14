"""Repository layer providing pure database CRUD and aggregation access for DiagnosticFindings."""

from typing import Any, Union
from uuid import UUID
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.core.constants import FindingSeverity, FindingType
from app.models.diagnostic_finding import DiagnosticFinding


class DiagnosticRepository:
    """
    Data access repository for DiagnosticFinding entities.
    
    Encapsulates all database queries, bulk persistence, filtered lookups,
    and aggregations while remaining free of business logic.
    """

    def __init__(self, db: Union[AsyncSession, Session]):
        self.db = db

    def _is_async(self) -> bool:
        """Determines if the session is an AsyncSession instance."""
        return isinstance(self.db, AsyncSession)

    async def create(
        self,
        *,
        dataset_id: UUID,
        finding_type: FindingType,
        severity: FindingSeverity,
        title: str,
        description: str,
        business_impact: str,
        metric_key: str | None = None,
        confidence_score: float = 1.0,
        supporting_data: dict[str, Any] | None = None,
    ) -> DiagnosticFinding:
        """Persists a single diagnostic finding and returns the refreshed entity."""
        finding = DiagnosticFinding(
            dataset_id=dataset_id,
            finding_type=finding_type,
            severity=severity,
            title=title,
            description=description,
            business_impact=business_impact,
            metric_key=metric_key,
            confidence_score=confidence_score,
            supporting_data=supporting_data,
        )
        self.db.add(finding)

        if self._is_async():
            await self.db.flush()
            await self.db.refresh(finding)
        else:
            self.db.flush()
            self.db.refresh(finding)

        return finding

    async def create_many(
        self,
        findings: list[DiagnosticFinding],
    ) -> list[DiagnosticFinding]:
        """Bulk persists a collection of diagnostic findings and refreshes each entity."""
        if not findings:
            return []

        self.db.add_all(findings)

        if self._is_async():
            await self.db.flush()
            for finding in findings:
                await self.db.refresh(finding)
        else:
            self.db.flush()
            for finding in findings:
                self.db.refresh(finding)

        return findings

    async def get_by_id(
        self,
        finding_id: UUID,
    ) -> DiagnosticFinding | None:
        """Retrieves a diagnostic finding by its primary key."""
        stmt = select(DiagnosticFinding).where(DiagnosticFinding.id == finding_id)

        if self._is_async():
            result = await self.db.execute(stmt)
        else:
            result = self.db.execute(stmt)

        return result.scalar_one_or_none()

    async def get_dataset_findings(
        self,
        dataset_id: UUID,
        *,
        limit: int = 100,
        offset: int = 0,
    ) -> list[DiagnosticFinding]:
        """
        Retrieves paginated findings for a dataset ordered deterministically by
        (generated_at DESC, id DESC).
        """
        if limit < 1:
            raise ValueError("limit must be >= 1")
        if offset < 0:
            raise ValueError("offset must be >= 0")

        stmt = (
            select(DiagnosticFinding)
            .where(DiagnosticFinding.dataset_id == dataset_id)
            .order_by(
                DiagnosticFinding.generated_at.desc(),
                DiagnosticFinding.id.desc(),
            )
            .limit(limit)
            .offset(offset)
        )

        if self._is_async():
            result = await self.db.execute(stmt)
        else:
            result = self.db.execute(stmt)

        return list(result.scalars().all())

    async def get_findings_by_severity(
        self,
        dataset_id: UUID,
        severity: FindingSeverity,
    ) -> list[DiagnosticFinding]:
        """Retrieves dataset findings filtered by severity level using composite index."""
        stmt = (
            select(DiagnosticFinding)
            .where(
                DiagnosticFinding.dataset_id == dataset_id,
                DiagnosticFinding.severity == severity,
            )
            .order_by(
                DiagnosticFinding.generated_at.desc(),
                DiagnosticFinding.id.desc(),
            )
        )

        if self._is_async():
            result = await self.db.execute(stmt)
        else:
            result = self.db.execute(stmt)

        return list(result.scalars().all())

    async def get_findings_by_type(
        self,
        dataset_id: UUID,
        finding_type: FindingType,
    ) -> list[DiagnosticFinding]:
        """Retrieves dataset findings filtered by finding anomaly type."""
        stmt = (
            select(DiagnosticFinding)
            .where(
                DiagnosticFinding.dataset_id == dataset_id,
                DiagnosticFinding.finding_type == finding_type,
            )
            .order_by(
                DiagnosticFinding.generated_at.desc(),
                DiagnosticFinding.id.desc(),
            )
        )

        if self._is_async():
            result = await self.db.execute(stmt)
        else:
            result = self.db.execute(stmt)

        return list(result.scalars().all())

    async def get_total_findings(
        self,
        dataset_id: UUID,
    ) -> int:
        """Executes an efficient count query returning total findings for a dataset."""
        stmt = (
            select(func.count())
            .select_from(DiagnosticFinding)
            .where(DiagnosticFinding.dataset_id == dataset_id)
        )

        if self._is_async():
            result = await self.db.execute(stmt)
        else:
            result = self.db.execute(stmt)

        count_val = result.scalar_one()
        return int(count_val or 0)

    async def get_severity_counts(
        self,
        dataset_id: UUID,
    ) -> dict[str, int]:
        """
        Executes a GROUP BY severity aggregation query and returns a dictionary
        guaranteed to contain entries for all severity tiers.
        """
        counts: dict[str, int] = {
            FindingSeverity.CRITICAL.value: 0,
            FindingSeverity.HIGH.value: 0,
            FindingSeverity.MEDIUM.value: 0,
            FindingSeverity.LOW.value: 0,
        }

        stmt = (
            select(DiagnosticFinding.severity, func.count())
            .where(DiagnosticFinding.dataset_id == dataset_id)
            .group_by(DiagnosticFinding.severity)
        )

        if self._is_async():
            result = await self.db.execute(stmt)
        else:
            result = self.db.execute(stmt)

        for row in result.all():
            sev, cnt = row[0], row[1]
            sev_key = sev.value if hasattr(sev, "value") else str(sev)
            counts[sev_key] = int(cnt)

        return counts

    async def delete_dataset_findings(
        self,
        dataset_id: UUID,
    ) -> int:
        """Deletes all findings for a dataset via a direct SQL DELETE statement and returns rows deleted."""
        stmt = delete(DiagnosticFinding).where(DiagnosticFinding.dataset_id == dataset_id)

        if self._is_async():
            result = await self.db.execute(stmt)
        else:
            result = self.db.execute(stmt)

        return int(result.rowcount)
