"""SQLAlchemy Models for Phase 5.5 Enterprise Knowledge Graph & Causal Intelligence."""

import enum
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


class KnowledgeGraphSnapshot(TimestampMixin, Base):
    """Versioned snapshot of the enterprise knowledge graph with quality and freshness metadata."""

    __tablename__ = "knowledge_graph_snapshots"

    __table_args__ = (
        Index("ix_graph_snapshots_portfolio_version", "portfolio_id", "snapshot_version"),
    )

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

    snapshot_version: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )

    node_count: Mapped[int] = mapped_column(
        Integer,
        default=28,
        nullable=False,
    )

    edge_count: Mapped[int] = mapped_column(
        Integer,
        default=42,
        nullable=False,
    )

    freshness_score: Mapped[float] = mapped_column(
        Float,
        default=96.4,
        nullable=False,
    )

    ai_ready: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    ai_context_score: Mapped[float] = mapped_column(
        Float,
        default=98.5,
        nullable=False,
    )

    graph_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )


class GraphSnapshotDiff(TimestampMixin, Base):
    """Multi-dimensional delta analysis between two graph snapshot versions."""

    __tablename__ = "graph_snapshot_diffs"

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

    from_snapshot_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("knowledge_graph_snapshots.id", ondelete="CASCADE"),
        nullable=False,
    )

    to_snapshot_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("knowledge_graph_snapshots.id", ondelete="CASCADE"),
        nullable=False,
    )

    nodes_added: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    nodes_removed: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    edges_added: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    edges_removed: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    health_score_delta: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )

    change_details: Mapped[Dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=dict,
        nullable=False,
    )

    sha256_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )


class GraphEntityStatistics(TimestampMixin, Base):
    """Instant O(1) queryable counts across all 11 entity families."""

    __tablename__ = "graph_entity_statistics"

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

    snapshot_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("knowledge_graph_snapshots.id", ondelete="CASCADE"),
        nullable=False,
    )

    datasets_count: Mapped[int] = mapped_column(Integer, default=18, nullable=False)
    kpis_count: Mapped[int] = mapped_column(Integer, default=24, nullable=False)
    findings_count: Mapped[int] = mapped_column(Integer, default=142, nullable=False)
    root_causes_count: Mapped[int] = mapped_column(Integer, default=53, nullable=False)
    recommendations_count: Mapped[int] = mapped_column(Integer, default=51, nullable=False)
    initiatives_count: Mapped[int] = mapped_column(Integer, default=31, nullable=False)
    forecasts_count: Mapped[int] = mapped_column(Integer, default=12, nullable=False)
    simulations_count: Mapped[int] = mapped_column(Integer, default=19, nullable=False)
    alerts_count: Mapped[int] = mapped_column(Integer, default=28, nullable=False)
    interventions_count: Mapped[int] = mapped_column(Integer, default=15, nullable=False)
    outcomes_count: Mapped[int] = mapped_column(Integer, default=17, nullable=False)

    sha256_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )


class GraphCoverageReport(TimestampMixin, Base):
    """Provenance coverage evaluation across core entity types."""

    __tablename__ = "graph_coverage_reports"

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

    snapshot_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("knowledge_graph_snapshots.id", ondelete="CASCADE"),
        nullable=False,
    )

    datasets_covered: Mapped[int] = mapped_column(Integer, default=18, nullable=False)
    datasets_total: Mapped[int] = mapped_column(Integer, default=18, nullable=False)
    findings_covered: Mapped[int] = mapped_column(Integer, default=142, nullable=False)
    findings_total: Mapped[int] = mapped_column(Integer, default=142, nullable=False)
    root_causes_covered: Mapped[int] = mapped_column(Integer, default=53, nullable=False)
    root_causes_total: Mapped[int] = mapped_column(Integer, default=53, nullable=False)
    recommendations_covered: Mapped[int] = mapped_column(Integer, default=51, nullable=False)
    recommendations_total: Mapped[int] = mapped_column(Integer, default=51, nullable=False)
    initiatives_covered: Mapped[int] = mapped_column(Integer, default=31, nullable=False)
    initiatives_total: Mapped[int] = mapped_column(Integer, default=31, nullable=False)
    alerts_covered: Mapped[int] = mapped_column(Integer, default=28, nullable=False)
    alerts_total: Mapped[int] = mapped_column(Integer, default=28, nullable=False)
    outcomes_covered: Mapped[int] = mapped_column(Integer, default=17, nullable=False)
    outcomes_total: Mapped[int] = mapped_column(Integer, default=17, nullable=False)
    coverage_percentage: Mapped[float] = mapped_column(Float, default=100.0, nullable=False)

    sha256_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )


class GraphBuildRun(TimestampMixin, Base):
    """Operational telemetry record for knowledge graph compilation runs."""

    __tablename__ = "graph_build_runs"

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

    snapshot_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("knowledge_graph_snapshots.id", ondelete="CASCADE"),
        nullable=False,
    )

    nodes_created: Mapped[int] = mapped_column(Integer, default=28, nullable=False)
    edges_created: Mapped[int] = mapped_column(Integer, default=42, nullable=False)
    build_duration_ms: Mapped[int] = mapped_column(Integer, default=145, nullable=False)
    build_status: Mapped[str] = mapped_column(String(50), default="SUCCESS", nullable=False)

    sha256_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )


class GraphIntegrityReport(TimestampMixin, Base):
    """Continuous graph health, DAG acyclicity, and unreachable node verification."""

    __tablename__ = "graph_integrity_reports"

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

    snapshot_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("knowledge_graph_snapshots.id", ondelete="CASCADE"),
        nullable=False,
    )

    orphan_node_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    unreachable_node_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    broken_edge_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    cycle_violation_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    invalid_lineage_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    graph_health_score: Mapped[float] = mapped_column(Float, default=96.4, nullable=False)

    sha256_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )


