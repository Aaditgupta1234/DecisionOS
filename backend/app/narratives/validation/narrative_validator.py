"""Validation layer for AI-generated executive narratives."""

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from app.narratives.constants import (
    EXECUTIVE_SUMMARY_MAX_WORDS,
    EXECUTIVE_SUMMARY_MIN_WORDS,
    HALLUCINATION_TRIGGERS,
    NARRATIVE_TYPE_EXECUTIVE,
    NARRATIVE_TYPE_FORECAST,
    NARRATIVE_TYPE_KPI,
    NARRATIVE_TYPE_RECOMMENDATION,
    NARRATIVE_TYPE_ROOT_CAUSE,
    NARRATIVE_TYPE_SCENARIO,
    SECTION_NARRATIVE_MAX_WORDS,
    SECTION_NARRATIVE_MIN_WORDS,
)


@dataclass
class ValidationResult:
    """Result payload produced by narrative validation checks."""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    word_count: int = 0
    validation_time_ms: float = 0.0


class NarrativeValidator:
    """
    Validates AI-generated structured narrative output against schemas,
    length limits, and anti-hallucination guardrails.
    """

    REQUIRED_FIELDS_BY_TYPE = {
        NARRATIVE_TYPE_EXECUTIVE: ["headline", "executive_summary", "health_assessment"],
        NARRATIVE_TYPE_KPI: ["summary", "stability_assessment"],
        NARRATIVE_TYPE_ROOT_CAUSE: ["summary", "causal_chain_narrative"],
        NARRATIVE_TYPE_RECOMMENDATION: ["summary", "expected_impact_narrative"],
        NARRATIVE_TYPE_FORECAST: ["summary", "trend_direction"],
        NARRATIVE_TYPE_SCENARIO: ["summary", "baseline_vs_scenario_comparison"],
    }

    @classmethod
    def validate(
        cls,
        data: Any,
        context: Optional[Dict[str, Any]] = None,
        narrative_type: str = NARRATIVE_TYPE_EXECUTIVE,
    ) -> ValidationResult:
        """
        Executes comprehensive validation of the generated dictionary payload.

        Checks:
        1. Dict payload type.
        2. Presence of non-empty required fields.
        3. Word count boundaries.
        4. Absence of ungrounded hallucination triggers.
        """
        start_ts = time.monotonic()
        errors: List[str] = []

        # 1. Type validation
        if not isinstance(data, dict):
            duration = round((time.monotonic() - start_ts) * 1000, 2)
            return ValidationResult(
                is_valid=False,
                errors=[f"Expected dict response, got {type(data).__name__}"],
                word_count=0,
                validation_time_ms=duration,
            )

        # 2. Required fields check
        required_fields = cls.REQUIRED_FIELDS_BY_TYPE.get(narrative_type, ["summary"])
        for req_f in required_fields:
            val = data.get(req_f)
            if not val or not isinstance(val, str) or not val.strip():
                errors.append(f"Missing or empty required field: '{req_f}'")

        # 3. Aggregate text & calculate word count
        text_corpus = []
        for k, v in data.items():
            if isinstance(v, str):
                text_corpus.append(v)
            elif isinstance(v, list):
                for item in v:
                    if isinstance(item, str):
                        text_corpus.append(item)
                    elif isinstance(item, dict):
                        for sub_v in item.values():
                            if isinstance(sub_v, str):
                                text_corpus.append(sub_v)

        combined_text = " ".join(text_corpus)
        words = combined_text.split()
        word_count = len(words)

        # Primary prose word count
        primary_text = data.get("executive_summary") or data.get("summary") or ""
        primary_words = len(primary_text.split())

        # 4. Word count boundaries
        if narrative_type == NARRATIVE_TYPE_EXECUTIVE:
            if primary_words < EXECUTIVE_SUMMARY_MIN_WORDS:
                errors.append(
                    f"Executive summary too short ({primary_words} words, minimum {EXECUTIVE_SUMMARY_MIN_WORDS})"
                )
            elif primary_words > EXECUTIVE_SUMMARY_MAX_WORDS:
                errors.append(
                    f"Executive summary too long ({primary_words} words, maximum {EXECUTIVE_SUMMARY_MAX_WORDS})"
                )
        else:
            if primary_words < SECTION_NARRATIVE_MIN_WORDS:
                errors.append(
                    f"Section narrative too short ({primary_words} words, minimum {SECTION_NARRATIVE_MIN_WORDS})"
                )
            elif primary_words > SECTION_NARRATIVE_MAX_WORDS:
                errors.append(
                    f"Section narrative too long ({primary_words} words, maximum {SECTION_NARRATIVE_MAX_WORDS})"
                )

        # 5. Hallucination trigger detection
        lower_corpus = combined_text.lower()
        for trigger in HALLUCINATION_TRIGGERS:
            if trigger in lower_corpus:
                errors.append(f"Detected ungrounded speculative phrase: '{trigger}'")

        duration_ms = round((time.monotonic() - start_ts) * 1000, 2)
        return ValidationResult(
            is_valid=(len(errors) == 0),
            errors=errors,
            word_count=word_count,
            validation_time_ms=duration_ms,
        )
