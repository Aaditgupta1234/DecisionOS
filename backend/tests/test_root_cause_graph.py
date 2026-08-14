"""Unit tests for pure Python RootCauseGraph Directed Acyclic Graph (DAG)."""

import uuid
import pytest

from app.core.constants import FindingSeverity, FindingType
from app.models.diagnostic_finding import DiagnosticFinding
from app.root_cause.graph import RootCauseGraph


def create_mock_finding(title: str, subtype: str) -> DiagnosticFinding:
    """Helper creating an in-memory DiagnosticFinding."""
    return DiagnosticFinding(
        id=uuid.uuid4(),
        dataset_id=uuid.uuid4(),
        finding_type=FindingType.REVENUE_DROP,
        severity=FindingSeverity.HIGH,
        title=title,
        description="...",
        business_impact="...",
        confidence_score=0.90,
        supporting_data={"category": "GENERAL", "subtype": subtype},
    )


def test_graph_node_and_edge_addition():
    """Verifies adding vertices and directed causal edges."""
    graph = RootCauseGraph()

    f1 = create_mock_finding("Delivery Delays", "DELIVERY_DELAY")
    f2 = create_mock_finding("Customer Churn", "CHURN_INCREASE")

    graph.add_node(f1)
    graph.add_node(f2)

    assert len(graph.nodes) == 2

    added = graph.add_edge(
        source_id=str(f1.id),
        target_id=str(f2.id),
        relationship_type="AMPLIFIES",
        relationship_strength="STRONG",
        confidence_score=0.85,
        impact_score=0.88,
    )
    assert added is True
    assert len(graph.get_edges()) == 1


def test_graph_cycle_detection_and_rejection():
    """Verifies that cyclical edges (A -> B -> C -> A) are blocked and rejected."""
    graph = RootCauseGraph()

    f_a = create_mock_finding("Finding A", "SUB_A")
    f_b = create_mock_finding("Finding B", "SUB_B")
    f_c = create_mock_finding("Finding C", "SUB_C")

    for f in (f_a, f_b, f_c):
        graph.add_node(f)

    # A -> B -> C
    assert graph.add_edge(str(f_a.id), str(f_b.id), "CAUSES", "STRONG", 0.8, 0.8) is True
    assert graph.add_edge(str(f_b.id), str(f_c.id), "CAUSES", "STRONG", 0.8, 0.8) is True

    # Attempting C -> A (would create a cycle: A -> B -> C -> A)
    cycle_edge_added = graph.add_edge(str(f_c.id), str(f_a.id), "CAUSES", "STRONG", 0.8, 0.8)
    assert cycle_edge_added is False
    assert graph.has_cycle() is False


def test_multi_hop_causal_chains_and_root_cause_discovery():
    """Verifies discovery of ultimate root causes and full multi-hop causal chains."""
    # Chain: Delivery Delay (Root) -> Customer Churn (Intermed) -> Revenue Decline (Symptom)
    graph = RootCauseGraph()

    f_deliv = create_mock_finding("Delivery Delay", "DELIVERY_DELAY")
    f_churn = create_mock_finding("Customer Churn", "CHURN_INCREASE")
    f_rev = create_mock_finding("Revenue Decline", "DECLINE")

    for f in (f_deliv, f_churn, f_rev):
        graph.add_node(f)

    graph.add_edge(str(f_deliv.id), str(f_churn.id), "AMPLIFIES", "STRONG", 0.85, 0.80)
    graph.add_edge(str(f_churn.id), str(f_rev.id), "CAUSES", "VERY_STRONG", 0.90, 0.95)

    # Direct cause of Revenue Decline should be Customer Churn
    direct_causes = graph.get_direct_causes(str(f_rev.id))
    assert direct_causes == [str(f_churn.id)]

    # Ultimate root cause of Revenue Decline should be Delivery Delay
    ultimate_roots = graph.get_root_causes(str(f_rev.id))
    assert ultimate_roots == [str(f_deliv.id)]

    # Full causal chain
    chains = graph.get_causal_chains(str(f_rev.id))
    assert len(chains) == 1
    assert chains[0] == [str(f_deliv.id), str(f_churn.id), str(f_rev.id)]


def test_graph_serialization_to_dict():
    """Verifies JSON serializable export."""
    graph = RootCauseGraph()
    f1 = create_mock_finding("F1", "S1")
    f2 = create_mock_finding("F2", "S2")

    graph.add_node(f1)
    graph.add_node(f2)
    graph.add_edge(str(f1.id), str(f2.id), "CAUSES", "STRONG", 0.9, 0.85)

    d = graph.to_dict()
    assert "nodes" in d
    assert "edges" in d
    assert len(d["nodes"]) == 2
    assert len(d["edges"]) == 1
    assert d["edges"][0]["source_id"] == str(f1.id)
    assert d["edges"][0]["target_id"] == str(f2.id)
