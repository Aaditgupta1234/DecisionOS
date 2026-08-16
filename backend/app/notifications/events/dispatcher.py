"""In-Process Asynchronous Event Dispatcher for Notification Framework."""

import asyncio
import logging
from typing import Any, Callable, Coroutine, List
from app.notifications.events.events import NotificationEvent

logger = logging.getLogger("decisionos.notifications")

EventListener = Callable[[NotificationEvent], Coroutine[Any, Any, None]]


class NotificationEventDispatcher:
    """
    Lightweight, in-process asynchronous event dispatcher for platform notifications.
    Decouples event producers (e.g. JobService) from notification storage and delivery.
    """

    def __init__(self):
        self._listeners: List[EventListener] = []

    def subscribe(self, listener: EventListener) -> None:
        """Register an asynchronous event listener."""
        if listener not in self._listeners:
            self._listeners.append(listener)

    def unsubscribe(self, listener: EventListener) -> None:
        """Remove a previously registered event listener."""
        if listener in self._listeners:
            self._listeners.remove(listener)

    async def publish(self, event: NotificationEvent) -> None:
        """
        Publish an event to all registered in-process listeners concurrently.
        Catches and logs exceptions in individual listeners to prevent cascading failures.
        """
        if not self._listeners:
            logger.debug(f"[NotificationEventDispatcher] No listeners registered for event {event.event_type}")
            return

        tasks = []
        for listener in self._listeners:
            tasks.append(self._invoke_listener(listener, event))

        await asyncio.gather(*tasks, return_exceptions=True)

    async def _invoke_listener(self, listener: EventListener, event: NotificationEvent) -> None:
        try:
            await listener(event)
        except Exception as exc:
            logger.error(
                f"[NotificationEventDispatcher] Listener {listener} failed on event {event.event_type}: {exc}",
                exc_info=True,
            )


# Global in-process singleton instance
notification_event_dispatcher = NotificationEventDispatcher()
