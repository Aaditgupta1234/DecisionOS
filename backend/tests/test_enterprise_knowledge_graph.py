"""Unit tests for Phase 5.5 Enterprise Knowledge Graph & Causal Intelligence."""

import uuid
import pytest
from app.knowledge_graph.services.knowledge_graph_builder import KnowledgeGraphBuilder
from app.knowledge_graph.services.graph_diff_engine import GraphDiffEngine
from app.knowledge_graph.services.causal_intelligence_engine import CausalIntelligenceEngine
from app.knowledge_graph.services.outcome_attribution_engine import OutcomeAttributionEngine
from app.knowledge_graph.services.impact_propagation_engine import ImpactPropagationEngine
from app.knowledge_graph.services.recommendation_effectiveness_engine import (
    RecommendationEffectivenessEngine,
)
from app.knowledge_graph.services.initiative_intelligence_engine import (
    InitiativeIntelligenceEngine,
)
from app.knowledge_graph.services.explainability_engine import ExplainabilityEngine


def test_knowledge_graph_builder_and_topology():
    """Test standard node and edge generation, and DAG topology."""
    portfolio_id = uuid.uuid4()
    res = KnowledgeGraphBuilder.build_graph(portfolio_id, snapshot_version=1)

    assert res.portfolio_id == portfolio_id
    assert res.snapshot_version == 1
    assert res.total_nodes >= 20
    assert res.total_edges >= 12
    assert res.topological_density > 0.0

    node_types = {n.node_type for n in res.nodes}
    assert "DATASET" in node_types
    assert "KPI" in node_types
    assert "FINDING" in node_types
    assert "ROOT_CAUSE" in node_types
    assert "RECOMMENDATION" in node_types
    assert "INITIATIVE" in node_types
    assert "OUTCOME" in node_types

    edge_types = {e.relationship_type for e in res.edges}
    assert "CAUSES" in edge_types
    assert "RECOMMENDED" in edge_types
    assert "RESULTED_IN" in edge_types


def test_graph_health_and_acyclicity():
    """Test DAG acyclicity, zero cycle violations, and health score."""
    portfolio_id = uuid.uuid4()
    health = KnowledgeGraphBuilder.get_health(portfolio_id, snapshot_version=1)

    assert health.portfolio_id == portfolio_id
    assert health.graph_health_score >= 95.0
    assert health.cycle_count == 0
    assert health.broken_edges == 0
    assert health.unreachable_nodes == 0
    assert health.ai_ready is True
    assert health.freshness_score >= 90.0


def test_graph_coverage_and_entity_statistics():
    """Test provenance coverage and instant entity statistics."""
    portfolio_id = uuid.uuid4()
    cov = KnowledgeGraphBuilder.get_coverage(portfolio_id)
    assert cov.portfolio_id == portfolio_id
    assert cov.coverage_percentage == 100.0
    assert cov.datasets_covered == cov.datasets_total == 18
    assert cov.recommendations_covered == cov.recommendations_total == 51

    stats = KnowledgeGraphBuilder.get_statistics(portfolio_id)
    assert stats.portfolio_id == portfolio_id
    assert stats.total_entities == 410
    assert stats.kpis_count == 24
    assert stats.findings_count == 142
    assert stats.root_causes_count == 53


def test_graph_snapshot_diff_engine():
    """Test snapshot diffing engine comparing two graph versions."""
    portfolio_id = uuid.uuid4()
    from_id = uuid.uuid4()
    to_id = uuid.uuid4()

    diff = GraphDiffEngine.compare_snapshots(
        portfolio_id=portfolio_id,
        from_snapshot_id=from_id,
        to_snapshot_id=to_id,
        from_version=1,
        to_version=2,
    )

    assert diff.portfolio_id == portfolio_id
    assert diff.from_version == 1
    assert diff.to_version == 2
    assert diff.nodes_added == 8
    assert diff.edges_added == 15
    assert diff.health_score_delta == +4.3
    assert len(diff.change_details["recommendations_added"]) >= 1


