"""AIInsightManager coordinating context building, concurrent generator execution, and entity building."""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Union
from uuid import UUID

from app.ai_insights.builders.context_builder import ContextBuilder
from app.ai_insights.constants import INSIGHT_VERSION, PROMPT_VERSION, REPORT_VERSION
from app.ai_insights.generators.action_plan_generator import ActionPlanGenerator
from app.ai_insights.generators.business_assessment_generator import BusinessAssessmentGenerator
from app.ai_insights.generators.executive_narrative_generator import ExecutiveNarrativeGenerator
from app.ai_insights.generators.opportunity_generator import OpportunityGenerator
from app.ai_insights.generators.risk_analysis_generator import RiskAnalysisGenerator
from app.ai_insights.generators.strategic_priority_generator import StrategicPriorityGenerator
from app.ai_insights.providers.base_llm_provider import BaseLLMProvider
from app.intelligence.models import IntelligenceReport
from app.models.ai_insight import AIInsight
from app.schemas.intelligence import IntelligenceReportResponse

logger = logging.getLogger(__name__)


class AIInsightManager:
    """
    Coordinates context building, concurrent generator execution, schema validation,
    and constructs the AIInsight SQLAlchemy model entity.
    """

    def __init__(self, provider: BaseLLMProvider):
        self.provider = provider
        self.narrative_gen = ExecutiveNarrativeGenerator(provider)
        self.assessment_gen = BusinessAssessmentGenerator(provider)
        self.risk_gen = RiskAnalysisGenerator(provider)
        self.opp_gen = OpportunityGenerator(provider)
        self.priority_gen = StrategicPriorityGenerator(provider)
        self.action_gen = ActionPlanGenerator(provider)

    async def generate_and_build(
        self,
        dataset_id: UUID,
        report: Union[IntelligenceReport, IntelligenceReportResponse, Dict[str, Any]],
    ) -> AIInsight:
        """
        Executes all 6 AI insight generators concurrently, validates outputs,
        and constructs an AIInsight model record.
        """
        # 1. Distill Context
        context = ContextBuilder.build_context(report)

        # 2. Run all 6 generators concurrently
        (
            narrative,
            assessment,
            risk_analysis,
            opportunities,
            strategic_priorities,
            action_plan,
        ) = await asyncio.gather(
            self.narrative_gen.generate(context),
            self.assessment_gen.generate(context),
            self.risk_gen.generate(context),
            self.opp_gen.generate(context),
            self.priority_gen.generate(context),
            self.action_gen.generate(context),
        )

        # 3. Compile Metadata
        metadata_info = {
            "business_health_score": context.get("business_health_score"),
            "business_health_status": context.get("business_health_status"),
            "primary_issue": context.get("primary_issue"),
            "confidence_breakdown": context.get("confidence_breakdown"),
            "metric_count": len(context.get("metrics", [])),
            "finding_count": len(context.get("findings", [])),
            "rca_count": len(context.get("root_causes", [])),
            "recommendation_count": len(context.get("recommendations", [])),
        }

        # 4. Construct Model Entity
        return AIInsight(
            dataset_id=dataset_id,
            insight_version=INSIGHT_VERSION,
            prompt_version=PROMPT_VERSION,
            report_version=REPORT_VERSION,
            model_provider=self.provider.provider_name,
            model_name=self.provider.model_name,
            executive_narrative=narrative.model_dump(),
            business_assessment=assessment.model_dump(),
            risk_analysis=risk_analysis.model_dump(),
            opportunities=opportunities.model_dump(),
            strategic_priorities=strategic_priorities.model_dump(),
            action_plan=action_plan.model_dump(),
            metadata_info=metadata_info,
            generated_at=datetime.now(timezone.utc),
        )
