"""REST API Endpoints for Strategic Programs (Phase 12)."""

import uuid
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, Query, status

from app.api.dependencies.auth import get_current_active_user, require_admin
from app.database.session import get_db
from app.execution.constants import ProgramStatus, ProgramTemplateCode
from app.execution.schemas.program import (
    ProgramCreate,
    ProgramListResponse,
    ProgramResponse,
    ProgramUpdate,
)
from app.execution.services.program_rollup_engine import ProgramRollupEngine
from app.execution.services.program_service import ProgramService
from app.execution.templates import list_templates
from app.models.user import User

program_router = APIRouter(prefix="/programs", tags=["Strategic Programs (Phase 12)"])


def _resolve_org_id(current_user: User, organization_id: Optional[uuid.UUID] = None) -> uuid.UUID:
    """Resolve active organization ID for the authenticated user."""
    if organization_id:
        return organization_id
    if getattr(current_user, "organization_id", None):
        return current_user.organization_id
    if getattr(current_user, "memberships", None) and len(current_user.memberships) > 0:
        return current_user.memberships[0].organization_id
    return current_user.id


@program_router.post(
    "",
    response_model=ProgramResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_program(
    payload: ProgramCreate,
    organization_id: Optional[uuid.UUID] = Query(None, description="Optional organization ID override"),
    db=Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Creates a new strategic program."""
    org_id = _resolve_org_id(current_user, organization_id)
    service = ProgramService(db)
    program = await service.create_program(org_id, payload, current_user=current_user)
    rollup = ProgramRollupEngine.calculate_program_rollup(program)
    return ProgramResponse(
        id=program.id,
        organization_id=program.organization_id,
        decision_package_id=program.decision_package_id,
        template_code=program.template_code,
        title=program.title,
        description=program.description,
        status=rollup["status"],
        owner=program.owner,
        owner_id=program.owner_id,
        start_date=program.start_date,
        target_completion_date=program.target_completion_date,
        actual_completion_date=program.actual_completion_date,
        total_budget_allocated=rollup["total_budget_allocated"],
        total_budget_spent=rollup["total_budget_spent"],
        program_completion_percentage=rollup["program_completion_percentage"],
        program_health_score=rollup["program_health_score"],
        program_health_grade=rollup["program_health_grade"],
        initiative_count=rollup["initiative_count"],
        created_at=program.created_at,
        updated_at=program.updated_at,
    )


@program_router.post(
    "/from-template",
    response_model=ProgramResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_program_from_template(
    template_code: ProgramTemplateCode = Query(..., description="Pre-configured program template code"),
    custom_title: Optional[str] = Query(None, description="Optional title override"),
    custom_owner: Optional[str] = Query(None, description="Optional owner override"),
    organization_id: Optional[uuid.UUID] = Query(None, description="Optional organization ID override"),
    db=Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Instantiates a complete Strategic Program and child initiatives from seed template."""
    org_id = _resolve_org_id(current_user, organization_id)
    service = ProgramService(db)
    program = await service.create_from_template(
        organization_id=org_id,
        template_code=template_code,
        custom_title=custom_title,
        custom_owner=custom_owner,
        current_user=current_user,
    )
    rollup = ProgramRollupEngine.calculate_program_rollup(program)
    return ProgramResponse(
        id=program.id,
        organization_id=program.organization_id,
        decision_package_id=program.decision_package_id,
        template_code=program.template_code,
        title=program.title,
        description=program.description,
        status=rollup["status"],
        owner=program.owner,
        owner_id=program.owner_id,
        start_date=program.start_date,
        target_completion_date=program.target_completion_date,
        actual_completion_date=program.actual_completion_date,
        total_budget_allocated=rollup["total_budget_allocated"],
        total_budget_spent=rollup["total_budget_spent"],
        program_completion_percentage=rollup["program_completion_percentage"],
        program_health_score=rollup["program_health_score"],
        program_health_grade=rollup["program_health_grade"],
        initiative_count=rollup["initiative_count"],
        created_at=program.created_at,
        updated_at=program.updated_at,
    )


@program_router.get(
    "/templates",
    status_code=status.HTTP_200_OK,
)
async def get_program_templates(
    current_user: User = Depends(get_current_active_user),
) -> List[Dict[str, Any]]:
    """Returns available system-defined seed program templates."""
    return list_templates()


@program_router.get(
    "",
    response_model=ProgramListResponse,
    status_code=status.HTTP_200_OK,
)
async def list_programs(
    status_filter: Optional[ProgramStatus] = Query(None, description="Optional status filter"),
    organization_id: Optional[uuid.UUID] = Query(None, description="Optional organization ID override"),
    db=Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Lists strategic programs with calculated rollups."""
    org_id = _resolve_org_id(current_user, organization_id)
    service = ProgramService(db)
    return await service.list_programs(org_id, status_filter=status_filter)


@program_router.get(
    "/{program_id}",
    response_model=ProgramResponse,
    status_code=status.HTTP_200_OK,
)
async def get_program_detail(
    program_id: uuid.UUID,
    organization_id: Optional[uuid.UUID] = Query(None, description="Optional organization ID override"),
    db=Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Retrieves single strategic program by ID with live rollup calculations."""
    org_id = _resolve_org_id(current_user, organization_id)
    service = ProgramService(db)
    program = await service.get_program_by_id(program_id, org_id)
    rollup = ProgramRollupEngine.calculate_program_rollup(program)
    return ProgramResponse(
        id=program.id,
        organization_id=program.organization_id,
        decision_package_id=program.decision_package_id,
        template_code=program.template_code,
        title=program.title,
        description=program.description,
        status=rollup["status"],
        owner=program.owner,
        owner_id=program.owner_id,
        start_date=program.start_date,
        target_completion_date=program.target_completion_date,
        actual_completion_date=program.actual_completion_date,
        total_budget_allocated=rollup["total_budget_allocated"],
        total_budget_spent=rollup["total_budget_spent"],
        program_completion_percentage=rollup["program_completion_percentage"],
        program_health_score=rollup["program_health_score"],
        program_health_grade=rollup["program_health_grade"],
        initiative_count=rollup["initiative_count"],
        created_at=program.created_at,
        updated_at=program.updated_at,
    )


@program_router.patch(
    "/{program_id}",
    response_model=ProgramResponse,
    status_code=status.HTTP_200_OK,
)
async def update_program(
    program_id: uuid.UUID,
    payload: ProgramUpdate,
    organization_id: Optional[uuid.UUID] = Query(None, description="Optional organization ID override"),
    db=Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Updates strategic program details."""
    org_id = _resolve_org_id(current_user, organization_id)
    service = ProgramService(db)
    program = await service.update_program(program_id, org_id, payload)
    rollup = ProgramRollupEngine.calculate_program_rollup(program)
    return ProgramResponse(
        id=program.id,
        organization_id=program.organization_id,
        decision_package_id=program.decision_package_id,
        template_code=program.template_code,
        title=program.title,
        description=program.description,
        status=rollup["status"],
        owner=program.owner,
        owner_id=program.owner_id,
        start_date=program.start_date,
        target_completion_date=program.target_completion_date,
        actual_completion_date=program.actual_completion_date,
        total_budget_allocated=rollup["total_budget_allocated"],
        total_budget_spent=rollup["total_budget_spent"],
        program_completion_percentage=rollup["program_completion_percentage"],
        program_health_score=rollup["program_health_score"],
        program_health_grade=rollup["program_health_grade"],
        initiative_count=rollup["initiative_count"],
        created_at=program.created_at,
        updated_at=program.updated_at,
    )


@program_router.delete(
    "/{program_id}",
    status_code=status.HTTP_200_OK,
)
async def delete_program(
    program_id: uuid.UUID,
    organization_id: Optional[uuid.UUID] = Query(None, description="Optional organization ID override"),
    db=Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Deletes strategic program and cascades to child initiatives (Admin only)."""
    from sqlalchemy import select
    from app.execution.models.program import StrategicProgram
    from sqlalchemy.ext.asyncio import AsyncSession

    org_id = _resolve_org_id(current_user, organization_id)
    if not organization_id:
        stmt = select(StrategicProgram).where(StrategicProgram.id == program_id)
        if isinstance(db, AsyncSession):
            res = await db.execute(stmt)
            prog = res.scalar_one_or_none()
        else:
            prog = db.execute(stmt).scalar_one_or_none()
        if prog:
            org_id = prog.organization_id

    service = ProgramService(db)
    await service.delete_program(program_id, org_id)
    return {"status": "success", "message": f"Strategic program '{program_id}' deleted successfully."}
