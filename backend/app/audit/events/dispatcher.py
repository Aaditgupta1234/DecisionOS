"""In-process asynchronous Audit Event Dispatcher for Phase 10.3: Audit Center."""

import asyncio
import inspect
import logging
from typing import Any, Callable, Coroutine, List, Set

from app.audit.events.events import AuditEvent

logger = logging.getLogger(__name__)

AuditEventListener = Callable[[AuditEvent], Coroutine[Any, Any, None]]


class AuditEventDispatcher:
    """
    Lightweight, strictly in-process asynchronous event bus for operational audit events.
    Enables decoupled domain auditing without external broker dependencies.
    """

    def __init__(self) -> None:
        self._listeners: Set[AuditEventListener] = set()

    def subscribe(self, listener: AuditEventListener) -> None:
        """Register a subscriber listener to receive dispatched audit events."""
        self._listeners.add(listener)

    def unsubscribe(self, listener: AuditEventListener) -> None:
        """Remove a previously registered subscriber listener."""
        self._listeners.discard(listener)

    async def publish(self, event: AuditEvent) -> None:
        """
        Broadcast an audit event asynchronously to all active subscribers.
        Failures in subscribers are logged but do not disrupt other listeners or the caller.
        """
        if not self._listeners:
            return

        tasks = []
        for listener in list(self._listeners):
            try:
                res = listener(event)
                if inspect.isawaitable(res):
                    tasks.append(res)
            except Exception as ex:
                logger.error(f"Error invoking synchronous audit listener: {ex}", exc_info=True)

        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for r in results:
                if isinstance(r, Exception):
                    logger.error(f"Audit event listener raised an error: {r}", exc_info=True)


# Global singleton instance
audit_dispatcher = AuditEventDispatcher()
