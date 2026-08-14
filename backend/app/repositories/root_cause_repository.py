"""Repository layer providing database CRUD and relational queries for RootCauseAnalysis entities."""

from typing import Any, List, Optional, Union
from uuid import UUID
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session, selectinload

from app.core.constants import RelationshipStrength, RelationshipType
from app.models.root_cause_analysis import RootCauseAnalysis


class RootCauseRepository:
    """
    Data access repository for RootCauseAnalysis entities.
    
    Encapsulates all database operations, relational joins, eager loading,
    and bulk persistence for causal analytics.
    """

    def __init__(self, db: Union[AsyncSession, Session]):
        self.db = db

    def _is_async(self) -> bool:
        """Determines if the current database session is async."""
        return isinstance(self.db, AsyncSession)

    async def create(
        self,
        *,
        dataset_id: UUID,
        primary_finding_id: UUID,
        root_cause_finding_id: UUID,
        relationship_type: RelationshipType,
        relationship_strength: RelationshipStrength,
        confidence_score: float,
        impact_score: float,
        explanation: str,
        supporting_evidence: Optional[dict[str, Any]] = None,
    ) -> RootCauseAnalysis:
        """Persists a single RootCauseAnalysis entity and returns the refreshed instance."""
        rca = RootCauseAnalysis(
            dataset_id=dataset_id,
            primary_finding_id=primary_finding_id,
            root_cause_finding_id=root_cause_finding_id,
            relationship_type=relationship_type,
            relationship_strength=relationship_strength,
            confidence_score=confidence_score,
            impact_score=impact_score,
            explanation=explanation,
            supporting_evidence=supporting_evidence,
        )
        self.db.add(rca)

        if self._is_async():
            await self.db.flush()
            await self.db.refresh(rca)
        else:
            self.db.flush()
            self.db.refresh(rca)

        return rca

    async def create_many(
        self,
        analyses: List[RootCauseAnalysis],
    ) -> List[RootCauseAnalysis]:
        """Bulk persists a list of RootCauseAnalysis entities."""
        if not analyses:
            return []

        self.db.add_all(analyses)

        if self._is_async():
            await self.db.flush()
            for rca in analyses:
                await self.db.refresh(rca)
        else:
            self.db.flush()
            for rca in analyses:
                self.db.refresh(rca)

        return analyses

    async def get_by_id(
        self,
        analysis_id: UUID,
    ) -> Optional[RootCauseAnalysis]:
        """Retrieves a RootCauseAnalysis by ID with eager loading of findings."""
        stmt = (
            select(RootCauseAnalysis)
            .options(
                selectinload(RootCauseAnalysis.primary_finding),
                selectinload(RootCauseAnalysis.root_cause_finding),
            )
            .where(RootCauseAnalysis.id == analysis_id)
        )

        if self._is_async():
            result = await self.db.execute(stmt)
        else:
            result = self.db.execute(stmt)

        return result.scalar_one_or_none()

    async def get_by_dataset(
        self,
        dataset_id: UUID,
        *,
        limit: int = 100,
        offset: int = 0,
    ) -> List[RootCauseAnalysis]:
        """
        Retrieves paginated root cause analyses for a dataset ordered by
        (impact_score DESC, confidence_score DESC).
        """
        stmt = (
            select(RootCauseAnalysis)
            .options(
                selectinload(RootCauseAnalysis.primary_finding),
                selectinload(RootCauseAnalysis.root_cause_finding),
            )
            .where(RootCauseAnalysis.dataset_id == dataset_id)
            .order_by(
                RootCauseAnalysis.impact_score.desc(),
                RootCauseAnalysis.confidence_score.desc(),
                RootCauseAnalysis.created_at.desc(),
            )
            .limit(limit)
            .offset(offset)
        )

        if self._is_async():
            result = await self.db.execute(stmt)
        else:
            result = self.db.execute(stmt)

        return list(result.scalars().all())

    async def get_by_primary_finding(
        self,
        primary_finding_id: UUID,
    ) -> List[RootCauseAnalysis]:
        """Retrieves all root causes that triggered a specific primary finding."""
        stmt = (
            select(RootCauseAnalysis)
            .options(
                selectinload(RootCauseAnalysis.primary_finding),
                selectinload(RootCauseAnalysis.root_cause_finding),
            )
            .where(RootCauseAnalysis.primary_finding_id == primary_finding_id)
            .order_by(RootCauseAnalysis.impact_score.desc())
        )

        if self._is_async():
            result = await self.db.execute(stmt)
        else:
            result = self.db.execute(stmt)

        return list(result.scalars().all())

    async def get_by_root_cause_finding(
        self,
        root_cause_finding_id: UUID,
    ) -> List[RootCauseAnalysis]:
        """Retrieves all downstream impacts caused by a specific root cause finding."""
        stmt = (
            select(RootCauseAnalysis)
            .options(
                selectinload(RootCauseAnalysis.primary_finding),
                selectinload(RootCauseAnalysis.root_cause_finding),
            )
            .where(RootCauseAnalysis.root_cause_finding_id == root_cause_finding_id)
            .order_by(RootCauseAnalysis.impact_score.desc())
        )

        if self._is_async():
            result = await self.db.execute(stmt)
        else:
            result = self.db.execute(stmt)

        return list(result.scalars().all())

    async def count_by_dataset(self, dataset_id: UUID) -> int:
        """Counts total root cause analyses generated for a dataset."""
        stmt = (
            select(func.count())
            .select_from(RootCauseAnalysis)
            .where(RootCauseAnalysis.dataset_id == dataset_id)
        )

        if self._is_async():
            result = await self.db.execute(stmt)
        else:
            result = self.db.execute(stmt)

        return int(result.scalar_one() or 0)

    async def delete_by_dataset(self, dataset_id: UUID) -> int:
        """Deletes all root cause analyses for a dataset and returns rows deleted."""
        stmt = delete(RootCauseAnalysis).where(RootCauseAnalysis.dataset_id == dataset_id)

        if self._is_async():
            result = await self.db.execute(stmt)
        else:
            result = self.db.execute(stmt)

        return int(result.rowcount)
