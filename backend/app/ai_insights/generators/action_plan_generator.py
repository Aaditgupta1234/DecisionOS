"""ActionPlanGenerator formulating the 90-day phased execution roadmap."""

import logging
from typing import Any, Dict

from app.ai_insights.builders.prompt_builder import PromptBuilder
from app.ai_insights.providers.base_llm_provider import BaseLLMProvider
from app.ai_insights.schemas.ai_insight_schema import ActionPlanRoadmap

logger = logging.getLogger(__name__)


class ActionPlanGenerator:
    """
    Generates a 90-Day phased execution roadmap (Immediate, 30 Days, 60 Days, 90 Days)
    grounded purely in approved recommendations.
    """

    def __init__(self, provider: BaseLLMProvider):
        self.provider = provider

    async def generate(self, context: Dict[str, Any]) -> ActionPlanRoadmap:
        """
        Executes generation and returns validated ActionPlanRoadmap instance.
        """
        prompt = PromptBuilder.build_action_plan_prompt(context)
        system_prompt = PromptBuilder.get_system_prompt()

        raw_json = await self.provider.generate_json(
            prompt=prompt,
            system_prompt=system_prompt,
        )

        return ActionPlanRoadmap.model_validate(raw_json)
