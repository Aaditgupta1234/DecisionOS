"""AIInsightService orchestrating request caching, forced regeneration, and history retrieval."""

import logging
from typing import List, Optional, Union
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.ai_insights.providers import BaseLLMProvider, get_llm_provider
from app.ai_insights.schemas.ai_insight_schema import (
    AIInsightHistoryItem,
    AIInsightResponse,
)
from app.ai_insights.services.ai_insight_manager import AIInsightManager
from app.repositories.ai_insight_repository import AIInsightRepository
from app.services.intelligence_service import IntelligenceService

logger = logging.getLogger(__name__)


class AIInsightService:
    """
    Business service coordinating intelligence aggregation, LLM caching,
    forced regeneration, and historical revisions.
    """

    def __init__(
        self,
        db: Union[AsyncSession, Session],
        provider: Optional[BaseLLMProvider] = None,
    ):
        self.db = db
        self.repo = AIInsightRepository(db)
        self.intel_service = IntelligenceService(db)
        self._provider = provider

    def _is_async(self) -> bool:
        return isinstance(self.db, AsyncSession)

    def _get_provider(
        self,
        provider_name: Optional[str] = None,
        model_name: Optional[str] = None,
    ) -> BaseLLMProvider:
        if self._provider:
            return self._provider
        return get_llm_provider(provider_name=provider_name, model_name=model_name)

    async def get_insights(
        self,
        dataset_id: UUID,
        force_regenerate: bool = False,
        provider_name: Optional[str] = None,
        model_name: Optional[str] = None,
    ) -> AIInsightResponse:
        """
        Retrieves cached AI insights if available, or generates and caches fresh insights.
        """
        # 1. Check cache first unless forced
        if not force_regenerate:
            cached = await self.repo.get_latest_by_dataset(dataset_id)
            if cached:
                return AIInsightResponse.model_validate(cached)

        # 2. Fetch Intelligence Report
        report_response = await self.intel_service.get_intelligence_report(dataset_id)

        # 3. Resolve Provider and Manager
        provider = self._get_provider(provider_name=provider_name, model_name=model_name)
        manager = AIInsightManager(provider=provider)

        # 4. Generate and Build Entity
        insight_model = await manager.generate_and_build(
            dataset_id=dataset_id,
            report=report_response,
        )

        # 5. Persist to Database
        persisted = await self.repo.create(insight_model)

        # 6. Commit Session
        if self._is_async():
            await self.db.commit()
        else:
            self.db.commit()

        return AIInsightResponse.model_validate(persisted)

    async def regenerate_insights(
        self,
        dataset_id: UUID,
        provider_name: Optional[str] = None,
        model_name: Optional[str] = None,
    ) -> AIInsightResponse:
        """Forces new LLM insight generation and appends to version history."""
        return await self.get_insights(
            dataset_id=dataset_id,
            force_regenerate=True,
            provider_name=provider_name,
            model_name=model_name,
        )

    async def list_history(
        self,
        dataset_id: UUID,
        limit: int = 10,
        offset: int = 0,
    ) -> List[AIInsightHistoryItem]:
        """
        Retrieves historical AI insight revisions for a dataset.
        """
        records = await self.repo.list_history_by_dataset(
            dataset_id=dataset_id,
            limit=limit,
            offset=offset,
        )

        return [
            AIInsightHistoryItem(
                id=rec.id,
                dataset_id=rec.dataset_id,
                insight_version=rec.insight_version,
                model_provider=rec.model_provider,
                model_name=rec.model_name,
                headline=rec.executive_narrative.get("headline", "AI Executive Insight"),
                generated_at=rec.generated_at,
            )
            for rec in records
        ]
