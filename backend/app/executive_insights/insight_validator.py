"""Validation layer for Phase 9.3: Executive Insight Generator."""

import time
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from app.executive_insights.constants import (
    BOARD_COMMENTARY_MAX_WORDS,
    BOARD_COMMENTARY_MIN_WORDS,
    HALLUCINATION_TRIGGERS,
    INSIGHT_TYPE_ACTIONS,
    INSIGHT_TYPE_ALERTS,
    INSIGHT_TYPE_BOARD_COMMENTARY,
    INSIGHT_TYPE_FULL_PACKAGE,
    INSIGHT_TYPE_OPPORTUNITIES,
    INSIGHT_TYPE_RISKS,
    INSIGHT_TYPE_THEMES,
    OPPORTUNITY_DESC_MAX_WORDS,
    OPPORTUNITY_DESC_MIN_WORDS,
    RISK_DESC_MAX_WORDS,
    RISK_DESC_MIN_WORDS,
)


class InsightValidationResult(BaseModel):
    """Encapsulates validation outcome, errors, and timing telemetry."""
    is_valid: bool = Field(..., description="True if output satisfies all schema, word-count, and anti-hallucination guardrails.")
    errors: List[str] = Field(default_factory=list, description="Descriptive list of validation errors.")
    validation_time_ms: float = Field(default=0.0, description="Duration of validation check in milliseconds.")


