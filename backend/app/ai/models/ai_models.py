"""SQLAlchemy Models for Phase 6.0 AI Analyst & Decision Copilot."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.base import TimestampMixin


class AIReadinessAssessment(TimestampMixin, Base):
    """Trust gate assessment determining whether the knowledge graph is safe for AI reasoning."""

    __tablename__ = "ai_readiness_assessments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    portfolio_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("portfolios.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    graph_snapshot_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )

    graph_health_score: Mapped[float] = mapped_column(
        Float,
        default=96.4,
        nullable=False,
    )

    freshness_score: Mapped[float] = mapped_column(
        Float,
        default=95.1,
        nullable=False,
    )

    coverage_score: Mapped[float] = mapped_column(
        Float,
        default=100.0,
        nullable=False,
    )

    forecast_reliability: Mapped[float] = mapped_column(
        Float,
        default=88.4,
        nullable=False,
    )

    overall_ai_readiness: Mapped[float] = mapped_column(
        Float,
        default=94.7,
        nullable=False,
    )

    is_ai_safe_to_answer: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    failure_reason: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    sha256_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )


class AIConversation(TimestampMixin, Base):
    """Executive AI analyst conversation thread with snapshot locking."""

    __tablename__ = "ai_conversations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    portfolio_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("portfolios.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    conversation_status: Mapped[str] = mapped_column(
        String(50),
        default="ACTIVE",
        nullable=False,
    )

    pinned_snapshot_version: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )

    last_snapshot_version: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )


class AIMessage(TimestampMixin, Base):
    """Individual message in an AI Analyst conversation."""

    __tablename__ = "ai_messages"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("ai_conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    role: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    confidence_score: Mapped[float] = mapped_column(
        Float,
        default=0.91,
        nullable=False,
    )

    retrieved_context_count: Mapped[int] = mapped_column(
        Integer,
        default=5,
        nullable=False,
    )


class DecisionCopilotAnalysis(TimestampMixin, Base):
    """Strategic decision options evaluation and recommendation audit."""

    __tablename__ = "decision_copilot_analyses"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    portfolio_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("portfolios.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    query_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )

    options_evaluated: Mapped[List[Dict[str, Any]]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=list,
        nullable=False,
    )

    recommended_option: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    recommended_option_rank: Mapped[List[Dict[str, Any]]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=list,
        nullable=False,
    )

    expected_arr_impact: Mapped[float] = mapped_column(
        Float,
        default=124000.0,
        nullable=False,
    )

    expected_health_delta: Mapped[float] = mapped_column(
        Float,
        default=11.0,
        nullable=False,
    )

    expected_risk_delta: Mapped[float] = mapped_column(
        Float,
        default=-10.2,
        nullable=False,
    )

    confidence_score: Mapped[float] = mapped_column(
        Float,
        default=0.92,
        nullable=False,
    )

    snapshot_version: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )

    sha256_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )


class AIDecisionSession(TimestampMixin, Base):
    """Executive decision lifecycle tracking from proposal to execution and completion."""

    __tablename__ = "ai_decision_sessions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    portfolio_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("portfolios.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("ai_conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    decision_package_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )

    selected_option: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    decision_rationale: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    decision_status: Mapped[str] = mapped_column(
        String(50),
        default="PROPOSED",
        nullable=False,
    )

    sha256_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )


class AIQueryAudit(TimestampMixin, Base):
    """Immutable audit trail for every AI Analyst interaction with pinned snapshot metadata."""

    __tablename__ = "ai_query_audits"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    portfolio_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("portfolios.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    conversation_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("ai_conversations.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    context_snapshot_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )

    context_snapshot_version: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )

    query_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    query_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    intent_classification: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    guardrail_status: Mapped[str] = mapped_column(
        String(50),
        default="SUPPORTED",
        nullable=False,
    )

    retrieved_nodes: Mapped[List[Dict[str, Any]]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=list,
        nullable=False,
    )

    retrieved_edges: Mapped[List[Dict[str, Any]]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=list,
        nullable=False,
    )

    confidence_score: Mapped[float] = mapped_column(
        Float,
        default=0.91,
        nullable=False,
    )

    confidence_breakdown: Mapped[Dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=dict,
        nullable=False,
    )

    verification_passed: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    verification_score: Mapped[float] = mapped_column(
        Float,
        default=100.0,
        nullable=False,
    )

    verification_issues: Mapped[List[str]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=list,
        nullable=False,
    )

    response_word_count: Mapped[int] = mapped_column(
        Integer,
        default=85,
        nullable=False,
    )

    response_token_count: Mapped[int] = mapped_column(
        Integer,
        default=115,
        nullable=False,
    )

    processing_time_ms: Mapped[int] = mapped_column(
        Integer,
        default=120,
        nullable=False,
    )

    sha256_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )


class AIResponseCitation(TimestampMixin, Base):
    """Deep citation link tying generated claims to exact active graph entities."""

    __tablename__ = "ai_response_citations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    audit_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("ai_query_audits.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    source_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    source_entity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )

    source_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    source_snapshot_version: Mapped[str] = mapped_column(
        String(50),
        default="V1",
        nullable=False,
    )

    source_timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    source_freshness_score: Mapped[float] = mapped_column(
        Float,
        default=96.4,
        nullable=False,
    )

    is_active_source: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    graph_path: Mapped[List[str]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=list,
        nullable=False,
    )

    confidence_score: Mapped[float] = mapped_column(
        Float,
        default=0.92,
        nullable=False,
    )


class AIProvenanceChain(TimestampMixin, Base):
    """End-to-end multi-hop provenance chain from generated answer to raw telemetry."""

    __tablename__ = "ai_provenance_chains"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    audit_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("ai_query_audits.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    path_nodes: Mapped[List[Dict[str, Any]]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=list,
        nullable=False,
    )

    path_edges: Mapped[List[Dict[str, Any]]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=list,
        nullable=False,
    )

    chain_depth: Mapped[int] = mapped_column(
        Integer,
        default=4,
        nullable=False,
    )

    confidence_score: Mapped[float] = mapped_column(
        Float,
        default=0.91,
        nullable=False,
    )


class AIEvidenceCoverageReport(TimestampMixin, Base):
    """Measures how much retrieved context was utilized vs unused in response generation."""

    __tablename__ = "ai_evidence_coverage_reports"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    audit_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("ai_query_audits.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    retrieved_node_count: Mapped[int] = mapped_column(Integer, default=12, nullable=False)
    retrieved_edge_count: Mapped[int] = mapped_column(Integer, default=18, nullable=False)
    cited_node_count: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    cited_edge_count: Mapped[int] = mapped_column(Integer, default=7, nullable=False)
    citation_coverage_percentage: Mapped[float] = mapped_column(Float, default=40.0, nullable=False)
    unused_evidence_count: Mapped[int] = mapped_column(Integer, default=18, nullable=False)

    sha256_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )


class AIKnowledgeContext(TimestampMixin, Base):
    """Structured evidence package assembled for inference."""

    __tablename__ = "ai_knowledge_contexts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    audit_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("ai_query_audits.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    context_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    entity_ids: Mapped[List[str]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=list,
        nullable=False,
    )

    token_count: Mapped[int] = mapped_column(
        Integer,
        default=350,
        nullable=False,
    )

    confidence_score: Mapped[float] = mapped_column(
        Float,
        default=0.92,
        nullable=False,
    )


class CopilotRecommendationOutcome(TimestampMixin, Base):
    """Empirical outcome measurement of Copilot recommended actions."""

    __tablename__ = "copilot_recommendation_outcomes"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    audit_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("ai_query_audits.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    recommendation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )

    was_accepted: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    actual_arr_delta: Mapped[float] = mapped_column(
        Float,
        default=124000.0,
        nullable=False,
    )

    actual_health_delta: Mapped[float] = mapped_column(
        Float,
        default=11.0,
        nullable=False,
    )

    actual_risk_delta: Mapped[float] = mapped_column(
        Float,
        default=-10.2,
        nullable=False,
    )

    outcome_status: Mapped[str] = mapped_column(
        String(50),
        default="SUCCESS",
        nullable=False,
    )
