"""Execution APIRouter aggregating all Phase 12 sub-routers."""

from fastapi import APIRouter

from app.execution.api.v1.dependency_endpoints import dependency_router
from app.execution.api.v1.event_endpoints import event_router
from app.execution.api.v1.initiative_endpoints import initiative_router
from app.execution.api.v1.program_endpoints import program_router

execution_router = APIRouter(prefix="/execution", tags=["Strategic Execution Layer (Phase 12)"])

execution_router.include_router(program_router)
execution_router.include_router(initiative_router)
execution_router.include_router(event_router)
execution_router.include_router(dependency_router)
