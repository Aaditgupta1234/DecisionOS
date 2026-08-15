"""FastAPI API Router for Phase 9.2 AI Narrative Engine."""

import logging
from typing import Any, List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_active_user
from app.database.session import get_db
from app.models.user import User
from app.narratives.schemas.narrative_schema import (
    DatasetNarrativePackageResponse,
    ExecutiveNarrativeResponse,
    ForecastNarrativeRequest,
    ForecastNarrativeResponse,
    KPINarrativeResponse,
    NarrativeGenerateRequest,
    NarrativeReportHistoryItem,
    RecommendationNarrativeResponse,
    RootCauseNarrativeResponse,
    ScenarioNarrativeRequest,
    ScenarioNarrativeResponse,
)
from app.narratives.services.narrative_engine_service import NarrativeEngineService
from app.schemas.base import SuccessResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/datasets/{dataset_id}/narratives/executive-summary",
    response_model=SuccessResponse[ExecutiveNarrativeResponse],
    status_code=status.HTTP_200_OK,
    summary="Generate Executive Decision Narrative",
)
async def generate_executive_narrative(
    dataset_id: UUID,
    request_data: Optional[NarrativeGenerateRequest] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Synthesizes a boardroom-ready executive decision narrative from deterministic intelligence artifacts.
    """
    service = NarrativeEngineService(db)
    result = await service.get_executive_narrative(dataset_id, req=request_data)
    return SuccessResponse(
        message="Executive narrative synthesized successfully.",
        data=result,
    )


@router.post(
    "/datasets/{dataset_id}/narratives/kpis",
    response_model=SuccessResponse[KPINarrativeResponse],
    status_code=status.HTTP_200_OK,
    summary="Generate KPI Performance Narrative",
)
async def generate_kpi_narrative(
    dataset_id: UUID,
    request_data: Optional[NarrativeGenerateRequest] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Synthesizes a specialized KPI performance narrative explaining metric movements and domain insights.
    """
    service = NarrativeEngineService(db)
    result = await service.get_kpi_narrative(dataset_id, req=request_data)
    return SuccessResponse(
        message="KPI performance narrative synthesized successfully.",
        data=result,
    )


@router.post(
    "/datasets/{dataset_id}/narratives/root-causes",
    response_model=SuccessResponse[RootCauseNarrativeResponse],
    status_code=status.HTTP_200_OK,
    summary="Generate Root Cause Analysis Narrative",
)
async def generate_root_cause_narrative(
    dataset_id: UUID,
    request_data: Optional[NarrativeGenerateRequest] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Synthesizes a causal DAG explanation narrative explaining primary drivers and failure mechanisms.
    """
    service = NarrativeEngineService(db)
    result = await service.get_root_cause_narrative(dataset_id, req=request_data)
    return SuccessResponse(
        message="Root cause analysis narrative synthesized successfully.",
        data=result,
    )


@router.post(
    "/datasets/{dataset_id}/narratives/recommendations",
    response_model=SuccessResponse[RecommendationNarrativeResponse],
    status_code=status.HTTP_200_OK,
    summary="Generate Strategic Recommendations Narrative",
)
async def generate_recommendation_narrative(
    dataset_id: UUID,
    request_data: Optional[NarrativeGenerateRequest] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Synthesizes strategic recommendations narrative prioritizing actions and explaining projected ROI.
    """
    service = NarrativeEngineService(db)
    result = await service.get_recommendation_narrative(dataset_id, req=request_data)
    return SuccessResponse(
        message="Strategic recommendations narrative synthesized successfully.",
        data=result,
    )


@router.post(
    "/datasets/{dataset_id}/narratives/forecasts",
    response_model=SuccessResponse[ForecastNarrativeResponse],
    status_code=status.HTTP_200_OK,
    summary="Generate Time-Series Forecast Narrative",
)
async def generate_forecast_narrative(
    dataset_id: UUID,
    request_data: Optional[ForecastNarrativeRequest] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Synthesizes forecasting narrative explaining future projections, trend directions, and risk warnings.
    """
    service = NarrativeEngineService(db)
    result = await service.get_forecast_narrative(dataset_id, req=request_data)
    return SuccessResponse(
        message="Forecasting narrative synthesized successfully.",
        data=result,
    )


@router.post(
    "/datasets/{dataset_id}/narratives/scenarios",
    response_model=SuccessResponse[ScenarioNarrativeResponse],
    status_code=status.HTTP_200_OK,
    summary="Generate Scenario Simulation Narrative",
)
async def generate_scenario_narrative(
    dataset_id: UUID,
    request_data: Optional[ScenarioNarrativeRequest] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Synthesizes scenario simulation narrative detailing delta comparisons and boardroom implications.
    """
    service = NarrativeEngineService(db)
    result = await service.get_scenario_narrative(dataset_id, req=request_data)
    return SuccessResponse(
        message="Scenario simulation narrative synthesized successfully.",
        data=result,
    )


@router.post(
    "/datasets/{dataset_id}/narratives/full-package",
    response_model=SuccessResponse[DatasetNarrativePackageResponse],
    status_code=status.HTTP_200_OK,
    summary="Generate and Persist Consolidated Narrative Package",
)
async def generate_and_persist_full_package(
    dataset_id: UUID,
    request_data: Optional[NarrativeGenerateRequest] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Concurrently synthesizes all narrative perspectives and persists the resulting NarrativeReport to the database.
    """
    service = NarrativeEngineService(db)
    result = await service.generate_and_persist_full_package(dataset_id, req=request_data)
    return SuccessResponse(
        message="Consolidated narrative package generated and persisted successfully.",
        data=result,
    )


@router.get(
    "/datasets/{dataset_id}/narratives/latest",
    response_model=SuccessResponse[Optional[DatasetNarrativePackageResponse]],
    status_code=status.HTTP_200_OK,
    summary="Get Latest Persisted Narrative Report",
)
async def get_latest_persisted_report(
    dataset_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieves the most recently generated and persisted narrative report for a dataset.
    """
    service = NarrativeEngineService(db)
    result = await service.get_latest_persisted_report(dataset_id)
    if result is None:
        return SuccessResponse(
            message="No persisted narrative report found for this dataset.",
            data=None,
        )
    return SuccessResponse(
        message="Retrieved latest persisted narrative report.",
        data=result,
    )


@router.get(
    "/datasets/{dataset_id}/narratives/history",
    response_model=SuccessResponse[List[NarrativeReportHistoryItem]],
    status_code=status.HTTP_200_OK,
    summary="List Persisted Narrative Report History",
)
async def list_persisted_reports_history(
    dataset_id: UUID,
    limit: int = Query(10, ge=1, le=100, description="Max items to retrieve"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieves the paginated revision history of narrative reports persisted for this dataset.
    """
    service = NarrativeEngineService(db)
    results = await service.list_persisted_reports(dataset_id, limit=limit, offset=offset)
    return SuccessResponse(
        message=f"Retrieved {len(results)} historical narrative report revisions.",
        data=results,
    )
