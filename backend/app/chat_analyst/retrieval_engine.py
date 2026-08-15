"""Targeted Intelligence Retrieval Engine for Phase 9.4 AI Chat Analyst."""

import logging
from typing import Any, Dict, List, Optional, Tuple, Union
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.chat_analyst.constants import QuestionType
from app.executive_insights.repositories.executive_insight_repository import (
    ExecutiveInsightRepository,
)
from app.forecasting.repositories.forecast_repository import ForecastRepository
from app.intelligence.health_score import BusinessHealthScoreEngine
from app.models.dataset import Dataset
from app.models.dataset_metric import DatasetMetric
from app.models.diagnostic_finding import DiagnosticFinding
from app.models.recommendation import Recommendation
from app.models.root_cause_analysis import RootCauseAnalysis
from app.repositories.intelligence_repository import IntelligenceRepository
from app.repositories.narrative_repository import NarrativeRepository
from app.scenario_simulation.repositories.scenario_repository import (
    ScenarioRepository,
)

logger = logging.getLogger(__name__)


class RetrievalEngine:
    """
    Retrieves verified platform intelligence artifacts across KPIs, diagnostics,
    root causes, recommendations, narratives, executive insights, forecasts,
    and scenario simulations.
    
    STRICT GUARDRAIL: Under no circumstance does this engine query raw CSV files.
    """

    def __init__(self, db: Union[AsyncSession, Session]):
        self.db = db
        self.intel_repo = IntelligenceRepository(db)
        self.narrative_repo = NarrativeRepository(db)
        self.insight_repo = ExecutiveInsightRepository(db)
        self.forecast_repo = ForecastRepository(db)
        self.scenario_repo = ScenarioRepository(db)

    async def retrieve_intelligence_bundle(
        self,
        dataset_id: UUID,
        question_type: QuestionType = QuestionType.GENERAL_BUSINESS_QUESTION,
    ) -> Optional[Dict[str, Any]]:
        """
        Gathers only verified analytical telemetry and persistent report snapshots.
        """
        artifacts = await self.intel_repo.get_dataset_with_all_artifacts(dataset_id)
        if not artifacts:
            return None

        dataset, metrics, findings, root_causes, recommendations = artifacts

        # 1. Deterministic Health Score
        health_score, health_status = BusinessHealthScoreEngine.calculate(
            findings=findings,
            root_causes=root_causes,
            recommendations=recommendations,
        )

        # 2. Latest AI Narrative Report
        latest_narrative = await self.narrative_repo.get_latest_by_dataset(dataset_id)

        # 3. Latest Executive Insight Report
        latest_insights = await self.insight_repo.get_latest_by_dataset(dataset_id)

        # 4. Forecast Simulations
        forecasts = await self.forecast_repo.list_history_by_dataset(dataset_id, limit=5)

        # 5. Scenario Simulations
        scenarios = await self.scenario_repo.list_history_by_dataset(dataset_id, limit=5)

        return {
            "dataset": dataset,
            "metrics": metrics,
            "findings": findings,
            "root_causes": root_causes,
            "recommendations": recommendations,
            "health_score": health_score,
            "health_status": health_status.value if hasattr(health_status, "value") else str(health_status),
            "narrative_report": latest_narrative,
            "executive_insight_report": latest_insights,
            "forecasts": forecasts,
            "scenarios": scenarios,
            "question_type": question_type,
        }
