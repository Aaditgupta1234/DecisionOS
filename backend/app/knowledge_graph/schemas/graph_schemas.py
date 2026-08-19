"""Pydantic Schemas for Phase 5.5 Enterprise Knowledge Graph & Causal Intelligence."""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


# --- Knowledge Graph Snapshots & Health ---

class KnowledgeGraphSnapshotResponse(BaseModel):
    id: uuid.UUID
    portfolio_id: uuid.UUID
    snapshot_version: int
    node_count: int
    edge_count: int
    freshness_score: float
    ai_ready: bool
    ai_context_score: float
    graph_hash: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class GraphHealthResponse(BaseModel):
    portfolio_id: uuid.UUID
    snapshot_version: int
    graph_health_score: float
    node_count: int
    edge_count: int
    cycle_count: int
    broken_edges: int
    unreachable_nodes: int
    orphan_nodes: int
    ai_ready: bool
    freshness_score: float


class GraphCoverageResponse(BaseModel):
    portfolio_id: uuid.UUID
    snapshot_id: uuid.UUID
    coverage_percentage: float
    datasets_covered: int
    datasets_total: int
    findings_covered: int
    findings_total: int
    root_causes_covered: int
    root_causes_total: int
    recommendations_covered: int
    recommendations_total: int
    initiatives_covered: int
    initiatives_total: int
    alerts_covered: int
    alerts_total: int
    outcomes_covered: int
    outcomes_total: int
    created_at: datetime


class GraphEntityStatisticsResponse(BaseModel):
    portfolio_id: uuid.UUID
    snapshot_id: uuid.UUID
    datasets_count: int
    kpis_count: int
    findings_count: int
    root_causes_count: int
    recommendations_count: int
    initiatives_count: int
    forecasts_count: int
    simulations_count: int
    alerts_count: int
    interventions_count: int
    outcomes_count: int
    total_entities: int


class GraphBuildRunResponse(BaseModel):
    id: uuid.UUID
    portfolio_id: uuid.UUID
    snapshot_id: uuid.UUID
    nodes_created: int
    edges_created: int
    build_duration_ms: int
    build_status: str
    created_at: datetime
    sha256_hash: str

    model_config = ConfigDict(from_attributes=True)


class GraphSnapshotDiffResponse(BaseModel):
    id: uuid.UUID
    portfolio_id: uuid.UUID
    from_snapshot_id: uuid.UUID
    to_snapshot_id: uuid.UUID
    from_version: int
    to_version: int
    nodes_added: int
    nodes_removed: int
    edges_added: int
    edges_removed: int
    health_score_delta: float
    change_details: Dict[str, Any]
    created_at: datetime


# --- Nodes and Edges ---

class GraphNodeResponse(BaseModel):
    id: uuid.UUID
    portfolio_id: uuid.UUID
    graph_snapshot_id: Optional[uuid.UUID] = None
    node_type: str
    node_name: str
    node_status: str  # ACTIVE, ARCHIVED, DEPRECATED, SUPERSEDED
    source_entity_id: uuid.UUID
    source_system: Optional[str] = None
    source_created_at: Optional[datetime] = None
    source_updated_at: Optional[datetime] = None
    node_metadata: Dict[str, Any]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class GraphEdgeResponse(BaseModel):
    id: uuid.UUID
    portfolio_id: uuid.UUID
    graph_snapshot_id: Optional[uuid.UUID] = None
    source_node_id: uuid.UUID
    target_node_id: uuid.UUID
    relationship_type: str
    evidence_type: str
    evidence_reference_id: Optional[uuid.UUID] = None
    weight: float
    confidence_score: float
    effective_confidence: float
    last_validated_at: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class KnowledgeGraphOverviewResponse(BaseModel):
    portfolio_id: uuid.UUID
    snapshot_version: int
    total_nodes: int
    total_edges: int
    topological_density: float
    nodes: List[GraphNodeResponse]
    edges: List[GraphEdgeResponse]


class RecommendationLifecycleResponse(BaseModel):
    recommendation_id: uuid.UUID
    status: str
    superseded_by_recommendation_id: Optional[uuid.UUID] = None
    reason: str
    updated_at: datetime


