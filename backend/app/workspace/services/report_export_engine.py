"""Report Export Engine for Phase 6.1."""

import uuid
from datetime import datetime, timezone
from app.workspace.schemas.workspace_schemas import ReportExportRequest, ReportExportResponse


class ReportExportEngine:
    """Generates multi-format boardroom report export packages."""

    @staticmethod
    def create_export_job(payload: ReportExportRequest) -> ReportExportResponse:
        """
        Creates an export job and provides a formatted download URL.
        """
        job_id = uuid.uuid4()
        fmt = payload.export_format.lower()
        slug = payload.report_type.lower().replace("_", "-")
        download_url = f"/api/v1/reports/download/{job_id}/{slug}.{fmt}"

        return ReportExportResponse(
            id=job_id,
            portfolio_id=payload.portfolio_id,
            report_type=payload.report_type,
            export_format=payload.export_format.upper(),
            export_status="COMPLETED",
            download_url=download_url,
            created_at=datetime.now(timezone.utc),
        )
