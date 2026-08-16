"""JobExecutor abstract interface and AsyncJobExecutor implementation for Phase 10.1."""

import asyncio
import logging
import uuid
from abc import ABC, abstractmethod
from typing import Any, Awaitable, Callable, Coroutine, Dict, Optional

from app.jobs.constants import DEFAULT_JOB_TIMEOUT_SECONDS

logger = logging.getLogger("decisionos.jobs")


class JobExecutor(ABC):
    """
    Abstract execution engine interface for background workloads.
    Decouples job submission from underlying execution runtime (asyncio vs. future Celery/Redis).
    """

    @abstractmethod
    async def submit(
        self,
        job_id: uuid.UUID,
        coro_fn: Callable[[], Coroutine[Any, Any, None]],
        timeout_seconds: Optional[int] = None,
    ) -> None:
        """Submit a coroutine for asynchronous execution."""
        raise NotImplementedError

    @abstractmethod
    async def cancel(self, job_id: uuid.UUID) -> bool:
        """Attempt to cancel an active job."""
        raise NotImplementedError


class AsyncJobExecutor(JobExecutor):
    """
    In-process asynchronous job executor using Python asyncio tasks.
    Manages active task registries, cancellation tokens, timeout guards, and leak-free cleanups.
    """

    def __init__(self):
        self._active_tasks: Dict[uuid.UUID, asyncio.Task] = {}
        self._cancellation_tokens: Dict[uuid.UUID, asyncio.Event] = {}

    def get_cancellation_event(self, job_id: uuid.UUID) -> asyncio.Event:
        """Get or create the cancellation event for a job."""
        if job_id not in self._cancellation_tokens:
            self._cancellation_tokens[job_id] = asyncio.Event()
        return self._cancellation_tokens[job_id]

    def is_active(self, job_id: uuid.UUID) -> bool:
        """Check if a job has an actively running asyncio task."""
        return job_id in self._active_tasks and not self._active_tasks[job_id].done()

    async def submit(
        self,
        job_id: uuid.UUID,
        coro_fn: Callable[[], Coroutine[Any, Any, None]],
        timeout_seconds: Optional[int] = None,
    ) -> None:
        """
        Spawn an asynchronous task for background job execution.
        Wraps execution with timeout enforcement and ensures cleanup in finally blocks.
        """
        timeout = float(timeout_seconds or DEFAULT_JOB_TIMEOUT_SECONDS)
        cancel_event = self.get_cancellation_event(job_id)

        async def _execution_wrapper():
            try:
                logger.info(f"[AsyncJobExecutor] Starting execution for job {job_id} (timeout={timeout}s)")
                await asyncio.wait_for(coro_fn(), timeout=timeout)
                logger.info(f"[AsyncJobExecutor] Completed execution for job {job_id}")
            except asyncio.TimeoutError:
                logger.warning(f"[AsyncJobExecutor] Job {job_id} exceeded timeout of {timeout}s")
            except asyncio.CancelledError:
                logger.info(f"[AsyncJobExecutor] Job {job_id} task was cancelled")
            except Exception as e:
                logger.error(f"[AsyncJobExecutor] Job {job_id} encountered unhandled error: {e}", exc_info=True)
            finally:
                # Guarantee memory leak-free cleanup
                self._active_tasks.pop(job_id, None)
                self._cancellation_tokens.pop(job_id, None)

        task = asyncio.create_task(_execution_wrapper())
        self._active_tasks[job_id] = task

    async def cancel(self, job_id: uuid.UUID) -> bool:
        """
        Signal cancellation to a running job and abort its asyncio task.
        Returns True if an active task was signalled, False otherwise.
        """
        # Set cooperative cancellation event
        if job_id in self._cancellation_tokens:
            self._cancellation_tokens[job_id].set()

        # Abort asyncio task if running
        task = self._active_tasks.get(job_id)
        if task and not task.done():
            task.cancel()
            return True
        return False

    def active_count(self) -> int:
        """Return the count of actively running jobs."""
        return sum(1 for t in self._active_tasks.values() if not t.done())


# Global singleton instance of AsyncJobExecutor
async_job_executor = AsyncJobExecutor()