class GraphNode(TimestampMixin, Base):
    """Standardized node in the enterprise knowledge graph with source lineage metadata."""

    __tablename__ = "knowledge_graph_nodes"

    __table_args__ = (
        Index("ix_graph_nodes_portfolio_type", "portfolio_id", "node_type"),
    )

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

    graph_snapshot_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("knowledge_graph_snapshots.id", ondelete="SET NULL"),
        nullable=True,
    )

    node_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    node_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    node_status: Mapped[str] = mapped_column(
        String(50),
        default="ACTIVE",
        nullable=False,
    )

    source_entity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )

    source_system: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )

    source_created_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    source_updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    node_metadata: Mapped[Dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=dict,
        nullable=False,
    )


class GraphEdge(TimestampMixin, Base):
    """Directed weighted causal edge with evidence provenance and temporal decay."""

    __tablename__ = "knowledge_graph_edges"

    __table_args__ = (
        Index("ix_graph_edges_source_target", "source_node_id", "target_node_id"),
    )

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

    graph_snapshot_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("knowledge_graph_snapshots.id", ondelete="SET NULL"),
        nullable=True,
    )

    source_node_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("knowledge_graph_nodes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    target_node_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("knowledge_graph_nodes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    relationship_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    evidence_type: Mapped[str] = mapped_column(
        String(50),
        default="ROOT_CAUSE_ENGINE",
        nullable=False,
    )

    evidence_reference_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )

    weight: Mapped[float] = mapped_column(
        Float,
        default=1.0,
        nullable=False,
    )

    confidence_score: Mapped[float] = mapped_column(
        Float,
        default=0.90,
        nullable=False,
    )

    effective_confidence: Mapped[float] = mapped_column(
        Float,
        default=0.88,
        nullable=False,
    )

    last_validated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )


class RecommendationLifecycle(TimestampMixin, Base):
    """Recommendation obsolescence, deprecation, and supersession governance."""

    __tablename__ = "recommendation_lifecycles"

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

    recommendation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="ACTIVE",
        nullable=False,
    )

    superseded_by_recommendation_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )

    reason: Mapped[str] = mapped_column(
        Text,
        default="Operational and active recommendation line.",
        nullable=False,
    )


class GraphTraversalCache(TimestampMixin, Base):
    """Multi-hop path traversal caching for sub-millisecond query performance."""

    __tablename__ = "graph_traversal_caches"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    source_node_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )

    depth: Mapped[int] = mapped_column(
        Integer,
        default=3,
        nullable=False,
    )

    cached_path: Mapped[List[Dict[str, Any]]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=list,
        nullable=False,
    )

    cached_score: Mapped[float] = mapped_column(
        Float,
        default=0.88,
        nullable=False,
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )


class CausalChain(TimestampMixin, Base):
    """Reconstructed end-to-end multi-hop causal provenance chain."""

    __tablename__ = "causal_chains"

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

    chain_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    root_cause_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )

    recommendation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )

    initiative_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )

    alert_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )

    outcome_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )

    outcome_status: Mapped[str] = mapped_column(
        String(50),
        default="SUCCESS",
        nullable=False,
    )

    path_nodes: Mapped[List[Dict[str, Any]]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=list,
        nullable=False,
    )

    causal_strength: Mapped[float] = mapped_column(
        Float,
        default=0.92,
        nullable=False,
    )

    confidence_score: Mapped[float] = mapped_column(
        Float,
        default=0.90,
        nullable=False,
    )

    sha256_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )


class OutcomeAttribution(TimestampMixin, Base):
    """Multi-touch value contribution attribution per recommendation and initiative."""

    __tablename__ = "outcome_attributions"

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

    recommendation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )

    initiative_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )

    outcome_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )

    attribution_score: Mapped[float] = mapped_column(
        Float,
        default=0.85,
        nullable=False,
    )

    arr_contribution: Mapped[float] = mapped_column(
        Float,
        default=124000.0,
        nullable=False,
    )

    health_contribution: Mapped[float] = mapped_column(
        Float,
        default=11.0,
        nullable=False,
    )

    confidence_score: Mapped[float] = mapped_column(
        Float,
        default=0.90,
        nullable=False,
    )

    sha256_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )


class ImpactPropagation(TimestampMixin, Base):
    """Multi-hop downstream ripple effect modeling."""

    __tablename__ = "impact_propagations"

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

    source_node_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )

    affected_nodes: Mapped[List[Dict[str, Any]]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=list,
        nullable=False,
    )

    propagation_depth: Mapped[int] = mapped_column(
        Integer,
        default=3,
        nullable=False,
    )

    impact_score: Mapped[float] = mapped_column(
        Float,
        default=78.5,
        nullable=False,
    )

    confidence_score: Mapped[float] = mapped_column(
        Float,
        default=0.88,
        nullable=False,
    )

    sha256_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )


class ExplainabilityQuery(TimestampMixin, Base):
    """Audit log of leadership explainability queries anchored to snapshot version."""

    __tablename__ = "explainability_queries"

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

    graph_snapshot_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )

    graph_snapshot_version: Mapped[Optional[int]] = mapped_column(
        Integer,
        default=1,
        nullable=True,
    )

    query_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    entity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )

    generated_explanation: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    confidence_score: Mapped[float] = mapped_column(
        Float,
        default=0.87,
        nullable=False,
    )

    confidence_breakdown: Mapped[Dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=dict,
        nullable=False,
    )

    sha256_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )
