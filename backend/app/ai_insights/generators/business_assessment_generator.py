"""BusinessAssessmentGenerator evaluating strengths, weaknesses, and functional domains."""

import logging
from typing import Any, Dict

from app.ai_insights.builders.prompt_builder import PromptBuilder
from app.ai_insights.providers.base_llm_provider import BaseLLMProvider
from app.ai_insights.schemas.ai_insight_schema import BusinessAssessment

logger = logging.getLogger(__name__)


class BusinessAssessmentGenerator:
    """
    Generates multi-domain operational, revenue, customer, and product assessments.
    """

    def __init__(self, provider: BaseLLMProvider):
        self.provider = provider

    async def generate(self, context: Dict[str, Any]) -> BusinessAssessment:
        """
        Executes generation and returns validated BusinessAssessment instance.
        """
        prompt = PromptBuilder.build_business_assessment_prompt(context)
        system_prompt = PromptBuilder.get_system_prompt()

        raw_json = await self.provider.generate_json(
            prompt=prompt,
            system_prompt=system_prompt,
        )

        return BusinessAssessment.model_validate(raw_json)
