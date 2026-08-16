"""Dependency Service for Phase 12: Strategic Execution Layer."""

import uuid
from typing import Dict, List, Set, Union
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.execution.models.dependency import InitiativeDependency
from app.execution.repositories.dependency_repository import DependencyRepository
from app.execution.repositories.initiative_repository import InitiativeRepository
from app.execution.schemas.dependency import (
    DependencyCreate,
    DependencyListResponse,
    DependencyResponse,
)


class DependencyService:
    """Business service managing directed dependencies between strategic initiatives with cycle detection."""

    def __init__(self, db: Union[AsyncSession, Session]) -> None:
        self.db = db
        self.repo = DependencyRepository(db)
        self.init_repo = InitiativeRepository(db)

    async def create_dependency(
        self,
        organization_id: uuid.UUID,
        payload: DependencyCreate,
    ) -> InitiativeDependency:
        """Creates a dependency relationship after cycle and existence validation."""
        if payload.source_initiative_id == payload.target_initiative_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="An initiative cannot depend on or block itself.",
            )

        source_init = await self.init_repo.get_by_id(payload.source_initiative_id, organization_id)
        if not source_init:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Source initiative '{payload.source_initiative_id}' not found.",
            )

        target_init = await self.init_repo.get_by_id(payload.target_initiative_id, organization_id)
        if not target_init:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Target initiative '{payload.target_initiative_id}' not found.",
            )

        # Check for circular dependency
        existing_deps = await self.repo.list_by_organization(organization_id)
        adj: Dict[uuid.UUID, Set[uuid.UUID]] = {}
        for d in existing_deps:
            adj.setdefault(d.source_initiative_id, set()).add(d.target_initiative_id)

        # Proposed edge: source -> target
        adj.setdefault(payload.source_initiative_id, set()).add(payload.target_initiative_id)

        # DFS to detect cycle starting from target back to source
        visited: Set[uuid.UUID] = set()
        rec_stack: Set[uuid.UUID] = set()

        def has_cycle(node: uuid.UUID) -> bool:
            visited.add(node)
            rec_stack.add(node)
            for neighbor in adj.get(node, set()):
                if neighbor not in visited:
                    if has_cycle(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
            rec_stack.remove(node)
            return False

        for n in list(adj.keys()):
            if n not in visited:
                if has_cycle(n):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Circular dependency detected: Adding this dependency would create an execution loop.",
                    )

        dep = InitiativeDependency(
            id=uuid.uuid4(),
            organization_id=organization_id,
            source_initiative_id=payload.source_initiative_id,
            target_initiative_id=payload.target_initiative_id,
            dependency_type=payload.dependency_type,
            notes=payload.notes,
        )

        return await self.repo.create(dep)

    async def list_initiative_dependencies(
        self,
        initiative_id: uuid.UUID,
        organization_id: uuid.UUID,
    ) -> DependencyListResponse:
        """Lists all dependencies related to an initiative."""
        deps = await self.repo.list_by_initiative(initiative_id, organization_id)
        responses = [
            DependencyResponse(
                id=d.id,
                organization_id=d.organization_id,
                source_initiative_id=d.source_initiative_id,
                source_initiative_title=d.source_initiative.title if d.source_initiative else None,
                target_initiative_id=d.target_initiative_id,
                target_initiative_title=d.target_initiative.title if d.target_initiative else None,
                dependency_type=d.dependency_type,
                notes=d.notes,
                created_at=d.created_at,
            )
            for d in deps
        ]

        return DependencyListResponse(
            organization_id=organization_id,
            initiative_id=initiative_id,
            total_dependencies=len(responses),
            dependencies=responses,
        )

    async def delete_dependency(
        self,
        dependency_id: uuid.UUID,
        organization_id: uuid.UUID,
    ) -> bool:
        """Deletes a dependency."""
        deleted = await self.repo.delete(dependency_id, organization_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Dependency with ID '{dependency_id}' was not found.",
            )
        return True
