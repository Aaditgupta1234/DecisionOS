"""BaseJob abstract class for Background Job Infrastructure."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from app.jobs.framework.context import JobContext


class BaseJob(ABC):
    """
    Abstract base class for all background job handlers in DecisionOS.
    Subclasses implement the async `run()` method with progress reporting.
    """

    job_type: str = ""
    timeout_seconds: Optional[int] = None

    @abstractmethod
    async def run(self, context: JobContext) -> Dict[str, Any]:
        """
        Execute the core business logic of the job.

        Args:
            context: JobContext containing job_id, payload, and progress callbacks.

        Returns:
            Dict[str, Any]: Standardized result dictionary containing "summary", "artifacts", "warnings".
        """
        raise NotImplementedError("Subclasses must implement run(context)")
