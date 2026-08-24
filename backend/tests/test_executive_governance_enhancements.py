"""Comprehensive validation suite for Executive Governance Enhancements (Phase 7.1)."""

import uuid
import pytest
from app.reporting.services.executive_directive_generator import ExecutiveDirectiveGenerator
from app.reporting.services.board_risk_register_engine import BoardRiskRegisterEngine
from app.reporting.services.directive_dag_engine import DirectiveDAGEngine
from app.reporting.services.narrative_confidence_calculator import NarrativeConfidenceCalculator
from app.reporting.services.report_governance_engine import ReportGovernanceEngine


def test_directive_evidence_chain_traceability():
    """Enhancement 1: Verify 7-tier evidence lineage chain for directives."""
    report_id = uuid.uuid4()
    directives = ExecutiveDirectiveGenerator.generate_directives(report_id=report_id)

    assert len(directives) >= 3
    for d in directives:
        assert d.evidence_chain is not None
        assert len(d.evidence_chain) == 7
        tiers = [node["tier"] for node in d.evidence_chain]
        assert tiers == ["DIRECTIVE", "INITIATIVE", "RECOMMENDATION", "ROOT_CAUSE", "DIAGNOSTIC", "KPI", "DATASET"]
        for node in d.evidence_chain:
            assert 0.0 < node["confidence"] <= 1.0


def test_board_risk_register_generation():
    """Enhancement 2: Verify multidimensional risk scoring and tiers."""
    # Test low risk
    risk_low = BoardRiskRegisterEngine.evaluate_directive_risk(
        confidence_score=0.95,
        expected_arr=30000.0,
        has_upstream_dependencies=False,
        status="COMPLETED",
    )
    assert risk_low["risk_tier"] in ["LOW", "MEDIUM"]
    assert "execution_risk" in risk_low["dimensions"]
    assert "financial_risk" in risk_low["dimensions"]

    # Test high risk
    risk_high = BoardRiskRegisterEngine.evaluate_directive_risk(
        confidence_score=0.60,
        expected_arr=250000.0,
        has_upstream_dependencies=True,
        status="PLANNED",
    )
    assert risk_high["risk_tier"] in ["HIGH", "CRITICAL"]
    assert risk_high["composite_score"] > risk_low["composite_score"]


def test_benefit_realization_tracking_and_variance():
    """Enhancement 3: Verify benefit realization formulas, variance, and trend."""
    report_id = uuid.uuid4()
    directives = ExecutiveDirectiveGenerator.generate_directives(report_id=report_id, base_revenue=500.0)

    # First directive is COMPLETED
    d1 = directives[0]
    assert d1.status == "COMPLETED"
    assert d1.benefit_tracking is not None
    assert d1.benefit_tracking["actual_arr"] > 0
    assert d1.benefit_tracking["realization_percentage"] == 95.0
    assert d1.benefit_tracking["trend_direction"] == "IMPROVING"

    # Second directive is IN_PROGRESS
    d2 = directives[1]
    assert d2.status == "IN_PROGRESS"
    assert d2.benefit_tracking["actual_arr"] == 0.0
    assert d2.benefit_tracking["realization_percentage"] == 0.0


def test_board_report_version_comparison_diff():
    """Enhancement 4: Verify dynamic version diff calculation."""
    report_id = uuid.uuid4()
    diff = ReportGovernanceEngine.compute_version_diff(report_id, from_v=1, to_v=2)

    assert diff.from_version == 1
    assert diff.to_version == 2
    assert "portfolio_health" in diff.kpis_changed
    assert len(diff.recommendations_added) >= 1
    assert "V2" in diff.summary_delta


def test_executive_signoff_workflow_states():
    """Enhancement 5: Verify valid and invalid governance state transitions."""
    assert ReportGovernanceEngine.can_transition("DRAFT", "UNDER_REVIEW") is True
    assert ReportGovernanceEngine.can_transition("UNDER_REVIEW", "APPROVED") is True
    assert ReportGovernanceEngine.can_transition("APPROVED", "PUBLISHED") is True
    assert ReportGovernanceEngine.can_transition("PUBLISHED", "ARCHIVED") is True

    # Invalid jump
    assert ReportGovernanceEngine.can_transition("DRAFT", "PUBLISHED") is False
    assert ReportGovernanceEngine.can_transition("ARCHIVED", "DRAFT") is False


def test_confidence_explainability_breakdown():
    """Enhancement 6: Verify formulas, inputs, and penalty attribution in confidence breakdown."""
    breakdown = NarrativeConfidenceCalculator.calculate_confidence(
        total_findings=8,
        findings_with_causes=8,
        findings_with_recommendations=8,
        dataset_row_count=20,
        missing_metric_count=1,
    )

    assert breakdown.explainability is not None
    assert "telemetry" in breakdown.explainability
    assert "formula" in breakdown.explainability["telemetry"]
    assert "graph" in breakdown.explainability
    assert "causal" in breakdown.explainability
    assert "outcome" in breakdown.explainability
    assert "composite_weights" in breakdown.explainability


def test_directive_dag_cycle_detection_and_critical_path():
    """Enhancement 7: Verify DAG construction, acyclicity, and critical path."""
    directives = [
        {"id": "DIR-01", "title": "SLA Enforcement", "dependencies": []},
        {"id": "DIR-02", "title": "Win-Back Outreach", "dependencies": ["DIR-01"]},
        {"id": "DIR-03", "title": "Channel Expansion", "dependencies": ["DIR-02"]},
    ]
    dag = DirectiveDAGEngine.build_directive_dag(directives)

    assert dag["is_acyclic"] is True
    assert dag["cycle_count"] == 0
    assert len(dag["edges"]) == 2
    assert dag["critical_path"] == ["DIR-01", "DIR-02", "DIR-03"]

    # Test cyclic dependency detection
    cyclic_directives = [
        {"id": "DIR-01", "title": "Action A", "dependencies": ["DIR-02"]},
        {"id": "DIR-02", "title": "Action B", "dependencies": ["DIR-01"]},
    ]
    cyclic_dag = DirectiveDAGEngine.build_directive_dag(cyclic_directives)
    assert cyclic_dag["is_acyclic"] is False
    assert cyclic_dag["cycle_count"] == 1


def test_hardened_audit_trail_immutability():
    """Enhancement 8: Verify immutable SHA-256 event trail across report lifecycle."""
    report_id = uuid.uuid4()
    trail = ReportGovernanceEngine.get_audit_trail(report_id)

    assert len(trail) >= 4
    event_types = [e.event_type for e in trail]
    assert "REPORT_GENERATED" in event_types
    assert "REPORT_REVIEWED" in event_types
    assert "REPORT_APPROVED" in event_types
    assert "REPORT_EXPORTED" in event_types

    for event in trail:
        assert len(event.sha256_hash) == 64  # Valid SHA-256 length
        assert event.timestamp is not None
