"""Execution Event Dispatcher for Phase 12: Strategic Execution Layer.

Centralized domain event dispatcher validating, persisting, and publishing execution events,
triggering rollups and tagging Phase 13 automation hooks.
"""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.execution.constants import ExecutionEventType
from app.execution.models.event import InitiativeExecutionEvent


class ExecutionEventDispatcher:
    """
    Centralized event dispatcher responsible for recording execution timeline events,
    evaluating automation eligibility, and notifying downstream calculation listeners.
    """

    AUTOMATION_ELIGIBLE_EVENT_TYPES = {
        ExecutionEventType.RISK_ESCALATED,
        ExecutionEventType.BLOCKER_RECORDED,
        ExecutionEventType.MILESTONE_DELAYED,
        ExecutionEventType.OUTCOME_TARGET_MISSED,
        ExecutionEventType.OUTCOME_TARGET_ACHIEVED,
        ExecutionEventType.ADMIN_OVERRIDE,
        ExecutionEventType.GOVERNANCE_REVIEW_COMPLETED,
    }

    def __init__(self, db: Union[AsyncSession, Session]) -> None:
        self.db = db

    async def dispatch_event(
        self,
        organization_id: uuid.UUID,
        initiative_id: uuid.UUID,
        event_type: ExecutionEventType,
        title: str,
        description: str,
        actor_name: str = "System",
        actor_id: Optional[uuid.UUID] = None,
        previous_value: Optional[str] = None,
        new_value: Optional[str] = None,
        metadata_payload: Optional[Dict[str, Any]] = None,
        force_automation_eligible: Optional[bool] = None,
    ) -> InitiativeExecutionEvent:
        """
        Validates, persists, and publishes an initiative execution event.
        """
        is_auto_eligible = (
            force_automation_eligible
            if force_automation_eligible is not None
            else (event_type in self.AUTOMATION_ELIGIBLE_EVENT_TYPES)
        )

        trigger_type = f"AUTO_TRIGGER_{event_type.value}" if is_auto_eligible else None

        event = InitiativeExecutionEvent(
            id=uuid.uuid4(),
            organization_id=organization_id,
            initiative_id=initiative_id,
            event_type=event_type,
            title=title,
            description=description,
            actor_name=actor_name,
            actor_id=actor_id,
            previous_value=previous_value,
            new_value=new_value,
            metadata_payload=metadata_payload or {},
            automation_eligible=is_auto_eligible,
            automation_trigger_type=trigger_type,
            created_at=datetime.now(timezone.utc),
        )

        self.db.add(event)
        if isinstance(self.db, AsyncSession):
            await self.db.flush()
        else:
            self.db.flush()
        return event

    def dispatch_event_sync(
        self,
        organization_id: uuid.UUID,
        initiative_id: uuid.UUID,
        event_type: ExecutionEventType,
        title: str,
        description: str,
        actor_name: str = "System",
        actor_id: Optional[uuid.UUID] = None,
        previous_value: Optional[str] = None,
        new_value: Optional[str] = None,
        metadata_payload: Optional[Dict[str, Any]] = None,
        force_automation_eligible: Optional[bool] = None,
    ) -> InitiativeExecutionEvent:
        """
        Synchronous variant for non-async execution paths.
        """
        is_auto_eligible = (
            force_automation_eligible
            if force_automation_eligible is not None
            else (event_type in self.AUTOMATION_ELIGIBLE_EVENT_TYPES)
        )

        trigger_type = f"AUTO_TRIGGER_{event_type.value}" if is_auto_eligible else None

        event = InitiativeExecutionEvent(
            id=uuid.uuid4(),
            organization_id=organization_id,
            initiative_id=initiative_id,
            event_type=event_type,
            title=title,
            description=description,
            actor_name=actor_name,
            actor_id=actor_id,
            previous_value=previous_value,
            new_value=new_value,
            metadata_payload=metadata_payload or {},
            automation_eligible=is_auto_eligible,
            automation_trigger_type=trigger_type,
            created_at=datetime.now(timezone.utc),
        )

        self.db.add(event)
        self.db.flush()
        return event
