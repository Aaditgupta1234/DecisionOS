"""JobRegistry and built-in reference handlers for Phase 10.1 Background Job Infrastructure."""

import asyncio
from typing import Any, Dict, List, Optional, Type

from app.jobs.constants import JobType
from app.jobs.framework.base_job import BaseJob
from app.jobs.framework.context import JobContext


# Built-in Infrastructure Job Handlers
class EchoJobHandler(BaseJob):
    """Reference job handler that echoes input payload back with progress steps."""
    job_type = JobType.ECHO.value

    async def run(self, context: JobContext) -> Dict[str, Any]:
        await context.update_progress(25)
        await asyncio.sleep(0.01)
        context.check_cancelled()

        await context.update_progress(75)
        await asyncio.sleep(0.01)
        context.check_cancelled()

        await context.update_progress(100)
        return {
            "summary": {"echo": context.payload, "status": "echoed"},
            "artifacts": {},
            "warnings": [],
        }


class ComputeJobHandler(BaseJob):
    """Reference job handler for numerical arithmetic operations with progress reporting."""
    job_type = JobType.COMPUTE.value

    async def run(self, context: JobContext) -> Dict[str, Any]:
        numbers = context.payload.get("numbers", [1, 2, 3, 4, 5])
        operation = context.payload.get("operation", "sum")

        await context.update_progress(20)
        context.check_cancelled()

        if operation == "sum":
            result_val = sum(numbers)
        elif operation == "product":
            result_val = 1
            for n in numbers:
                result_val *= n
        elif operation == "average":
            result_val = sum(numbers) / max(1, len(numbers))
        else:
            raise ValueError(f"Unsupported compute operation: {operation}")

        await context.update_progress(80)
        context.check_cancelled()

        await context.update_progress(100)
        return {
            "summary": {"operation": operation, "input_count": len(numbers), "result": result_val},
            "artifacts": {},
            "warnings": [],
        }


class SimulatedWorkJobHandler(BaseJob):
    """Reference handler for simulating multi-step asynchronous workloads with cancellation support."""
    job_type = JobType.SIMULATED_WORK.value

    async def run(self, context: JobContext) -> Dict[str, Any]:
        steps = context.payload.get("steps", 5)
        step_delay = context.payload.get("step_delay_seconds", 0.05)
        should_fail = context.payload.get("should_fail", False)
        fail_at_step = context.payload.get("fail_at_step", 3)

        for step in range(1, steps + 1):
            context.check_cancelled()
            if should_fail and step == fail_at_step:
                raise RuntimeError(f"Simulated failure at step {step} of {steps}")

            progress_pct = int((step / steps) * 100)
            await context.update_progress(
                progress_pct,
                partial_result={"current_step": step, "total_steps": steps},
            )
            if step_delay > 0:
                await asyncio.sleep(step_delay)

        return {
            "summary": {"completed_steps": steps, "status": "success"},
            "artifacts": {"artifact_count": steps},
            "warnings": [],
        }


class JobRegistry:
    """
    Central registry mapping job_type strings to BaseJob implementation classes.
    Enables pluggable, open-closed addition of new domain handlers.
    """

    _registry: Dict[str, Type[BaseJob]] = {}

    @classmethod
    def register(cls, job_type: str, handler_cls: Type[BaseJob]) -> None:
        """Register a new job handler class for a specific job_type."""
        cls._registry[job_type] = handler_cls

    @classmethod
    def get(cls, job_type: str) -> Optional[Type[BaseJob]]:
        """Retrieve the registered handler class for a job_type."""
        return cls._registry.get(job_type)

    @classmethod
    def has(cls, job_type: str) -> bool:
        """Check whether a handler is registered for a job_type."""
        return job_type in cls._registry

    @classmethod
    def list_registered_types(cls) -> List[str]:
        """List all currently registered job type identifiers."""
        return sorted(list(cls._registry.keys()))

    @classmethod
    def clear(cls) -> None:
        """Reset registry (primarily for testing isolation)."""
        cls._registry.clear()

    @classmethod
    def register_defaults(cls) -> None:
        """Register default built-in infrastructure handlers."""
        cls.register(JobType.ECHO.value, EchoJobHandler)
        cls.register(JobType.COMPUTE.value, ComputeJobHandler)
        cls.register(JobType.SIMULATED_WORK.value, SimulatedWorkJobHandler)


# Auto-register default handlers upon module import
JobRegistry.register_defaults()
