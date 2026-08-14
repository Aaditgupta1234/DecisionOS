"""StrategicPriorityGenerator sequencing time-phased executive priorities."""

import logging
from typing import Any, Dict

from app.ai_insights.builders.prompt_builder import PromptBuilder
from app.ai_insights.providers.base_llm_provider import BaseLLMProvider
from app.ai_insights.schemas.ai_insight_schema import StrategicPriorities

logger = logging.getLogger(__name__)


class StrategicPriorityGenerator:
    """
    Sequences initiatives into Immediate (1-7 days), Short-Term (30 days),
    and Medium-Term (60-90 days) based on recommendation impact, effort, and time-to-value.
    """

    def __init__(self, provider: BaseLLMProvider):
        self.provider = provider

    async def generate(self, context: Dict[str, Any]) -> StrategicPriorities:
        """
        Executes generation and returns validated StrategicPriorities instance.
        """
        prompt = PromptBuilder.build_strategic_priority_prompt(context)
        system_prompt = PromptBuilder.get_system_prompt()

        raw_json = await self.provider.generate_json(
            prompt=prompt,
            system_prompt=system_prompt,
        )

        return StrategicPriorities.model_validate(raw_json)
