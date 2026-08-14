"""RiskAnalysisGenerator formulating enterprise risk matrices and vulnerability rankings."""

import logging
from typing import Any, Dict

from app.ai_insights.builders.prompt_builder import PromptBuilder
from app.ai_insights.providers.base_llm_provider import BaseLLMProvider
from app.ai_insights.schemas.ai_insight_schema import RiskAnalysis

logger = logging.getLogger(__name__)


class RiskAnalysisGenerator:
    """
    Generates structured risk analysis, impact projections, and grounded mitigations.
    """

    def __init__(self, provider: BaseLLMProvider):
        self.provider = provider

    async def generate(self, context: Dict[str, Any]) -> RiskAnalysis:
        """
        Executes generation and returns validated RiskAnalysis instance.
        """
        prompt = PromptBuilder.build_risk_analysis_prompt(context)
        system_prompt = PromptBuilder.get_system_prompt()

        raw_json = await self.provider.generate_json(
            prompt=prompt,
            system_prompt=system_prompt,
        )

        return RiskAnalysis.model_validate(raw_json)
