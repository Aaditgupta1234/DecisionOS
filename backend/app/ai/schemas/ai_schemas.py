"""Pydantic Schemas for Phase 6.0 AI Analyst & Decision Copilot."""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


# --- Operational Health & Readiness ---

class AIHealthResponse(BaseModel):
    ai_ready: bool
    model_available: bool
    graph_connected: bool
    retrieval_engine: bool
    response_verifier: bool
    audit_system: bool


class AIReadinessResponse(BaseModel):
    portfolio_id: uuid.UUID
    graph_snapshot_id: uuid.UUID
    graph_health_score: float
    freshness_score: float
    coverage_score: float
    forecast_reliability: float
    overall_ai_readiness: float
    is_ai_safe_to_answer: bool
    failure_reason: Optional[str] = None
    created_at: datetime


class GuardrailEvaluationResponse(BaseModel):
    query_text: str
    guardrail_status: str  # SUPPORTED, PARTIALLY_SUPPORTED, INSUFFICIENT_EVIDENCE, OUT_OF_SCOPE
    is_safe_to_execute: bool
    rationale: str


# --- Confidence, Evidence & Citations ---

class ConfidenceBreakdown(BaseModel):
    telemetry_confidence: float
    graph_confidence: float
    causal_confidence: float
    outcome_confidence: float
    overall_confidence: float


class CitationItem(BaseModel):
    source: str
    source_type: str
    source_entity_id: uuid.UUID
    snapshot_version: str
    graph_path: List[str]
    confidence: float
    is_active_source: bool


class EvidenceItem(BaseModel):
    entity_name: str
    entity_type: str
    entity_id: uuid.UUID
    verified_metric: Optional[str] = None
    confidence_score: float


# --- Chat & AI Analyst ---

class ChatRequest(BaseModel):
    portfolio_id: uuid.UUID
    question: str
    conversation_id: Optional[uuid.UUID] = None
    snapshot_version: Optional[int] = 1


class ChatResponse(BaseModel):
    conversation_id: uuid.UUID
    answer: str
    confidence_score: float
    confidence_breakdown: ConfidenceBreakdown
    graph_snapshot_version: str
    pinned_snapshot_id: uuid.UUID
    intent_classification: str
    guardrail_status: str
    verification_passed: bool
    verification_score: float
    evidence: List[EvidenceItem]
    citations: List[CitationItem]
    evidence_count: int
    processing_time_ms: int
    sha256_hash: str


# --- Strategic Decision Copilot ---

class RankedOptionItem(BaseModel):
    rank: int
    path_name: str
    confidence: float
    expected_arr: float
    expected_health_lift: float
    key_advantage: str


class DecisionPackage(BaseModel):
    recommended_option: str
    expected_arr_recovery: float
    expected_health_lift: float
    expected_risk_delta: float
    confidence: float
    ranked_options: List[RankedOptionItem]
    supporting_evidence: List[str]
    risks: List[str]
    tradeoffs: List[str]


class CopilotRequest(BaseModel):
    portfolio_id: uuid.UUID
    question: str
    conversation_id: Optional[uuid.UUID] = None
    snapshot_version: Optional[int] = 1


class CopilotResponse(BaseModel):
    conversation_id: uuid.UUID
    analysis_id: uuid.UUID
    answer: str
    decision_package: DecisionPackage
    confidence_score: float
    confidence_breakdown: ConfidenceBreakdown
    graph_snapshot_version: str
    citations: List[CitationItem]
    processing_time_ms: int
    sha256_hash: str


class DecisionCopilotAnalysisResponse(BaseModel):
    id: uuid.UUID
    portfolio_id: uuid.UUID
    query_id: uuid.UUID
    options_evaluated: List[Dict[str, Any]]
    recommended_option: str
    recommended_option_rank: List[Dict[str, Any]]
    expected_arr_impact: float
    expected_health_delta: float
    expected_risk_delta: float
    confidence_score: float
    snapshot_version: int
    created_at: datetime
    sha256_hash: str

    model_config = ConfigDict(from_attributes=True)


# --- Decision Sessions & Outcomes ---

class AIDecisionSessionCreateRequest(BaseModel):
    portfolio_id: uuid.UUID
    conversation_id: uuid.UUID
    decision_package_id: uuid.UUID
    selected_option: str
    decision_rationale: str


class AIDecisionSessionResponse(BaseModel):
    id: uuid.UUID
    portfolio_id: uuid.UUID
    conversation_id: uuid.UUID
    decision_package_id: uuid.UUID
    selected_option: str
    decision_rationale: str
    decision_status: str  # PROPOSED, UNDER_REVIEW, APPROVED, REJECTED, EXECUTING, COMPLETED
    created_at: datetime
    sha256_hash: str

    model_config = ConfigDict(from_attributes=True)


class AIProvenanceChainResponse(BaseModel):
    id: uuid.UUID
    audit_id: uuid.UUID
    path_nodes: List[Dict[str, Any]]
    path_edges: List[Dict[str, Any]]
    chain_depth: int
    confidence_score: float
    created_at: datetime


class AIEvidenceCoverageResponse(BaseModel):
    id: uuid.UUID
    audit_id: uuid.UUID
    retrieved_node_count: int
    retrieved_edge_count: int
    cited_node_count: int
    cited_edge_count: int
    citation_coverage_percentage: float
    unused_evidence_count: int
    created_at: datetime
    sha256_hash: str

    model_config = ConfigDict(from_attributes=True)


class CopilotOutcomeResponse(BaseModel):
    id: uuid.UUID
    audit_id: uuid.UUID
    recommendation_id: uuid.UUID
    was_accepted: bool
    actual_arr_delta: float
    actual_health_delta: float
    actual_risk_delta: float
    outcome_status: str


# --- Conversations & Evolution ---

class ConversationCreateRequest(BaseModel):
    portfolio_id: uuid.UUID
    title: str


class AIMessageResponse(BaseModel):
    id: uuid.UUID
    role: str
    content: str
    confidence_score: float
    retrieved_context_count: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ConversationResponse(BaseModel):
    id: uuid.UUID
    portfolio_id: uuid.UUID
    title: str
    conversation_status: str
    pinned_snapshot_version: int
    last_snapshot_version: int
    messages: List[AIMessageResponse]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ConversationDiffResponse(BaseModel):
    conversation_id: uuid.UUID
    from_snapshot_version: int
    to_snapshot_version: int
    nodes_added: int
    edges_added: int
    health_score_delta: float
    summary_of_changes: List[str]


# --- Audits & Citations ---

class AIQueryAuditResponse(BaseModel):
    id: uuid.UUID
    portfolio_id: uuid.UUID
    conversation_id: Optional[uuid.UUID] = None
    context_snapshot_id: uuid.UUID
    context_snapshot_version: int
    query_text: str
    query_type: str
    intent_classification: str
    guardrail_status: str
    confidence_score: float
    verification_passed: bool
    verification_score: float
    response_word_count: int
    response_token_count: int
    processing_time_ms: int
    created_at: datetime
    sha256_hash: str

    model_config = ConfigDict(from_attributes=True)


class AIResponseCitationResponse(BaseModel):
    id: uuid.UUID
    audit_id: uuid.UUID
    source_type: str
    source_entity_id: uuid.UUID
    source_name: str
    source_snapshot_version: str
    source_freshness_score: float
    is_active_source: bool
    graph_path: List[str]
    confidence_score: float

    model_config = ConfigDict(from_attributes=True)
