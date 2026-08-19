"""Unit tests for Phase 6.0 Explainable AI Business Analyst & Decision Copilot."""

import uuid
import pytest
from app.ai.services.guardrail_engine import GuardrailEngine
from app.ai.services.intent_classifier import IntentClassifier
from app.ai.services.context_builder import ContextBuilder
from app.ai.services.knowledge_retriever import KnowledgeRetriever
from app.ai.services.causal_explanation_engine import CausalExplanationEngine
from app.ai.services.ai_narrative_engine import AINarrativeEngine
from app.ai.services.decision_copilot import DecisionCopilot
from app.ai.services.response_verification_engine import ResponseVerificationEngine


def test_guardrail_engine():
    """Test AI Safety Guardrails query boundary enforcement."""
    supported = GuardrailEngine.evaluate_query("Why is customer retention dropping in the Southeast?")
    assert supported.guardrail_status == "SUPPORTED"
    assert supported.is_safe_to_execute is True

    speculative = GuardrailEngine.evaluate_query("Predict bitcoin stock market prices for next quarter")
    assert speculative.guardrail_status == "OUT_OF_SCOPE"
    assert speculative.is_safe_to_execute is False

    out_of_horizon = GuardrailEngine.evaluate_query("What will our revenue be in 2035?")
    assert out_of_horizon.guardrail_status == "INSUFFICIENT_EVIDENCE"
    assert out_of_horizon.is_safe_to_execute is False


def test_intent_classifier():
    """Test deterministic categorization across query intent families."""
    q1, conf1 = IntentClassifier.classify("Why is customer retention declining?")
    assert q1 == "ROOT_CAUSE_QUERY"
    assert conf1 >= 0.90

    q2, conf2 = IntentClassifier.classify("Which initiative generated the most ARR recovery?")
    assert q2 == "OUTCOME_QUERY"
    assert conf2 >= 0.90

    q3, conf3 = IntentClassifier.classify("What changed between Forecast V1 and V3?")
    assert q3 == "COMPARISON_QUERY"
    assert conf3 >= 0.90

    q4, conf4 = IntentClassifier.classify("What recommendations should we execute?")
    assert q4 == "RECOMMENDATION_QUERY"

    q5, conf5 = IntentClassifier.classify("What happens if we simulate a 20% logistics boost?")
    assert q5 == "SIMULATION_QUERY"


def test_context_builder_and_snapshot_pinning():
    """Test graph snapshot pinning and multi-engine context assembly."""
    portfolio_id = uuid.uuid4()
    context = ContextBuilder.build_pinned_context(portfolio_id, snapshot_version=2)

    assert context["pinned_snapshot_version"] == 2
    assert context["freshness_score"] >= 90.0
    assert context["ai_ready"] is True
    assert context["total_nodes"] >= 20
    assert context["total_edges"] >= 12
    assert len(context["nodes"]) == context["total_nodes"]


def test_knowledge_retriever_active_sources():
    """Test retrieval of active graph nodes, evidence items, and citations."""
    portfolio_id = uuid.uuid4()
    context = ContextBuilder.build_pinned_context(portfolio_id, snapshot_version=1)

    retrieval = KnowledgeRetriever.retrieve_evidence(context, "ROOT_CAUSE_QUERY", "Why is retention falling?")

    assert len(retrieval["evidence"]) >= 1
    assert len(retrieval["citations"]) >= 1

    cit = retrieval["citations"][0]
    assert cit.is_active_source is True
    assert cit.snapshot_version == "V1"
    assert len(cit.graph_path) >= 2


def test_causal_explanation_and_provenance_chain():
    """Test causal narrative generation and full 5-step provenance chain."""
    explanation = CausalExplanationEngine.generate_explanation(
        "ROOT_CAUSE_QUERY",
        "Why is retention declining?",
    )
    assert "Customer Retention declined by -7.3%" in explanation
    assert "Delivery Latency increasing to 5.4 days" in explanation
    assert "Carrier Rebalancing & Automated SLA Penalties" in explanation

    audit_id = uuid.uuid4()
    chain = CausalExplanationEngine.build_provenance_chain(audit_id)

    assert chain.audit_id == audit_id
    assert chain.chain_depth == 5
    assert len(chain.path_nodes) == 5
    assert chain.path_nodes[0]["type"] == "RESPONSE"
    assert chain.path_nodes[-1]["type"] == "DATASET"


def test_ai_narrative_engine():
    """Test structured executive markdown formatting."""
    raw = "Retention dropped due to hub latency."
    briefing = AINarrativeEngine.format_briefing(raw, "ROOT_CAUSE_QUERY")

    assert "### Executive Summary" in briefing
    assert "Key Diagnostic Findings:" in briefing
    assert "Primary Bottleneck:" in briefing


def test_decision_copilot_strategic_ranking():
    """Test strategic options ranking and DecisionPackage synthesis."""
    portfolio_id = uuid.uuid4()
    result = DecisionCopilot.evaluate_strategic_options(
        portfolio_id,
        "Which recovery path should we choose?",
        snapshot_version=1,
    )

    pkg = result["decision_package"]
    assert "Recovery Path A" in pkg.recommended_option
    assert pkg.expected_arr_recovery == 124000.0
    assert pkg.expected_health_lift == 11.0
    assert len(pkg.ranked_options) == 3
    assert pkg.ranked_options[0].rank == 1
    assert pkg.ranked_options[0].expected_arr == 124000.0
    assert len(pkg.supporting_evidence) >= 2
    assert len(pkg.risks) >= 1
    assert len(pkg.tradeoffs) >= 1


def test_response_verification_and_evidence_coverage():
    """Test runtime zero-hallucination verification and coverage reporting."""
    portfolio_id = uuid.uuid4()
    context = ContextBuilder.build_pinned_context(portfolio_id, snapshot_version=1)
    retrieval = KnowledgeRetriever.retrieve_evidence(context, "OUTCOME_QUERY", "Top ARR recommendation")

    passed, score, issues = ResponseVerificationEngine.verify_response(
        "Verified yield of $124K ARR",
        retrieval["citations"],
        retrieval["evidence"],
    )

    assert passed is True
    assert score == 100.0
    assert len(issues) == 0

    audit_id = uuid.uuid4()
    cov_report = ResponseVerificationEngine.generate_coverage_report(
        audit_id,
        retrieved_nodes_count=12,
        retrieved_edges_count=18,
        cited_nodes_count=5,
        cited_edges_count=7,
    )

    assert cov_report.audit_id == audit_id
    assert cov_report.retrieved_node_count == 12
    assert cov_report.cited_node_count == 5
    assert cov_report.citation_coverage_percentage == 40.0
    assert cov_report.unused_evidence_count == 18