class ExecutiveInsightValidator:
    """Rigorous schema integrity and anti-hallucination validator for Executive Insights."""

    @classmethod
    def _count_words(cls, text: str) -> int:
        return len(text.strip().split()) if text and text.strip() else 0

    @classmethod
    def _scan_hallucination_triggers(cls, text: str, field_name: str) -> List[str]:
        errors = []
        lower = text.lower()
        for trigger in HALLUCINATION_TRIGGERS:
            if trigger in lower:
                errors.append(f"Detected ungrounded speculative phrase '{trigger}' in field '{field_name}'.")
        return errors

    @classmethod
    def validate_risks(cls, data: Any) -> InsightValidationResult:
        start = time.perf_counter()
        errors = []

        if not isinstance(data, dict):
            return InsightValidationResult(
                is_valid=False,
                errors=["Payload must be a JSON dictionary containing 'top_risks'."],
                validation_time_ms=round((time.perf_counter() - start) * 1000, 2),
            )

        risks = data.get("top_risks")
        if not isinstance(risks, list) or len(risks) == 0:
            errors.append("Field 'top_risks' must be a non-empty list.")
        else:
            for idx, r in enumerate(risks):
                if not isinstance(r, dict):
                    errors.append(f"Risk item at index {idx} must be an object.")
                    continue
                if not r.get("title") or not str(r["title"]).strip():
                    errors.append(f"Risk item at index {idx} missing 'title'.")
                desc = r.get("description", "")
                w_count = cls._count_words(desc)
                if w_count < RISK_DESC_MIN_WORDS or w_count > RISK_DESC_MAX_WORDS:
                    errors.append(f"Risk item '{r.get('title', idx)}' description word count ({w_count}) outside bounds [{RISK_DESC_MIN_WORDS}-{RISK_DESC_MAX_WORDS}].")
                errors.extend(cls._scan_hallucination_triggers(desc, f"top_risks[{idx}].description"))
                sev = str(r.get("severity", "")).upper()
                if sev not in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
                    errors.append(f"Risk item at index {idx} has invalid severity '{sev}'.")

        dur = round((time.perf_counter() - start) * 1000, 2)
        return InsightValidationResult(is_valid=len(errors) == 0, errors=errors, validation_time_ms=dur)

    @classmethod
    def validate_opportunities(cls, data: Any) -> InsightValidationResult:
        start = time.perf_counter()
        errors = []

        if not isinstance(data, dict):
            return InsightValidationResult(
                is_valid=False,
                errors=["Payload must be a JSON dictionary containing 'top_opportunities'."],
                validation_time_ms=round((time.perf_counter() - start) * 1000, 2),
            )

        opps = data.get("top_opportunities")
        if not isinstance(opps, list) or len(opps) == 0:
            errors.append("Field 'top_opportunities' must be a non-empty list.")
        else:
            for idx, o in enumerate(opps):
                if not isinstance(o, dict):
                    errors.append(f"Opportunity item at index {idx} must be an object.")
                    continue
                if not o.get("title") or not str(o["title"]).strip():
                    errors.append(f"Opportunity item at index {idx} missing 'title'.")
                desc = o.get("description", "")
                w_count = cls._count_words(desc)
                if w_count < OPPORTUNITY_DESC_MIN_WORDS or w_count > OPPORTUNITY_DESC_MAX_WORDS:
                    errors.append(f"Opportunity item '{o.get('title', idx)}' description word count ({w_count}) outside bounds [{OPPORTUNITY_DESC_MIN_WORDS}-{OPPORTUNITY_DESC_MAX_WORDS}].")
                errors.extend(cls._scan_hallucination_triggers(desc, f"top_opportunities[{idx}].description"))
                imp = str(o.get("impact", "")).upper()
                if imp not in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
                    errors.append(f"Opportunity item at index {idx} has invalid impact '{imp}'.")

        dur = round((time.perf_counter() - start) * 1000, 2)
        return InsightValidationResult(is_valid=len(errors) == 0, errors=errors, validation_time_ms=dur)

    @classmethod
    def validate_priority_actions(cls, data: Any) -> InsightValidationResult:
        start = time.perf_counter()
        errors = []

        if not isinstance(data, dict):
            return InsightValidationResult(
                is_valid=False,
                errors=["Payload must be a JSON dictionary containing 'priority_actions'."],
                validation_time_ms=round((time.perf_counter() - start) * 1000, 2),
            )

        actions = data.get("priority_actions")
        if not isinstance(actions, list) or len(actions) == 0:
            errors.append("Field 'priority_actions' must be a non-empty list.")
        else:
            for idx, a in enumerate(actions):
                if not isinstance(a, dict):
                    errors.append(f"Action item at index {idx} must be an object.")
                    continue
                if not a.get("action") or not str(a["action"]).strip():
                    errors.append(f"Action item at index {idx} missing 'action'.")
                rationale = a.get("rationale", "")
                errors.extend(cls._scan_hallucination_triggers(rationale, f"priority_actions[{idx}].rationale"))

        dur = round((time.perf_counter() - start) * 1000, 2)
        return InsightValidationResult(is_valid=len(errors) == 0, errors=errors, validation_time_ms=dur)

    @classmethod
    def validate_strategic_themes(cls, data: Any) -> InsightValidationResult:
        start = time.perf_counter()
        errors = []

        if not isinstance(data, dict):
            return InsightValidationResult(
                is_valid=False,
                errors=["Payload must be a JSON dictionary containing 'strategic_themes'."],
                validation_time_ms=round((time.perf_counter() - start) * 1000, 2),
            )

        themes = data.get("strategic_themes")
        if not isinstance(themes, list) or len(themes) == 0:
            errors.append("Field 'strategic_themes' must be a non-empty list.")
        else:
            for idx, t in enumerate(themes):
                if not isinstance(t, dict) or not t.get("theme"):
                    errors.append(f"Theme at index {idx} missing 'theme' name.")

        dur = round((time.perf_counter() - start) * 1000, 2)
        return InsightValidationResult(is_valid=len(errors) == 0, errors=errors, validation_time_ms=dur)

    @classmethod
    def validate_executive_alerts(cls, data: Any) -> InsightValidationResult:
        start = time.perf_counter()
        errors = []

        if not isinstance(data, dict):
            return InsightValidationResult(
                is_valid=False,
                errors=["Payload must be a JSON dictionary containing 'executive_alerts'."],
                validation_time_ms=round((time.perf_counter() - start) * 1000, 2),
            )

        alerts = data.get("executive_alerts")
        if not isinstance(alerts, list):
            errors.append("Field 'executive_alerts' must be a list.")
        else:
            for idx, al in enumerate(alerts):
                if not isinstance(al, dict) or not al.get("headline"):
                    errors.append(f"Alert at index {idx} missing 'headline'.")

        dur = round((time.perf_counter() - start) * 1000, 2)
        return InsightValidationResult(is_valid=len(errors) == 0, errors=errors, validation_time_ms=dur)

    @classmethod
    def validate_board_commentary(cls, data: Any) -> InsightValidationResult:
        start = time.perf_counter()
        errors = []

        if not isinstance(data, dict):
            return InsightValidationResult(
                is_valid=False,
                errors=["Payload must be a JSON dictionary."],
                validation_time_ms=round((time.perf_counter() - start) * 1000, 2),
            )

        commentary_dict = data.get("board_commentary") if "board_commentary" in data and isinstance(data["board_commentary"], dict) else data
        comm_text = commentary_dict.get("commentary", "")
        w_count = cls._count_words(comm_text)

        if w_count < BOARD_COMMENTARY_MIN_WORDS:
            errors.append(f"Board commentary too short ({w_count} words, minimum {BOARD_COMMENTARY_MIN_WORDS}).")
        elif w_count > BOARD_COMMENTARY_MAX_WORDS:
            errors.append(f"Board commentary exceeds word limit ({w_count} words, maximum {BOARD_COMMENTARY_MAX_WORDS}).")

        errors.extend(cls._scan_hallucination_triggers(comm_text, "board_commentary.commentary"))

        if not commentary_dict.get("headline"):
            errors.append("Missing required field 'headline' in board commentary.")

        dur = round((time.perf_counter() - start) * 1000, 2)
        return InsightValidationResult(is_valid=len(errors) == 0, errors=errors, validation_time_ms=dur)

    @classmethod
    def validate_full_package(cls, data: Any) -> InsightValidationResult:
        start = time.perf_counter()
        errors = []

        if not isinstance(data, dict):
            return InsightValidationResult(
                is_valid=False,
                errors=["Full package payload must be a JSON dictionary."],
                validation_time_ms=round((time.perf_counter() - start) * 1000, 2),
            )

        res_r = cls.validate_risks(data)
        if not res_r.is_valid:
            errors.extend(res_r.errors)

        res_o = cls.validate_opportunities(data)
        if not res_o.is_valid:
            errors.extend(res_o.errors)

        res_a = cls.validate_priority_actions(data)
        if not res_a.is_valid:
            errors.extend(res_a.errors)

        res_t = cls.validate_strategic_themes(data)
        if not res_t.is_valid:
            errors.extend(res_t.errors)

        res_al = cls.validate_executive_alerts(data)
        if not res_al.is_valid:
            errors.extend(res_al.errors)

        res_b = cls.validate_board_commentary(data.get("board_commentary", {}))
        if not res_b.is_valid:
            errors.extend(res_b.errors)

        dur = round((time.perf_counter() - start) * 1000, 2)
        return InsightValidationResult(is_valid=len(errors) == 0, errors=errors, validation_time_ms=dur)

    @classmethod
    def validate(cls, data: Any, insight_type: str) -> InsightValidationResult:
        if insight_type == INSIGHT_TYPE_RISKS:
            return cls.validate_risks(data)
        elif insight_type == INSIGHT_TYPE_OPPORTUNITIES:
            return cls.validate_opportunities(data)
        elif insight_type == INSIGHT_TYPE_ACTIONS:
            return cls.validate_priority_actions(data)
        elif insight_type == INSIGHT_TYPE_THEMES:
            return cls.validate_strategic_themes(data)
        elif insight_type == INSIGHT_TYPE_ALERTS:
            return cls.validate_executive_alerts(data)
        elif insight_type == INSIGHT_TYPE_BOARD_COMMENTARY:
            return cls.validate_board_commentary(data)
        elif insight_type == INSIGHT_TYPE_FULL_PACKAGE:
            return cls.validate_full_package(data)
        else:
            return InsightValidationResult(is_valid=True, errors=[], validation_time_ms=0.0)
