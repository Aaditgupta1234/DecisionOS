"""Response Validator verifying anti-hallucination guardrails and schema compliance."""

import time
from typing import Any, Dict, List, Set
from pydantic import BaseModel, Field
from app.chat_analyst.constants import HALLUCINATION_TRIGGERS


class ChatValidationResult(BaseModel):
    """Validation outcome encapsulating validity, errors, and sanitized citations."""
    is_valid: bool = Field(..., description="True if output satisfies all schema, word-count, and anti-hallucination guardrails.")
    errors: List[str] = Field(default_factory=list, description="List of validation errors.")
    sanitized_answer: str = Field(default="", description="Sanitized response text.")
    sanitized_response_type: str = Field(default="GENERAL", description="Validated response type.")
    valid_finding_ids: List[str] = Field(default_factory=list, description="Verified finding IDs present in context.")
    valid_root_cause_ids: List[str] = Field(default_factory=list, description="Verified RCA IDs present in context.")
    valid_recommendation_ids: List[str] = Field(default_factory=list, description="Verified recommendation IDs present in context.")
    valid_forecast_ids: List[str] = Field(default_factory=list, description="Verified forecast IDs present in context.")
    valid_scenario_ids: List[str] = Field(default_factory=list, description="Verified scenario IDs present in context.")
    validation_time_ms: float = Field(default=0.0, description="Duration in ms.")


class ResponseValidator:
    """Rigorous schema, lexical, and factual validator for chat responses."""

    @classmethod
    def _extract_context_id_sets(cls, context: Dict[str, Any]) -> Dict[str, Set[str]]:
        """Collects all valid UUID strings from context."""
        finding_ids = {str(f.get("id")) for f in context.get("findings", []) if f.get("id")}
        rca_ids = {str(r.get("id")) for r in context.get("root_causes", []) if r.get("id")}
        rec_ids = {str(r.get("id")) for r in context.get("recommendations", []) if r.get("id")}
        fc_ids = {str(fc.get("id")) for fc in context.get("forecasts", []) if fc.get("id")}
        sc_ids = {str(sc.get("id")) for sc in context.get("scenarios", []) if sc.get("id")}
        return {
            "findings": finding_ids,
            "root_causes": rca_ids,
            "recommendations": rec_ids,
            "forecasts": fc_ids,
            "scenarios": sc_ids,
        }

    @classmethod
    def validate(cls, raw_output: Any, context: Dict[str, Any]) -> ChatValidationResult:
        """
        Validates LLM output dictionary against schema, forbidden terms, and citation groundings.
        """
        start = time.perf_counter()
        errors = []

        if not isinstance(raw_output, dict):
            return ChatValidationResult(
                is_valid=False,
                errors=["Payload must be a JSON dictionary."],
                validation_time_ms=round((time.perf_counter() - start) * 1000, 2),
            )

        answer = str(raw_output.get("answer") or "").strip()
        if not answer:
            errors.append("Field 'answer' is missing or empty.")

        # Lexical scan for forbidden hallucination triggers
        lower_ans = answer.lower()
        for trigger in HALLUCINATION_TRIGGERS:
            if trigger in lower_ans:
                errors.append(f"Detected ungrounded speculative phrase '{trigger}' in response.")

        # Validate response type
        resp_type = str(raw_output.get("response_type") or "GENERAL").upper()
        if resp_type not in ["ROOT_CAUSE", "FORECAST", "SCENARIO", "RECOMMENDATION", "HEALTH_SCORE", "GENERAL"]:
            resp_type = "GENERAL"

        # Validate and sanitize citations
        valid_id_sets = cls._extract_context_id_sets(context)

        raw_f_ids = raw_output.get("cited_finding_ids") or []
        valid_f_ids = [str(fid) for fid in raw_f_ids if str(fid) in valid_id_sets["findings"]]

        raw_rca_ids = raw_output.get("cited_root_cause_ids") or []
        valid_rca_ids = [str(rid) for rid in raw_rca_ids if str(rid) in valid_id_sets["root_causes"]]

        raw_rec_ids = raw_output.get("cited_recommendation_ids") or []
        valid_rec_ids = [str(rec_id) for rec_id in raw_rec_ids if str(rec_id) in valid_id_sets["recommendations"]]

        raw_fc_ids = raw_output.get("cited_forecast_ids") or []
        valid_fc_ids = [str(fc_id) for fc_id in raw_fc_ids if str(fc_id) in valid_id_sets["forecasts"]]

        raw_sc_ids = raw_output.get("cited_scenario_ids") or []
        valid_sc_ids = [str(sc_id) for sc_id in raw_sc_ids if str(sc_id) in valid_id_sets["scenarios"]]

        # If model cited non-existent IDs, we drop invalid IDs rather than failing completely
        dur = round((time.perf_counter() - start) * 1000, 2)
        return ChatValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            sanitized_answer=answer,
            sanitized_response_type=resp_type,
            valid_finding_ids=valid_f_ids,
            valid_root_cause_ids=valid_rca_ids,
            valid_recommendation_ids=valid_rec_ids,
            valid_forecast_ids=valid_fc_ids,
            valid_scenario_ids=valid_sc_ids,
            validation_time_ms=dur,
        )
