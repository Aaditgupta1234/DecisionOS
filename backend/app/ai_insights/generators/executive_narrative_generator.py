"""ExecutiveNarrativeGenerator synthesizing boardroom-ready executive briefings."""

import logging
from typing import Any, Dict

from app.ai_insights.builders.prompt_builder import PromptBuilder
from app.ai_insights.providers.base_llm_provider import BaseLLMProvider
from app.ai_insights.schemas.ai_insight_schema import ExecutiveNarrative

logger = logging.getLogger(__name__)


class ExecutiveNarrativeGenerator:
    """
    Generates the core executive summary, headline, primary issue briefing,
    and qualitative health assessment from structured intelligence context.
    """

    def __init__(self, provider: BaseLLMProvider):
        self.provider = provider

    async def generate(self, context: Dict[str, Any]) -> ExecutiveNarrative:
        """
        Executes generation and returns validated ExecutiveNarrative instance.
        """
        prompt = PromptBuilder.build_executive_narrative_prompt(context)
        system_prompt = PromptBuilder.get_system_prompt()

        raw_json = await self.provider.generate_json(
            prompt=prompt,
            system_prompt=system_prompt,
        )

        return ExecutiveNarrative.model_validate(raw_json)