# --- Causal Intelligence Schemas ---

class CausalPathStep(BaseModel):
    step_number: int
    node_id: uuid.UUID
    node_type: str
    name: str
    relationship_to_next: Optional[str] = None
    evidence_type: Optional[str] = None
    confidence_score: float


class CausalChainResponse(BaseModel):
    id: uuid.UUID
    portfolio_id: uuid.UUID
    chain_name: str
    root_cause_id: uuid.UUID
    recommendation_id: uuid.UUID
    initiative_id: uuid.UUID
    alert_id: Optional[uuid.UUID] = None
    outcome_id: Optional[uuid.UUID] = None
    outcome_status: str
    causal_strength: float
    confidence_score: float
    path_steps: List[CausalPathStep]
    sha256_hash: str


# --- Outcome Attribution Schemas ---

class OutcomeAttributionResponse(BaseModel):
    recommendation_id: uuid.UUID
    recommendation_title: str
    initiative_id: uuid.UUID
    initiative_title: str
    outcome_id: uuid.UUID
    attribution_score: float
    arr_contribution: float
    health_contribution: float
    confidence_score: float


class OutcomeAttributionRankingResponse(BaseModel):
    portfolio_id: uuid.UUID
    total_attributions: int
    top_arr_producing_recommendations: List[OutcomeAttributionResponse]
    top_health_improving_initiatives: List[OutcomeAttributionResponse]


# --- Impact Propagation Schemas ---

class AffectedNodeItem(BaseModel):
    node_id: uuid.UUID
    node_type: str
    node_name: str
    hop_depth: int
    estimated_variance_pct: float
    direction: str  # POSITIVE, NEGATIVE
    confidence_score: float


class ImpactPropagationResponse(BaseModel):
    portfolio_id: uuid.UUID
    source_node_id: uuid.UUID
    source_node_name: str
    propagation_depth: int
    impact_score: float
    confidence_score: float
    affected_nodes: List[AffectedNodeItem]


# --- Recommendation Effectiveness & Initiative Profiling Schemas ---

class RecommendationRankItem(BaseModel):
    recommendation_id: uuid.UUID
    title: str
    verification_count: int
    evidence_strength: str  # VERY_HIGH, HIGH, MODERATE, LOW
    success_rate_pct: float
    avg_arr_recovery: float
    avg_health_lift: float
    avg_risk_reduction: float
    lifecycle_status: str


class RecommendationEffectivenessResponse(BaseModel):
    portfolio_id: uuid.UUID
    total_ranked_recommendations: int
    rankings: List[RecommendationRankItem]


class InitiativeProfileItem(BaseModel):
    initiative_id: str
    title: str
    reliability_score: float
    execution_velocity_pct: float
    roi_multiplier: float
    outcome_consistency: str  # VERY_HIGH, HIGH, MODERATE


class InitiativeIntelligenceResponse(BaseModel):
    portfolio_id: uuid.UUID
    total_profiles: int
    profiles: List[InitiativeProfileItem]


# --- Enterprise Explainability Schemas ---

class GraphProvenanceLink(BaseModel):
    source_node_name: str
    relationship: str
    target_node_name: str
    evidence_type: str


class ExplanationConfidenceBreakdown(BaseModel):
    telemetry_confidence: float
    causal_confidence: float
    outcome_validation: float
    composite_confidence: float


class ExplainabilityResponse(BaseModel):
    query_type: str
    entity_id: uuid.UUID
    entity_name: str
    explanation: str
    graph_snapshot_version: int
    confidence_score: float
    confidence_breakdown: ExplanationConfidenceBreakdown
    provenance_chain: List[GraphProvenanceLink]


class ExplainabilityQueryResponse(BaseModel):
    id: uuid.UUID
    portfolio_id: uuid.UUID
    graph_snapshot_id: Optional[uuid.UUID] = None
    graph_snapshot_version: Optional[int] = 1
    query_type: str
    entity_id: uuid.UUID
    generated_explanation: str
    confidence_score: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
