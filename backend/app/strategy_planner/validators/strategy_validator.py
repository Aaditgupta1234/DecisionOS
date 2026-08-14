"""Strict reject-only deterministic validator for AI-generated strategy execution plans."""

from typing import Any, Dict, Set
from app.core.constants import TargetDirection, TimeHorizon


class StrategyValidationError(Exception):
    """Raised when an AI-generated strategy plan violates deterministic trust boundaries."""
    pass


class StrategyValidator:
    """
    Pure deterministic validation engine enforcing strict recommendation traceability,
    valid existing KPI references, and allowable execution time horizons without semantic repair.
    """

    VALID_TIME_HORIZONS: Set[str] = {h.value for h in TimeHorizon}
    VALID_TARGET_DIRECTIONS: Set[str] = {d.value for d in TargetDirection}

    @classmethod
    def validate(
        cls,
        plan_dict: Dict[str, Any],
        allowed_recommendation_ids: Set[str],
        allowed_metric_keys: Set[str],
    ) -> None:
        """
        Validates LLM-generated strategy plan structure against authoritative dataset allowlists.
        Raises StrategyValidationError on any violation.
        """
        if not isinstance(plan_dict, dict):
            raise StrategyValidationError("Plan output is not a valid JSON dictionary.")

        # 1. Action Items Traceability & Horizon Validation
        action_items = plan_dict.get("action_items")
        if not isinstance(action_items, list):
            raise StrategyValidationError("'action_items' must be a list.")

        for action in action_items:
            if not isinstance(action, dict):
                raise StrategyValidationError("Each action item must be an object.")

            title = action.get("title", "Untitled Action")
            rec_id = action.get("source_recommendation_id")
            if not rec_id or str(rec_id) not in allowed_recommendation_ids:
                raise StrategyValidationError(
                    f"Action '{title}' references invalid or unallowed source recommendation ID '{rec_id}'."
                )

            horizon = action.get("time_horizon")
            if horizon not in cls.VALID_TIME_HORIZONS:
                raise StrategyValidationError(
                    f"Action '{title}' specifies invalid time horizon '{horizon}'. Must be one of {cls.VALID_TIME_HORIZONS}."
                )

        # 2. Strategic Priorities Traceability
        priorities = plan_dict.get("strategic_priorities")
        if not isinstance(priorities, list):
            raise StrategyValidationError("'strategic_priorities' must be a list.")

        for priority in priorities:
            if not isinstance(priority, dict):
                raise StrategyValidationError("Each strategic priority must be an object.")

            p_title = priority.get("title", "Untitled Priority")
            rec_ids = priority.get("source_recommendation_ids")
            if not isinstance(rec_ids, list) or len(rec_ids) == 0:
                raise StrategyValidationError(
                    f"Strategic priority '{p_title}' must contain non-empty 'source_recommendation_ids'."
                )

            for rid in rec_ids:
                if str(rid) not in allowed_recommendation_ids:
                    raise StrategyValidationError(
                        f"Strategic priority '{p_title}' references invalid recommendation ID '{rid}'."
                    )

        # 3. Success Criteria KPI Reference Validation
        criteria = plan_dict.get("success_criteria")
        if not isinstance(criteria, list):
            raise StrategyValidationError("'success_criteria' must be a list.")

        for crit in criteria:
            if not isinstance(crit, dict):
                raise StrategyValidationError("Each success criterion must be an object.")

            metric_key = crit.get("metric_key")
            if not metric_key or metric_key not in allowed_metric_keys:
                raise StrategyValidationError(
                    f"Success criterion references unknown or unallowed metric_key '{metric_key}'. "
                    f"Must be an existing dataset KPI from {allowed_metric_keys}."
                )

            direction = crit.get("target_direction")
            if direction not in cls.VALID_TARGET_DIRECTIONS:
                raise StrategyValidationError(
                    f"Success criterion for '{metric_key}' has invalid target direction '{direction}'."
                )

        # 4. Milestones Horizon Validation
        milestones = plan_dict.get("milestones")
        if not isinstance(milestones, list):
            raise StrategyValidationError("'milestones' must be a list.")

        for ms in milestones:
            if not isinstance(ms, dict):
                raise StrategyValidationError("Each milestone must be an object.")

            ms_title = ms.get("title", "Untitled Milestone")
            m_horizon = ms.get("time_horizon")
            if m_horizon not in cls.VALID_TIME_HORIZONS:
                raise StrategyValidationError(
                    f"Milestone '{ms_title}' specifies invalid time horizon '{m_horizon}'."
                )

        # 5. Source Recommendation IDs List Check
        plan_rec_ids = plan_dict.get("source_recommendation_ids") or []
        for rid in plan_rec_ids:
            if str(rid) not in allowed_recommendation_ids:
                raise StrategyValidationError(
                    f"Plan lists source recommendation ID '{rid}' not belonging to dataset."
                )
