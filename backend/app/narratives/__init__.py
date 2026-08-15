"""AI Narrative Engine package (Phase 9.2)."""

from app.narratives.builders.narrative_prompt_builder import NarrativePromptBuilder
from app.narratives.constants import (
    NARRATIVE_PROMPT_VERSION,
    NARRATIVE_TYPE_EXECUTIVE,
    NARRATIVE_TYPE_FORECAST,
    NARRATIVE_TYPE_FULL_PACKAGE,
    NARRATIVE_TYPE_KPI,
    NARRATIVE_TYPE_RECOMMENDATION,
    NARRATIVE_TYPE_ROOT_CAUSE,
    NARRATIVE_TYPE_SCENARIO,
)
from app.narratives.scoring import calculate_narrative_confidence
from app.narratives.services.narrative_engine_service import NarrativeEngineService
from app.narratives.templates.fallback_templates import FallbackTemplates
from app.narratives.validation.narrative_validator import (
    NarrativeValidator,
    ValidationResult,
)

__all__ = [
    "NarrativeEngineService",
    "NarrativePromptBuilder",
    "NarrativeValidator",
    "ValidationResult",
    "FallbackTemplates",
    "calculate_narrative_confidence",
    "NARRATIVE_PROMPT_VERSION",
    "NARRATIVE_TYPE_EXECUTIVE",
    "NARRATIVE_TYPE_KPI",
    "NARRATIVE_TYPE_ROOT_CAUSE",
    "NARRATIVE_TYPE_RECOMMENDATION",
    "NARRATIVE_TYPE_FORECAST",
    "NARRATIVE_TYPE_SCENARIO",
    "NARRATIVE_TYPE_FULL_PACKAGE",
]
