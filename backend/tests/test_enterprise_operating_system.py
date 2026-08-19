"""Unit tests for Phase 6.7–6.9 Unified Enterprise Governance, Competitive Intelligence & OS Platform."""

import uuid
import pytest
from app.enterprise_os.schemas.os_schemas import (
    EnterpriseDecisionCreateRequest,
    EnterpriseMemoryQueryRequest,
)
from app.enterprise_os.services.enterprise_decision_registry_engine import EnterpriseDecisionRegistryEngine
from app.enterprise_os.services.decision_outcome_attribution_engine import DecisionOutcomeAttributionEngine
from app.enterprise_os.services.decision_compliance_engine import DecisionComplianceEngine
from app.enterprise_os.services.governance_impact_engine import (
    GovernanceImpactEngine,
    BoardDirectiveEnforcementEngine,
)
from app.enterprise_os.services.benchmarking_engine import BenchmarkingEngine
from app.enterprise_os.services.opportunity_discovery_engine import (
    OpportunityDiscoveryEngine,
    BenchmarkScenarioGenerator,
)
from app.enterprise_os.services.competitive_intelligence_engine import CompetitiveIntelligenceEngine
from app.enterprise_os.services.enterprise_memory_engine import EnterpriseMemoryEngine
from app.enterprise_os.services.playbook_template_engine import (
    PlaybookTemplateEngine,
    PlaybookExecutionEngine,
)
from app.enterprise_os.services.enterprise_health_engine import (
    ApprovalGateEngine,
    WorkflowRecoveryEngine,
    EnterpriseHealthEngine,
)


def test_enterprise_decision_registry_lifecycle():
    """Test decision registry lifecycle and catalog."""
    portfolio_id = uuid.uuid4()
    req = EnterpriseDecisionCreateRequest(
        portfolio_id=portfolio_id,
        decision_code="DEC-2026-099",
        title="Q3 Autonomous Fulfillment Automation",
        decision_type="STRATEGIC",
        business_case="Authorize automated sorting to increase delivery throughput.",
        expected_value=250000.0,
        owner_role="VP Operations",
    )
    dec = EnterpriseDecisionRegistryEngine.create_decision(req)
    assert dec.decision_code == "DEC-2026-099"
    assert dec.status == "DRAFT"
    assert dec.expected_value == 250000.0

    decisions = EnterpriseDecisionRegistryEngine.get_sample_decisions(portfolio_id)
    assert len(decisions) == 3
    assert decisions[0].decision_code == "DEC-2026-042"
    assert decisions[0].actual_value == 312000.0


def test_decision_outcome_attribution():
    """Test closed-loop decision outcome attribution (91.8% accuracy)."""
    decision_id = uuid.uuid4()
    attr = DecisionOutcomeAttributionEngine.get_attribution(decision_id)

    assert attr.decision_id == decision_id
    assert attr.expected_arr == 340000.0
    assert attr.realized_arr == 312000.0
    assert attr.decision_accuracy_pct == 91.8
    assert attr.strategic_alignment_score == 96.0


def test_decision_compliance_enforcement():
    """Test policy rules compliance check."""
    decision_id = uuid.uuid4()
    comp = DecisionComplianceEngine.evaluate_compliance(decision_id)

    assert comp.compliance_status == "APPROVED"
    assert comp.risk_score == 24.0
    assert comp.evaluated_policy_count == 14
    assert len(comp.violations) == 0


def test_governance_impact_simulation():
    """Test pre-simulation of business and compliance impact."""
    decision_id = uuid.uuid4()
    sim = GovernanceImpactEngine.simulate_impact(decision_id)

    assert sim.expected_arr == 180000.0
    assert sim.expected_risk_delta_pct == 12.0
    assert sim.confidence_score == 94.5
    assert sim.recommendation == "RECOMMENDED_FOR_APPROVAL"

    scorecard = BoardDirectiveEnforcementEngine.get_governance_scorecard(uuid.uuid4())
    assert scorecard["governance_health_pct"] == 98.4
    assert scorecard["board_directives_enforced"] == 12


