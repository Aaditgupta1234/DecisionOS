"""Policy validation framework for Phase 10.6 Governance Policies."""

from typing import Any, Dict, Union
from app.governance.constants import GovernancePolicyType


class InvalidPolicyValueError(ValueError):
    """Raised when a governance policy payload fails domain boundary validation."""
    pass


class PolicyValidator:
    """
    Validates structure, types, and boundary constraints of governance policy configurations
    prior to database persistence.
    """

    @classmethod
    def validate_policy(
        cls,
        policy_type: Union[GovernancePolicyType, str],
        policy_value: Dict[str, Any],
    ) -> None:
        """Validate policy configuration according to its type."""
        if not isinstance(policy_value, dict):
            raise InvalidPolicyValueError("policy_value must be a JSON object dictionary.")

        pt_val = policy_type.value if isinstance(policy_type, GovernancePolicyType) else str(policy_type)

        if pt_val in (
            GovernancePolicyType.DATA_RETENTION.value,
            GovernancePolicyType.AUDIT_RETENTION.value,
            GovernancePolicyType.NOTIFICATION_RETENTION.value,
        ):
            cls._validate_retention_policy(pt_val, policy_value)
        elif pt_val == GovernancePolicyType.JOB_EXECUTION.value:
            cls._validate_job_execution_policy(policy_value)
        elif pt_val == GovernancePolicyType.SCHEDULE_EXECUTION.value:
            cls._validate_schedule_execution_policy(policy_value)
        elif pt_val == GovernancePolicyType.PLATFORM.value:
            cls._validate_platform_policy(policy_value)
        else:
            # Custom / unknown policy type: ensure non-empty dictionary
            if not policy_value:
                raise InvalidPolicyValueError(f"Empty policy configuration for {pt_val}.")

    @classmethod
    def _validate_retention_policy(cls, policy_type_str: str, value: Dict[str, Any]) -> None:
        retention = value.get("retention_days")
        if retention is None:
            raise InvalidPolicyValueError(f"{policy_type_str} requires 'retention_days' field.")
        if not isinstance(retention, int) or isinstance(retention, bool):
            raise InvalidPolicyValueError("'retention_days' must be an integer.")
        if retention <= 0 or retention > 3650:
            raise InvalidPolicyValueError("'retention_days' must be between 1 and 3650 days (10 years).")

    @classmethod
    def _validate_job_execution_policy(cls, value: Dict[str, Any]) -> None:
        max_jobs = value.get("max_concurrent_jobs")
        if max_jobs is not None:
            if not isinstance(max_jobs, int) or isinstance(max_jobs, bool) or max_jobs <= 0:
                raise InvalidPolicyValueError("'max_concurrent_jobs' must be a positive integer >= 1.")
            if max_jobs > 1000:
                raise InvalidPolicyValueError("'max_concurrent_jobs' cannot exceed 1000.")

        max_dur = value.get("max_duration_seconds")
        if max_dur is not None:
            if not isinstance(max_dur, int) or isinstance(max_dur, bool) or max_dur < 10:
                raise InvalidPolicyValueError("'max_duration_seconds' must be an integer >= 10.")

    @classmethod
    def _validate_schedule_execution_policy(cls, value: Dict[str, Any]) -> None:
        max_scheds = value.get("max_active_schedules")
        if max_scheds is not None:
            if not isinstance(max_scheds, int) or isinstance(max_scheds, bool) or max_scheds <= 0:
                raise InvalidPolicyValueError("'max_active_schedules' must be a positive integer >= 1.")
            if max_scheds > 500:
                raise InvalidPolicyValueError("'max_active_schedules' cannot exceed 500.")

        min_interval = value.get("min_interval_seconds")
        if min_interval is not None:
            if not isinstance(min_interval, int) or isinstance(min_interval, bool) or min_interval < 10:
                raise InvalidPolicyValueError("'min_interval_seconds' must be an integer >= 10.")

    @classmethod
    def _validate_platform_policy(cls, value: Dict[str, Any]) -> None:
        for flag in ("maintenance_mode", "read_only_mode", "allow_user_registrations"):
            if flag in value and not isinstance(value[flag], bool):
                raise InvalidPolicyValueError(f"'{flag}' must be a boolean.")
