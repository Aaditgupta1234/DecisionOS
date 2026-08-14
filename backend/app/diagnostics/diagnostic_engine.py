"""Diagnostic Engine Core orchestrating analyzers, finding persistence, lifecycle state, and idempotent execution."""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Union
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.core.constants import DatasetStatus, DiagnosticGenerationStatus
from app.diagnostics.analyzer_registry import AnalyzerRegistry
from app.diagnostics.base_analyzer import BaseDiagnosticAnalyzer
from app.models.dataset import Dataset
from app.models.dataset_metric import DatasetMetric
from app.models.diagnostic_finding import DiagnosticFinding
from app.repositories.diagnostic_repository import DiagnosticRepository


@dataclass(slots=True)
class DiagnosticEngineResult:
    """Internal result metadata returned upon completing a diagnostic generation cycle."""

    dataset_id: UUID
    findings_generated: int
    status: DiagnosticGenerationStatus
    generated_at: datetime | None = None
    error: str | None = None


class DiagnosticEngine:
    """
    Central orchestration engine for the DecisionOS Root Cause and Diagnostic Intelligence subsystem.
    
    Coordinates dataset readiness verification, metric retrieval, analyzer pipeline execution,
    finding persistence, idempotent cleanup, and dataset status management.
    """

    def __init__(
        self,
        db: Union[AsyncSession, Session],
        analyzers: list[BaseDiagnosticAnalyzer] | None = None,
    ):
        self.db = db
        self.repo = DiagnosticRepository(db)
        if analyzers is not None:
            self.analyzers = list(analyzers)
        else:
            self.analyzers = list(AnalyzerRegistry.get_default_analyzers())

    def _is_async(self) -> bool:
        """Determines if the database session is an AsyncSession instance."""
        return isinstance(self.db, AsyncSession)

    def register_analyzer(self, analyzer: BaseDiagnosticAnalyzer) -> None:
        """Registers a diagnostic analyzer in the engine, preventing duplicate entries."""
        if analyzer not in self.analyzers:
            self.analyzers.append(analyzer)

    async def validate_dataset_ready(self, dataset: Dataset) -> None:
        """
        Validates that the dataset has reached the READY state before diagnostics can be run.
        
        Raises:
            ValueError: If the dataset is not in READY status.
        """
        if dataset.status != DatasetStatus.READY:
            raise ValueError(
                f"Dataset must be in READY status before diagnostics can be generated (current status: {dataset.status.value})."
            )

    async def load_dataset_metrics(self, dataset_id: UUID) -> list[DatasetMetric]:
        """Loads all computed DatasetMetric records for the dataset ordered by metric_key ascending."""
        stmt = (
            select(DatasetMetric)
            .where(DatasetMetric.dataset_id == dataset_id)
            .order_by(DatasetMetric.metric_key.asc())
        )

        if self._is_async():
            result = await self.db.execute(stmt)
        else:
            result = self.db.execute(stmt)

        return list(result.scalars().all())

    async def run_analyzers(
        self,
        dataset: Dataset,
        metrics: list[DatasetMetric],
    ) -> list[DiagnosticFinding]:
        """
        Executes all registered diagnostic analyzers sequentially and aggregates their findings.
        
        Failures in any analyzer are allowed to propagate upward.
        """
        all_findings: list[DiagnosticFinding] = []

        for analyzer in self.analyzers:
            findings = await analyzer.analyze(dataset, metrics)
            if findings:
                all_findings.extend(findings)

        return all_findings

    async def generate(self, dataset: Dataset) -> DiagnosticEngineResult:
        """
        Main orchestration pipeline for diagnostic generation:
        1. Validates dataset readiness (status == READY).
        2. Loads computed dataset metrics.
        3. Deletes existing findings for idempotent regeneration.
        4. Runs all registered diagnostic analyzers.
        5. Persists newly generated findings via DiagnosticRepository.
        6. Updates dataset diagnostic generation status to GENERATED.
        7. Returns DiagnosticEngineResult.
        
        On failure, sets dataset diagnostic status to FAILED, persists error text, and re-raises.
        """
        try:
            # Step 1: Validate dataset readiness
            await self.validate_dataset_ready(dataset)

            # Step 2: Load metrics
            metrics = await self.load_dataset_metrics(dataset.id)

            # Step 3: Delete previous findings for idempotent regeneration
            await self.repo.delete_dataset_findings(dataset.id)

            # Step 4: Run registered analyzers
            findings = await self.run_analyzers(dataset, metrics)

            # Step 5: Persist findings if any were generated
            if findings:
                # Ensure each finding is associated with this dataset
                for finding in findings:
                    finding.dataset_id = dataset.id
                await self.repo.create_many(findings)

            # Step 6: Update dataset status to GENERATED
            now = datetime.now(timezone.utc)
            dataset.diagnostics_generation_status = DiagnosticGenerationStatus.GENERATED
            dataset.diagnostics_generated_at = now
            dataset.diagnostics_generation_error = None

            if self._is_async():
                await self.db.commit()
                await self.db.refresh(dataset)
            else:
                self.db.commit()
                self.db.refresh(dataset)

            # Step 7: Return engine result
            return DiagnosticEngineResult(
                dataset_id=dataset.id,
                findings_generated=len(findings),
                status=DiagnosticGenerationStatus.GENERATED,
                generated_at=now,
                error=None,
            )

        except Exception as e:
            # Failure handling: record error state on dataset and re-raise
            dataset.diagnostics_generation_status = DiagnosticGenerationStatus.FAILED
            dataset.diagnostics_generation_error = str(e)

            if self._is_async():
                await self.db.commit()
            else:
                self.db.commit()

            raise e