def test_causal_intelligence_chain():
    """Test multi-hop causal provenance reconstruction."""
    portfolio_id = uuid.uuid4()
    rc_id = uuid.uuid4()

    chain = CausalIntelligenceEngine.get_causal_chain(portfolio_id, rc_id)

    assert chain.portfolio_id == portfolio_id
    assert chain.root_cause_id == rc_id
    assert chain.outcome_status == "SUCCESS"
    assert chain.causal_strength >= 0.90
    assert len(chain.path_steps) == 5
    assert chain.path_steps[0].node_type == "ROOT_CAUSE"
    assert chain.path_steps[-1].node_type == "OUTCOME"
    assert len(chain.sha256_hash) == 64


def test_outcome_attribution_engine():
    """Test multi-touch value attribution and rankings."""
    portfolio_id = uuid.uuid4()
    res = OutcomeAttributionEngine.get_attributions(portfolio_id)

    assert res.portfolio_id == portfolio_id
    assert len(res.top_arr_producing_recommendations) >= 3
    assert len(res.top_health_improving_initiatives) >= 2

    top_rec = res.top_arr_producing_recommendations[0]
    assert top_rec.arr_contribution == 124000.0
    assert top_rec.attribution_score >= 0.85


def test_impact_propagation_engine():
    """Test multi-hop downstream ripple effect modeling."""
    portfolio_id = uuid.uuid4()
    node_id = uuid.uuid4()

    res = ImpactPropagationEngine.calculate_propagation(
        portfolio_id,
        node_id,
        source_node_name="Delivery Latency",
        propagation_depth=3,
    )

    assert res.portfolio_id == portfolio_id
    assert res.impact_score > 70.0
    assert len(res.affected_nodes) == 4

    csat_node = next(n for n in res.affected_nodes if "CSAT" in n.node_name)
    assert csat_node.hop_depth == 1
    assert csat_node.direction == "NEGATIVE"


def test_recommendation_effectiveness_and_lifecycle():
    """Test recommendation ranking by empirical evidence strength."""
    portfolio_id = uuid.uuid4()
    res = RecommendationEffectivenessEngine.rank_recommendations(portfolio_id)

    assert res.portfolio_id == portfolio_id
    assert res.total_ranked_recommendations == 4

    top_rank = res.rankings[0]
    assert top_rank.verification_count == 42
    assert top_rank.evidence_strength == "VERY_HIGH"
    assert top_rank.success_rate_pct > 90.0
    assert top_rank.lifecycle_status == "ACTIVE"


def test_initiative_intelligence_profiling():
    """Test initiative execution reliability and ROI profiling."""
    portfolio_id = uuid.uuid4()
    res = InitiativeIntelligenceEngine.profile_initiatives(portfolio_id)

    assert res.portfolio_id == portfolio_id
    assert res.total_profiles == 4

    init1 = next(p for p in res.profiles if p.initiative_id == "INIT-2026-001")
    assert init1.reliability_score > 90.0
    assert init1.roi_multiplier == 4.8
    assert init1.outcome_consistency == "VERY_HIGH"


def test_enterprise_explainability_engine():
    """Test deterministic graph-grounded query explanations."""
    portfolio_id = uuid.uuid4()
    entity_id = uuid.uuid4()

    exp = ExplainabilityEngine.explain_entity(
        portfolio_id,
        query_type="ROOT_CAUSE",
        entity_id=entity_id,
        snapshot_version=1,
    )

    assert exp.query_type == "ROOT_CAUSE"
    assert exp.confidence_score >= 0.85
    assert exp.confidence_breakdown.telemetry_confidence == 0.92
    assert exp.confidence_breakdown.causal_confidence == 0.87
    assert len(exp.provenance_chain) >= 3
    assert "Secondary Hub Dispatch Bottleneck" in exp.explanation
