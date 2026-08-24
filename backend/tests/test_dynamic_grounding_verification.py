"""Forensic test suite for Dynamic Grounding & Governance Verification Audit."""

import uuid
import pytest
from app.reporting.services.executive_impact_engine import ExecutiveImpactEngine
from app.reporting.services.narrative_confidence_calculator import NarrativeConfidenceCalculator
from app.reporting.services.executive_directive_generator import ExecutiveDirectiveGenerator
from app.reporting.services.report_verification_engine import ReportVerificationEngine
from app.reporting.services.presentation_deck_engine import PresentationDeckEngine
from app.reporting.services.executive_briefing_engine import ExecutiveBriefingEngine


def test_claim_1_arr_attribution_is_fully_dynamic():
    """Claim 1: Verify ARR values change dynamically when underlying revenue metrics change."""
    # Low revenue baseline ($275/mo)
    impact_low = ExecutiveImpactEngine.calculate_impact(base_revenue=275.0, improvement_pct=0.20)
    # High revenue baseline ($10,000/mo)
    impact_high = ExecutiveImpactEngine.calculate_impact(base_revenue=10000.0, improvement_pct=0.20)

    assert impact_low["expected_arr_impact"] < impact_high["expected_arr_impact"]
    assert impact_high["expected_arr_impact"] == round(10000.0 * 12.0 * 50.0 * 0.20, 2)


def test_claim_2_confidence_engine_stress_scenarios():
    """Claim 2: Verify confidence scores respond to removed recommendations, causes, and missing telemetry."""
    # Scenario A: Baseline with full evidence
    conf_baseline = NarrativeConfidenceCalculator.calculate_confidence(
        total_findings=7,
        findings_with_causes=7,
        findings_with_recommendations=7,
        dataset_row_count=20,
        missing_metric_count=0,
    )

    # Scenario B: Missing Recommendations
    conf_no_recs = NarrativeConfidenceCalculator.calculate_confidence(
        total_findings=7,
        findings_with_causes=7,
        findings_with_recommendations=1,
        dataset_row_count=20,
        missing_metric_count=0,
    )
    assert conf_no_recs.outcome < conf_baseline.outcome
    assert conf_no_recs.overall < conf_baseline.overall

    # Scenario C: Missing Root Causes (Broken DAG)
    conf_broken_dag = NarrativeConfidenceCalculator.calculate_confidence(
        total_findings=7,
        findings_with_causes=1,
        findings_with_recommendations=7,
        dataset_row_count=20,
        missing_metric_count=0,
    )
    assert conf_broken_dag.graph < conf_baseline.graph
    assert conf_broken_dag.causal < conf_baseline.causal

    # Scenario D: Missing KPI Metrics
    conf_missing_kpis = NarrativeConfidenceCalculator.calculate_confidence(
        total_findings=7,
        findings_with_causes=7,
        findings_with_recommendations=7,
        dataset_row_count=20,
        missing_metric_count=4,
    )
    assert conf_missing_kpis.telemetry < conf_baseline.telemetry


def test_claim_3_directives_generated_from_distinct_recommendations():
    """Claim 3: Verify directives change completely when generated from different recommendations."""
    report_id = uuid.uuid4()
    # Logistics Recommendations
    recs_logistics = [
        {"title": "Logistics Dispatch Protocol", "domain": "Logistics", "severity": "CRITICAL", "status": "IN_PROGRESS", "kpi": "lead_time"}
    ]
    # SaaS Subscription Recommendations
    recs_saas = [
        {"title": "Annual Plan Seat Expansion", "domain": "Revenue", "severity": "HIGH", "status": "COMPLETED", "kpi": "mrr_growth"}
    ]

    dir_logistics = ExecutiveDirectiveGenerator.generate_directives(report_id=report_id, recommendations=recs_logistics)
    dir_saas = ExecutiveDirectiveGenerator.generate_directives(report_id=report_id, recommendations=recs_saas)

    assert dir_logistics[0].title == "Logistics Dispatch Protocol"
    assert dir_logistics[0].owner == "Chief Operating Officer (COO)"
    assert dir_saas[0].title == "Annual Plan Seat Expansion"
    assert dir_saas[0].owner == "Chief Financial Officer (CFO)"


def test_claim_5_anti_hallucination_gate_enforcement():
    """Claim 5: Verify anti-hallucination engine blocks ungrounded directives from publication."""
    # Test 1: Valid directives -> can_publish = True
    report_id = uuid.uuid4()
    valid_dirs = ExecutiveDirectiveGenerator.generate_directives(report_id=report_id)
    val_pass = ReportVerificationEngine.validate_anti_hallucination(directives=[d.model_dump() for d in valid_dirs])
    assert val_pass["can_publish"] is True

    # Test 2: Injected ungrounded directive -> can_publish = False
    fake_dirs = [{"id": "DIR-HALLUCINATED", "expected_arr_impact": 1000000.0, "evidence_chain": []}]
    val_fail = ReportVerificationEngine.validate_anti_hallucination(directives=fake_dirs)
    assert val_fail["can_publish"] is False
    assert len(val_fail["blocking_errors"]) > 0


def test_claim_8_dataset_mutation_sensitivity():
    """Claim 8: Verify executive briefings and presentation decks adapt dynamically to mutated metrics."""
    report_id = uuid.uuid4()
    # Telemetry Run 1 (Distressed Baseline: 6.2d delay, 0% retention)
    deck_distressed = PresentationDeckEngine.generate_deck(
        report_id=report_id,
        health_score=74.0,
        baseline_health=60.0,
        base_revenue=275.0,
        retention_rate=0.0,
        delivery_days=6.2,
    )

    # Telemetry Run 2 (Recovered Baseline: 2.1d delay, 85% retention)
    deck_recovered = PresentationDeckEngine.generate_deck(
        report_id=report_id,
        health_score=92.0,
        baseline_health=74.0,
        base_revenue=5000.0,
        retention_rate=85.0,
        delivery_days=2.1,
    )

    # Slide titles and bullet contents must be distinct
    assert deck_distressed[1].slide_title != deck_recovered[1].slide_title
    assert "0.0%" in deck_distressed[1].bullet_points[1]
    assert "85.0%" in deck_recovered[1].bullet_points[1]
    assert "6.2 days" in deck_distressed[2].bullet_points[0]
    assert "2.1 days" in deck_recovered[2].bullet_points[0]
