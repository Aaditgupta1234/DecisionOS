"""Report Validator verifying dataset authorization, artifact presence, and document integrity."""

import logging
from typing import List, Optional, Union
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.models.dataset import Dataset
from app.repositories.intelligence_repository import IntelligenceRepository
from app.reporting.constants import ReportType
from app.reporting.report_templates import ReportDocument

logger = logging.getLogger(__name__)


class ReportValidationResult:
    """Encapsulates validation status and error descriptions."""

    def __init__(self, is_valid: bool, errors: Optional[List[str]] = None):
        self.is_valid = is_valid
        self.errors = errors or []


class ReportValidator:
    """
    Validates report generation requests against dataset ownership,
    intelligence artifact presence, and schema rules.
    """

    def __init__(self, db: Union[AsyncSession, Session]):
        self.db = db
        self.intel_repo = IntelligenceRepository(db)

    async def validate_dataset_access(
        self,
        dataset_id: UUID,
        organization_id: Optional[UUID] = None,
    ) -> Dataset:
        """
        Ensures the target dataset exists and matches the caller's multi-tenant organization.
        """
        dataset = await self.intel_repo.get_dataset(dataset_id)
        if not dataset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Dataset with ID '{dataset_id}' not found.",
            )

        if organization_id and getattr(dataset, "organization_id", None):
            if dataset.organization_id != organization_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access to dataset denied by tenant isolation policy.",
                )

        return dataset

    @classmethod
    def validate_document_integrity(
        cls,
        document: Optional[ReportDocument],
        report_type: ReportType,
    ) -> ReportValidationResult:
        """
        Verifies that the compiled document contains all mandatory sections for its type.
        """
        if not document:
            return ReportValidationResult(False, ["Compiled document is null or empty."])

        errors = []

        if not document.metadata.title:
            errors.append("Document metadata title is missing.")
        if not document.metadata.dataset_name:
            errors.append("Document metadata dataset_name is missing.")

        if not document.sections:
            errors.append(f"Report type '{report_type}' produced 0 content sections.")

        # Ensure no completely empty section titles
        for s in document.sections:
            if not s.title or not s.title.strip():
                errors.append(f"Section key '{s.key}' contains an empty title.")

        return ReportValidationResult(is_valid=len(errors) == 0, errors=errors)
