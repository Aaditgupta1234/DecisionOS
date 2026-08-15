"""Production-grade ChatAnalystService orchestrating conversational intelligence."""

import logging
import time
from typing import Any, Dict, List, Optional, Union
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.ai_insights.providers import BaseLLMProvider, get_llm_provider
from app.chat_analyst.chat_confidence import calculate_chat_confidence
from app.chat_analyst.citation_builder import CitationBuilder
from app.chat_analyst.constants import (
    CHAT_PROMPT_VERSION,
    DEFAULT_CHAT_MODEL,
    DEFAULT_CHAT_PROVIDER,
    QuestionType,
    ResponseType,
)
from app.chat_analyst.context_builder import ChatContextBuilder
from app.chat_analyst.conversation_memory import ConversationMemory
from app.chat_analyst.models.chat_message import ChatMessage
from app.chat_analyst.models.chat_session import ChatSession
from app.chat_analyst.prompt_builder import ChatPromptBuilder
from app.chat_analyst.question_classifier import QuestionClassifier
from app.chat_analyst.repositories.chat_message_repository import (
    ChatMessageRepository,
)
from app.chat_analyst.repositories.chat_session_repository import (
    ChatSessionRepository,
)
from app.chat_analyst.response_validator import ResponseValidator
from app.chat_analyst.retrieval_engine import RetrievalEngine
from app.chat_analyst.schemas.requests import (
    CreateSessionRequest,
    SendMessageRequest,
)
from app.chat_analyst.schemas.responses import (
    ChatMessageResponse,
    ChatResponse,
    ChatSessionResponse,
    CitationResponse,
)
from app.core.constants import ChatMessageRole

from app.repositories.intelligence_repository import IntelligenceRepository

logger = logging.getLogger(__name__)


