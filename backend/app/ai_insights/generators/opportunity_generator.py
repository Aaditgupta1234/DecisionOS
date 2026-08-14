"""OpportunityGenerator identifying growth and operational efficiency levers."""

import logging
from typing import Any, Dict

from app.ai_insights.builders.prompt_builder import PromptBuilder
from app.ai_insights.providers.base_llm_provider import BaseLLMProvider
from app.ai_insights.schemas.ai_insight_schema import OpportunityAssessment

logger = logging.getLogger(__name__)


class OpportunityGenerator:
    """
    Generates growth, efficiency, customer value, and revenue upside opportunities.
    """

    def __init__(self, provider: BaseLLMProvider):
        self.provider = provider

    async def generate(self, context: Dict[str, Any]) -> OpportunityAssessment:
        """
        Executes generation and returns validated OpportunityAssessment instance.
        """
        prompt = PromptBuilder.build_opportunity_prompt(context)
        system_prompt = PromptBuilder.get_system_prompt()

        raw_json = await self.provider.generate_json(
            prompt=prompt,
            system_prompt=system_prompt,
        )

        return OpportunityAssessment.model_validate(raw_json)
