"""FastAPI router endpoints for Phase 6.2 AI Strategy Planner."""

from typing import Any, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_active_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.base import SuccessResponse
from app.strategy_planner.schemas.strategy_schema import (
    StrategyPlanCreate,
    StrategyPlanHistoryResponse,
    StrategyPlanResponse,
    StrategyPlanStatusUpdate,
)
from app.strategy_planner.services.strategy_planner_service import StrategyPlannerService

router = APIRouter()


# ---------------------------------------------------------------------------
# 1. Dataset-Scoped Strategy Plan Endpoints
# ---------------------------------------------------------------------------

@router.get(
    "/datasets/{dataset_id}/strategy-plan",
    response_model=SuccessResponse[StrategyPlanResponse],
    status_code=status.HTTP_200_OK,
    summary="Get or Generate Latest Strategic Execution Plan",
)
async def get_or_generate_strategy_plan(
    dataset_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieves the latest cached strategy plan or triggers generation if none exists.
    """
    service = StrategyPlannerService(db)
    plan = await service.get_or_generate_plan(dataset_id=dataset_id)
    return SuccessResponse(
        message="Strategic execution plan retrieved successfully.",
        data=plan,
    )


@router.post(
    "/datasets/{dataset_id}/strategy-plan/regenerate",
    response_model=SuccessResponse[StrategyPlanResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Regenerate Strategic Execution Plan",
)
async def regenerate_strategy_plan(
    dataset_id: UUID,
    payload: Optional[StrategyPlanCreate] = None,
    provider: Optional[str] = Query(None, description="Optional LLM provider override."),
    model: Optional[str] = Query(None, description="Optional LLM model override."),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Forces generation of a new historical strategy plan version with incremented version number.
    """
    service = StrategyPlannerService(db)
    title = payload.title if payload else None
    objective = payload.objective if payload else None
    plan = await service.regenerate_plan(
        dataset_id=dataset_id,
        custom_title=title,
        custom_objective=objective,
    )
    return SuccessResponse(
        message="Strategic execution plan regenerated successfully.",
        data=plan,
    )


@router.get(
    "/datasets/{dataset_id}/strategy-plan/history",
    response_model=SuccessResponse[StrategyPlanHistoryResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Strategic Plan Version History",
)
async def get_strategy_plan_history(
    dataset_id: UUID,
    limit: int = Query(10, ge=1, le=100, description="Page limit."),
    offset: int = Query(0, ge=0, description="Page offset."),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Lists historical versions of strategy plans for a dataset.
    """
    service = StrategyPlannerService(db)
    history = await service.list_history(
        dataset_id=dataset_id,
        limit=limit,
        offset=offset,
    )
    return SuccessResponse(
        message=f"Retrieved {len(history.plans)} strategic plan revisions.",
        data=history,
    )


# ---------------------------------------------------------------------------
# 2. Plan Entity Management Endpoints
# ---------------------------------------------------------------------------

@router.get(
    "/strategy-plans/{plan_id}",
    response_model=SuccessResponse[StrategyPlanResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Specific Strategic Plan Version",
)
async def get_strategy_plan_by_id(
    plan_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieves a specific historical strategy plan by ID.
    """
    service = StrategyPlannerService(db)
    plan = await service.get_plan_by_id(plan_id=plan_id)
    return SuccessResponse(
        message="Strategic plan version retrieved successfully.",
        data=plan,
    )


@router.patch(
    "/strategy-plans/{plan_id}/status",
    response_model=SuccessResponse[StrategyPlanResponse],
    status_code=status.HTTP_200_OK,
    summary="Update Strategic Plan Status",
)
async def update_strategy_plan_status(
    plan_id: UUID,
    payload: StrategyPlanStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Updates the lifecycle state (DRAFT, ACTIVE, COMPLETED, ARCHIVED) of a strategy plan.
    """
    service = StrategyPlannerService(db)
    updated = await service.update_plan_status(plan_id=plan_id, new_status=payload.status)
    return SuccessResponse(
        message="Strategic plan status updated successfully.",
        data=updated,
    )