class ChatAnalystService:
    """
    Orchestrates targeted retrieval, context compression, memory tracking,
    LLM reasoning, anti-hallucination verification, citation resolution, and persistence.
    """

    def __init__(
        self,
        db: Union[AsyncSession, Session],
        provider: Optional[BaseLLMProvider] = None,
    ):
        self.db = db
        self.provider = provider
        self.session_repo = ChatSessionRepository(db)
        self.message_repo = ChatMessageRepository(db)
        self.retrieval_engine = RetrievalEngine(db)
        self.intel_repo = IntelligenceRepository(db)

    def _get_provider(
        self,
        provider_override: Optional[str] = None,
        model_override: Optional[str] = None,
    ) -> BaseLLMProvider:
        if self.provider:
            return self.provider
        return get_llm_provider(
            provider_name=provider_override,
            model_name=model_override,
        )

    # -----------------------------------------------------------------------
    # Session Management
    # -----------------------------------------------------------------------

    async def create_session(
        self,
        dataset_id: UUID,
        title: Optional[str] = None,
        user_id: Optional[UUID] = None,
        organization_id: Optional[UUID] = None,
        provider: Optional[str] = None,
        model: Optional[str] = None,
    ) -> ChatSessionResponse:
        """Creates and persists a new conversational chat session."""
        dataset = await self.intel_repo.get_dataset(dataset_id)
        if not dataset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Dataset with ID '{dataset_id}' not found.",
            )

        session_title = (title or "").strip() or "Business Analysis Session"
        session_provider = provider or DEFAULT_CHAT_PROVIDER
        session_model = model or DEFAULT_CHAT_MODEL

        session = ChatSession(
            dataset_id=dataset_id,
            organization_id=organization_id,
            title=session_title,
            created_by=user_id,
            provider=session_provider,
            model=session_model,
        )
        saved = await self.session_repo.save(session)
        return self._to_session_response(saved, message_count=0)

    async def list_sessions(
        self,
        dataset_id: UUID,
        organization_id: Optional[UUID] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> List[ChatSessionResponse]:
        """Lists active chat sessions for a dataset."""
        sessions = await self.session_repo.list_by_dataset(
            dataset_id=dataset_id,
            organization_id=organization_id,
            limit=limit,
            offset=offset,
        )
        results = []
        for s in sessions:
            count = await self.message_repo.count_by_session(s.id)
            results.append(self._to_session_response(s, message_count=count))
        return results

    async def get_session(
        self,
        session_id: UUID,
        organization_id: Optional[UUID] = None,
    ) -> ChatSessionResponse:
        """Retrieves session metadata."""
        session = await self.session_repo.get_by_id(session_id, organization_id=organization_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Chat session '{session_id}' not found.",
            )
        count = await self.message_repo.count_by_session(session.id)
        return self._to_session_response(session, message_count=count)

    async def delete_session(
        self,
        session_id: UUID,
        organization_id: Optional[UUID] = None,
    ) -> bool:
        """Deletes (archives) a chat session."""
        session = await self.session_repo.get_by_id(session_id, organization_id=organization_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Chat session '{session_id}' not found.",
            )
        return await self.session_repo.delete(session_id)

    # -----------------------------------------------------------------------
    # Message Processing & Interaction
    # -----------------------------------------------------------------------

    async def send_message(
        self,
        session_id: UUID,
        message_text: str,
        req: Optional[SendMessageRequest] = None,
        user_id: Optional[UUID] = None,
        organization_id: Optional[UUID] = None,
    ) -> ChatResponse:
        """
        Submits a user prompt, executes targeted retrieval, prompts LLM,
        validates output, and returns grounded response.
        """
        start_time = time.perf_counter()

        # 1. Validate Session & Text
        cleaned_text = (message_text or "").strip()
        if not cleaned_text:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Message text cannot be empty.",
            )
        if len(cleaned_text) > 4000:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Message text exceeds maximum length of 4000 characters.",
            )

        session = await self.session_repo.get_by_id(session_id, organization_id=organization_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Chat session '{session_id}' not found.",
            )

        # 2. Intent Classification
        question_type, default_resp_type = QuestionClassifier.classify(cleaned_text)

        # 3. Targeted Retrieval
        raw_bundle = await self.retrieval_engine.retrieve_intelligence_bundle(
            dataset_id=session.dataset_id,
            question_type=question_type,
        )
        if not raw_bundle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Dataset with ID '{session.dataset_id}' not found.",
            )

        # 4. Context Compression
        context = ChatContextBuilder.build_chat_context(raw_bundle=raw_bundle, question_type=question_type)
        context_tokens = ChatContextBuilder.estimate_token_count(context)

        # 5. Conversation Memory (Recent Turns)
        history_records = await self.message_repo.get_recent_history(session_id, limit=10)
        formatted_history = ConversationMemory.format_history(history_records)

        # 6. Prompt Formulation
        prompt = ChatPromptBuilder.build_chat_prompt(
            question=cleaned_text,
            context=context,
            history=formatted_history,
        )
        system_prompt = ChatPromptBuilder.get_system_prompt()

        # 7. Persist User Message
        user_msg = ChatMessage(
            session_id=session_id,
            role=ChatMessageRole.USER,
            content=cleaned_text,
            response_type=default_resp_type.value,
            prompt_version=CHAT_PROMPT_VERSION,
        )
        user_msg = await self.message_repo.save(user_msg)

        # 8. LLM Execution & Validation
        provider = self._get_provider(
            provider_override=req.provider_override if req else session.provider,
            model_override=req.model_override if req else session.model,
        )
        temperature = req.temperature if req and req.temperature is not None else 0.2

        raw_output = None
        fallback_triggered = False
        try:
            raw_output = await provider.generate_json(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=temperature,
            )
        except Exception as e:
            logger.warning(f"LLM Chat Analyst failed ({provider.provider_name}): {e}. Activating fallback.")
            fallback_triggered = True

        # 9. Validation & Fallback Handling
        if not raw_output or fallback_triggered:
            val_res = self._render_deterministic_fallback(cleaned_text, context, default_resp_type)
            fallback_triggered = True
        else:
            val_res = ResponseValidator.validate(raw_output, context)
            if not val_res.is_valid:
                logger.warning(f"Chat response validation failed: {val_res.errors}. Activating fallback.")
                val_res = self._render_deterministic_fallback(cleaned_text, context, default_resp_type)
                fallback_triggered = True

        # 10. Citation Enrichment
        citations = CitationBuilder.build_citations(
            context=context,
            finding_ids=val_res.valid_finding_ids,
            root_cause_ids=val_res.valid_root_cause_ids,
            recommendation_ids=val_res.valid_recommendation_ids,
            forecast_ids=val_res.valid_forecast_ids,
            scenario_ids=val_res.valid_scenario_ids,
        )
        legacy_sources = CitationBuilder.to_legacy_source_list(citations)

        # 11. Deterministic Confidence Calculation
        total_citations = (
            len(citations.findings)
            + len(citations.root_causes)
            + len(citations.recommendations)
            + len(citations.forecasts)
            + len(citations.scenarios)
        )
        narr_conf = float(raw_bundle["narrative_report"].narrative_confidence) if raw_bundle.get("narrative_report") else 0.85
        ins_conf = float(raw_bundle["executive_insight_report"].insight_confidence) if raw_bundle.get("executive_insight_report") else 0.85

        chat_confidence = calculate_chat_confidence(
            context=context,
            total_citations_count=total_citations,
            narrative_confidence=narr_conf,
            insight_confidence=ins_conf,
        )

        total_latency = round((time.perf_counter() - start_time) * 1000, 2)

        # 12. Persist Assistant Message
        assistant_msg = ChatMessage(
            session_id=session_id,
            role=ChatMessageRole.ASSISTANT,
            content=val_res.sanitized_answer,
            response_type=val_res.sanitized_response_type,
            response_time_ms=total_latency,
            context_tokens=context_tokens,
            prompt_version=CHAT_PROMPT_VERSION,
            confidence=chat_confidence,
            source_finding_ids=val_res.valid_finding_ids,
            source_root_cause_ids=val_res.valid_root_cause_ids,
            source_recommendation_ids=val_res.valid_recommendation_ids,
            source_forecast_ids=val_res.valid_forecast_ids,
            source_scenario_ids=val_res.valid_scenario_ids,
            citations=citations.model_dump(),
            sources=legacy_sources,
        )
        assistant_msg = await self.message_repo.save(assistant_msg)

        return ChatResponse(
            session_id=session_id,
            user_message=self._to_message_response(user_msg),
            assistant_message=self._to_message_response(assistant_msg, citations=citations),
            answer=val_res.sanitized_answer,
            citations=citations,
            sources=legacy_sources,
            confidence=chat_confidence,
            response_type=val_res.sanitized_response_type,
            fallback_triggered=fallback_triggered,
        )

    async def get_messages(
        self,
        session_id: UUID,
        limit: int = 50,
        offset: int = 0,
        organization_id: Optional[UUID] = None,
    ) -> List[ChatMessageResponse]:
        """Lists message history for a session."""
        session = await self.session_repo.get_by_id(session_id, organization_id=organization_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Chat session '{session_id}' not found.",
            )
        msgs = await self.message_repo.list_by_session(session_id, limit=limit, offset=offset, order_asc=True)
        return [self._to_message_response(m) for m in msgs]

    # -----------------------------------------------------------------------
    # Helper & Fallback Renderers
    # -----------------------------------------------------------------------

    def _render_deterministic_fallback(
        self,
        question: str,
        context: Dict[str, Any],
        default_resp_type: ResponseType,
    ) -> Any:
        """Generates grounded fallback answers when LLM provider is unavailable."""
        h_score = context.get("business_health_score", 85)
        h_status = context.get("business_health_status", "HEALTHY")
        findings = context.get("findings") or []
        root_causes = context.get("root_causes") or []
        recommendations = context.get("recommendations") or []

        f_ids = [str(f.get("id")) for f in findings if f.get("id")]
        rca_ids = [str(r.get("id")) for r in root_causes if r.get("id")]
        rec_ids = [str(r.get("id")) for r in recommendations if r.get("id")]

        p_find = findings[0].get("title") if findings else "operational performance"
        p_rca = root_causes[0].get("cause") if root_causes else "operational factors"
        p_rec = recommendations[0].get("title") if recommendations else "maintain standard cadence"

        if default_resp_type == ResponseType.ROOT_CAUSE:
            ans = (
                f"DecisionOS diagnostic telemetry isolates '{p_find}' as the primary operational variance affecting business trajectory. "
                f"Causal attribution confirms this variance is driven by '{p_rca}'. "
                f"Implementing '{p_rec}' is recommended to resolve this constraint."
            )
        elif default_resp_type == ResponseType.RECOMMENDATION:
            ans = (
                f"DecisionOS verified recommendations identify '{p_rec}' as the top prioritized strategic action. "
                f"This initiative directly mitigates '{p_find}' and protects baseline gross margins and customer retention."
            )
        elif default_resp_type == ResponseType.HEALTH_SCORE:
            ans = (
                f"DecisionOS evaluated Business Health Score is {h_score}/100, placing enterprise operations in {h_status} status. "
                f"Core performance indicators reflect steady baseline throughput with active mitigation focused on '{p_find}'."
            )
        elif default_resp_type == ResponseType.FORECAST:
            ans = (
                f"DecisionOS forecast telemetry reflects positive stabilization upon executing prioritized strategic actions. "
                f"Continuous monitoring is recommended to safeguard baseline revenue trajectory."
            )
        elif default_resp_type == ResponseType.SCENARIO:
            ans = (
                f"DecisionOS scenario simulations indicate that implementing prioritized interventions mitigates downside operational risk "
                f"and accelerates baseline recovery across upcoming reporting cycles."
            )
        else:
            ans = (
                f"DecisionOS enterprise telemetry indicates an overall Business Health Score of {h_score}/100 ({h_status}). "
                f"Primary operational focus centers on mitigating '{p_find}' through '{p_rec}'."
            )

        from app.chat_analyst.response_validator import ChatValidationResult

        return ChatValidationResult(
            is_valid=True,
            errors=[],
            sanitized_answer=ans,
            sanitized_response_type=default_resp_type.value,
            valid_finding_ids=f_ids[:2],
            valid_root_cause_ids=rca_ids[:2],
            valid_recommendation_ids=rec_ids[:2],
            valid_forecast_ids=[],
            valid_scenario_ids=[],
            validation_time_ms=0.0,
        )

    def _to_session_response(
        self,
        session: ChatSession,
        message_count: int = 0,
    ) -> ChatSessionResponse:
        return ChatSessionResponse(
            id=session.id,
            dataset_id=session.dataset_id,
            organization_id=session.organization_id,
            title=session.title,
            created_by=session.created_by,
            provider=session.provider,
            model=session.model,
            is_archived=session.is_archived,
            created_at=session.created_at,
            updated_at=session.updated_at,
            message_count=message_count,
        )

    def _to_message_response(
        self,
        msg: ChatMessage,
        citations: Optional[CitationResponse] = None,
    ) -> ChatMessageResponse:
        cit_dict = citations.model_dump() if citations else (msg.citations or {})
        return ChatMessageResponse(
            id=msg.id,
            session_id=msg.session_id,
            role="USER" if msg.role == ChatMessageRole.USER or str(msg.role).upper().endswith("USER") else "ASSISTANT",
            content=msg.content,
            response_type=msg.response_type,
            response_time_ms=msg.response_time_ms,
            context_tokens=msg.context_tokens,
            prompt_version=msg.prompt_version,
            confidence=msg.confidence,
            source_finding_ids=msg.source_finding_ids or [],
            source_root_cause_ids=msg.source_root_cause_ids or [],
            source_recommendation_ids=msg.source_recommendation_ids or [],
            source_forecast_ids=msg.source_forecast_ids or [],
            source_scenario_ids=msg.source_scenario_ids or [],
            citations=cit_dict,
            created_at=msg.created_at,
        )
