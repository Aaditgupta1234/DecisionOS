"""ReportExportService orchestrating artifact assembly, generation, persistence, and downloads."""

import logging
import os
import time
from pathlib import Path
from typing import List, Optional, Union
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.reporting.constants import (
    DEFAULT_STORAGE_DIR,
    REPORT_TEMPLATE_VERSION,
    ExportFormat,
    ReportStatus,
    ReportType,
)
from app.reporting.html_renderer import HTMLRenderer
from app.reporting.models.report_export import ReportExport
from app.reporting.pdf_generator import PDFGenerator
from app.reporting.report_builder import ReportBuilder
from app.reporting.report_validator import ReportValidator
from app.reporting.repositories.report_repository import ReportRepository
from app.reporting.schemas.responses import (
    ReportDetailResponse,
    ReportExportResponse,
)

logger = logging.getLogger(__name__)


class ReportExportService:
    """
    Coordinates dataset validation, intelligence retrieval, document assembly,
    PDF/HTML rendering, filesystem storage, and database persistence.
    """

    def __init__(
        self,
        db: Union[AsyncSession, Session],
        storage_dir: Optional[str] = None,
    ):
        self.db = db
        self.repo = ReportRepository(db)
        self.validator = ReportValidator(db)
        self.builder = ReportBuilder(db)
        self.storage_dir = Path(storage_dir or DEFAULT_STORAGE_DIR)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    async def generate_report(
        self,
        dataset_id: UUID,
        report_type: ReportType = ReportType.FULL_BOARD_PACKAGE,
        export_format: ExportFormat = ExportFormat.PDF,
        title: Optional[str] = None,
        company_name: Optional[str] = None,
        include_raw_evidence: bool = True,
        user_id: Optional[UUID] = None,
        organization_id: Optional[UUID] = None,
    ) -> ReportExportResponse:
        """
        Validates dataset access, builds ReportDocument, generates output binary,
        saves to disk, and records persistence entity.
        """
        start_time = time.perf_counter()

        # 1. Tenant & Dataset Access Verification
        dataset = await self.validator.validate_dataset_access(
            dataset_id=dataset_id,
            organization_id=organization_id,
        )

        # 2. Build Structured Document Object
        document = await self.builder.build(
            dataset_id=dataset_id,
            report_type=report_type,
            custom_title=title,
            company_name=company_name,
            include_raw_evidence=include_raw_evidence,
        )

        val_res = ReportValidator.validate_document_integrity(document, report_type)
        if not val_res.is_valid:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Report validation failed: {'; '.join(val_res.errors)}",
            )

        # 3. Create Persisted Record (Pending)
        doc_title = document.metadata.title
        report_record = ReportExport(
            dataset_id=dataset_id,
            organization_id=organization_id,
            report_type=report_type,
            export_format=export_format,
            status=ReportStatus.PENDING,
            title=doc_title,
            template_version=REPORT_TEMPLATE_VERSION,
            generated_by=user_id,
        )
        report_record = await self.repo.save(report_record)

        # 4. Storage Path & Generation Execution
        dataset_folder = self.storage_dir / str(dataset_id)
        dataset_folder.mkdir(parents=True, exist_ok=True)

        ext = "pdf" if export_format == ExportFormat.PDF else "html"
        file_name = f"{report_record.id}_{report_type.value.lower()}.{ext}"
        target_path = dataset_folder / file_name

        try:
            if export_format == ExportFormat.PDF:
                raw_bytes = PDFGenerator.generate(document, output_path=str(target_path))
                file_size = len(raw_bytes)
            else:
                raw_html = HTMLRenderer.render(document, output_path=str(target_path))
                file_size = len(raw_html.encode("utf-8"))

            latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

            # 5. Update Record Status to COMPLETED
            report_record.status = ReportStatus.COMPLETED
            report_record.storage_path = str(target_path)
            report_record.file_size_bytes = file_size
            report_record.generation_time_ms = latency_ms
            report_record.report_metadata = {
                "business_health_score": document.metadata.business_health_score,
                "business_health_status": document.metadata.business_health_status,
                "sections_count": len(document.sections),
                "evidence_count": len(document.evidence_references),
            }
            report_record = await self.repo.save(report_record)

            return self._to_export_response(report_record)

        except Exception as e:
            logger.exception(f"Report generation failed for record '{report_record.id}': {e}")
            report_record.status = ReportStatus.FAILED
            report_record.error_message = str(e)
            await self.repo.save(report_record)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Report export generation failed: {str(e)}",
            )

    async def get_report_details(
        self,
        report_id: UUID,
        organization_id: Optional[UUID] = None,
    ) -> ReportDetailResponse:
        """Retrieves complete metadata for a report export."""
        report = await self.repo.get_by_id(report_id, organization_id=organization_id)
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Report export '{report_id}' not found.",
            )
        return ReportDetailResponse(
            id=report.id,
            dataset_id=report.dataset_id,
            organization_id=report.organization_id,
            report_type=report.report_type,
            export_format=report.export_format,
            status=report.status,
            title=report.title,
            template_version=report.template_version,
            generated_by=report.generated_by,
            generated_at=report.generated_at,
            generation_time_ms=report.generation_time_ms,
            file_size_bytes=report.file_size_bytes,
            download_url=f"/api/v1/reports/download/{report.id}",
            created_at=report.created_at,
            report_metadata=report.report_metadata or {},
            error_message=report.error_message,
        )

    async def list_reports(
        self,
        dataset_id: UUID,
        organization_id: Optional[UUID] = None,
        report_type: Optional[ReportType] = None,
        export_format: Optional[ExportFormat] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> List[ReportExportResponse]:
        """Lists historical reports for a dataset with pagination."""
        reports = await self.repo.list_by_dataset(
            dataset_id=dataset_id,
            organization_id=organization_id,
            report_type=report_type,
            export_format=export_format,
            limit=limit,
            offset=offset,
        )
        return [self._to_export_response(r) for r in reports]

    async def count_reports(
        self,
        dataset_id: UUID,
        organization_id: Optional[UUID] = None,
        report_type: Optional[ReportType] = None,
        export_format: Optional[ExportFormat] = None,
    ) -> int:
        """Counts total reports matching filter criteria."""
        return await self.repo.count_by_dataset(
            dataset_id=dataset_id,
            organization_id=organization_id,
            report_type=report_type,
            export_format=export_format,
        )

    async def delete_report(
        self,
        report_id: UUID,
        organization_id: Optional[UUID] = None,
    ) -> bool:
        """Deletes a report entity and removes the stored document file."""
        report = await self.repo.get_by_id(report_id, organization_id=organization_id)
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Report export '{report_id}' not found.",
            )

        if report.storage_path and os.path.exists(report.storage_path):
            try:
                os.remove(report.storage_path)
            except Exception as e:
                logger.warning(f"Failed to delete report file '{report.storage_path}': {e}")

        return await self.repo.delete(report_id)

    async def get_report_file_path(
        self,
        report_id: UUID,
        organization_id: Optional[UUID] = None,
    ) -> str:
        """Resolves verified file path for download streaming."""
        report = await self.repo.get_by_id(report_id, organization_id=organization_id)
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Report export '{report_id}' not found.",
            )
        if report.status != ReportStatus.COMPLETED or not report.storage_path or not os.path.exists(report.storage_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report export file is unavailable or generation failed.",
            )
        return report.storage_path

    def _to_export_response(self, record: ReportExport) -> ReportExportResponse:
        return ReportExportResponse(
            id=record.id,
            dataset_id=record.dataset_id,
            organization_id=record.organization_id,
            report_type=record.report_type,
            export_format=record.export_format,
            status=record.status,
            title=record.title,
            template_version=record.template_version,
            generated_by=record.generated_by,
            generated_at=record.generated_at,
            generation_time_ms=record.generation_time_ms,
            file_size_bytes=record.file_size_bytes,
            download_url=f"/api/v1/reports/download/{record.id}",
            created_at=record.created_at,
        )