def test_benchmarking_and_provenance():
    """Test competitive benchmarks and verified data provenance (98% freshness)."""
    portfolio_id = uuid.uuid4()

    source = BenchmarkingEngine.get_benchmark_source()
    assert "SaaS Capital" in source.source_name
    assert source.freshness_score == 98.0
    assert source.confidence_score == 96.0

    benchmarks = BenchmarkingEngine.get_competitive_benchmarks(portfolio_id)
    assert len(benchmarks) == 3
    assert benchmarks[0].metric_name == "Customer Retention Rate"
    assert benchmarks[0].gap_to_median == -6.8


def test_opportunity_discovery_and_scenario_generation():
    """Test discovery of benchmark gaps and feeding the Digital Twin."""
    portfolio_id = uuid.uuid4()
    opps = OpportunityDiscoveryEngine.get_opportunities(portfolio_id)

    assert len(opps) == 2
    assert opps[0].potential_arr_gain == 340000.0

    # Test Benchmark -> Scenario Generator
    scenario_res = BenchmarkScenarioGenerator.generate_scenario_from_opportunity(opps[0].id)
    assert scenario_res.auto_scenario_id is not None
    assert scenario_res.status == "SCENARIO_GENERATED"


def test_competitive_intelligence_and_swot():
    """Test autonomous SWOT intelligence synthesis and market ranking."""
    portfolio_id = uuid.uuid4()
    snap = CompetitiveIntelligenceEngine.get_competitive_snapshot(portfolio_id)

    assert snap.market_rank == 4
    assert snap.percentile == 85.7
    assert len(snap.swot_strengths) >= 2
    assert len(snap.swot_opportunities) >= 2


def test_enterprise_institutional_memory():
    """Test querying institutional memory for Copilot."""
    req = EnterpriseMemoryQueryRequest(query_text="What happened with carrier reallocation last time?")
    records = EnterpriseMemoryEngine.query_memory(req)

    assert len(records) >= 2
    assert "Decision DEC-2026-042" in records[0].title
    assert records[0].outcome_rating == "HIGHLY_SUCCESSFUL"


def test_playbook_template_and_execution():
    """Test reusable playbook templates and quarterly execution runs."""
    templates = PlaybookTemplateEngine.get_templates()
    assert len(templates) == 2
    assert templates[0].template_code == "PBT-RETENTION-RECOVERY"
    assert len(templates[0].steps) == 5

    # Launch execution run
    exec_run = PlaybookExecutionEngine.launch_execution(templates[0].id)
    assert exec_run.execution_status == "SUCCESS"
    assert exec_run.execution_cost == 0.14
    assert len(exec_run.executed_steps) == 5


def test_approval_gates_and_workflow_recovery():
    """Test tiered approval gates and execution rollback compensation."""
    low_gate = ApprovalGateEngine.evaluate_gate("LOW")
    assert low_gate["auto_execute"] is True

    high_gate = ApprovalGateEngine.evaluate_gate("HIGH")
    assert high_gate["auto_execute"] is False
    assert high_gate["required_role"] == "EXECUTIVE"

    rb = WorkflowRecoveryEngine.rollback_execution(uuid.uuid4())
    assert rb["status"] == "ROLLED_BACK"
    assert len(rb["compensated_steps"]) == 2


def test_enterprise_health_and_command_center():
    """Test Enterprise Operating Score (94.8) and mission control summary."""
    health = EnterpriseHealthEngine.get_operating_health()
    assert health.operating_score == 94.8
    assert health.governance_health_pct == 98.4
    assert health.workflow_success_rate_pct == 97.2

    summary = EnterpriseHealthEngine.get_command_center_summary(uuid.uuid4())
    assert summary.operating_score == 94.8
    assert summary.market_percentile == 85.7
    assert summary.total_realized_arr == 312000.0
