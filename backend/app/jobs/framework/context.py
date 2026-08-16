"""JobContext execution wrapper for Phase 10.1 Background Job Infrastructure."""

import asyncio
import uuid
from typing import Any, Awaitable, Callable, Dict, Optional


class JobContext:
    """
    Execution context provided to background job handlers.
    Exposes progress update callbacks and cooperative cancellation checks.
    """

    def __init__(
        self,
        job_id: uuid.UUID,
        organization_id: uuid.UUID,
        job_type: str,
        payload: Optional[Dict[str, Any]] = None,
        created_by_user_id: Optional[uuid.UUID] = None,
        progress_callback: Optional[Callable[[int, Optional[Dict[str, Any]]], Awaitable[None]]] = None,
        cancellation_event: Optional[asyncio.Event] = None,
    ):
        self.job_id = job_id
        self.organization_id = organization_id
        self.job_type = job_type
        self.payload = payload or {}
        self.created_by_user_id = created_by_user_id
        self._progress_callback = progress_callback
        self._cancellation_event = cancellation_event or asyncio.Event()

    async def update_progress(
        self, progress_percent: int, partial_result: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Report execution progress (0-100) and optional intermediate results back to the caller/repository.
        """
        if self._progress_callback is not None:
            await self._progress_callback(
                max(0, min(100, progress_percent)), partial_result
            )

    def is_cancelled(self) -> bool:
        """Check if a cancellation signal has been dispatched for this job."""
        return self._cancellation_event.is_set()

    def check_cancelled(self) -> None:
        """Raise asyncio.CancelledError if the cancellation event is set."""
        if self.is_cancelled():
            raise asyncio.CancelledError(f"Job {self.job_id} was cancelled by user.")
