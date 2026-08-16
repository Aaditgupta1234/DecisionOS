"""Cron evaluation and schedule calculation engine using croniter."""

from datetime import datetime, timezone
from typing import Optional
from croniter import croniter
import pytz


class CronEvaluator:
    """Evaluates standard 5-field cron expressions and computes execution run times."""

    @staticmethod
    def validate_cron_expression(cron_expr: str) -> bool:
        """
        Validate whether a cron expression is syntactically valid.
        Example: "0 8 * * *" (Every day at 08:00 AM)
        """
        if not cron_expr or not isinstance(cron_expr, str):
            return False
        parts = cron_expr.strip().split()
        if len(parts) != 5:
            return False
        return croniter.is_valid(cron_expr.strip())

    @staticmethod
    def calculate_next_run(
        cron_expr: str,
        base_time: Optional[datetime] = None,
        tz_str: str = "UTC",
    ) -> datetime:
        """
        Calculate the next run timestamp in UTC given a cron expression and timezone.
        """
        if not CronEvaluator.validate_cron_expression(cron_expr):
            raise ValueError(f"Invalid cron expression: '{cron_expr}'")

        try:
            tz = pytz.timezone(tz_str)
        except Exception:
            tz = pytz.UTC

        now_utc = base_time or datetime.now(timezone.utc)
        if now_utc.tzinfo is None:
            now_utc = now_utc.replace(tzinfo=timezone.utc)

        # Convert base time to target timezone
        local_base = now_utc.astimezone(tz)

        # Compute next run in local timezone
        iter_obj = croniter(cron_expr.strip(), local_base)
        next_local = iter_obj.get_next(datetime)

        # Convert next run back to UTC
        if next_local.tzinfo is None:
            next_local = tz.localize(next_local)
        next_utc = next_local.astimezone(pytz.UTC)

        return next_utc

    @staticmethod
    def is_due(
        next_run_at: datetime,
        current_time: Optional[datetime] = None,
    ) -> bool:
        """Determine if a schedule is due for execution."""
        now = current_time or datetime.now(timezone.utc)
        if next_run_at.tzinfo is None:
            next_run_at = next_run_at.replace(tzinfo=timezone.utc)
        if now.tzinfo is None:
            now = now.replace(tzinfo=timezone.utc)
        return next_run_at <= now
