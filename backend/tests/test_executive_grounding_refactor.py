"""Comprehensive validation tests for Phase 7.1 Executive Grounding & Dynamic Boardroom Intelligence."""

import uuid
import pytest
from app.reporting.services.executive_ownership_resolver import ExecutiveOwnershipResolver
from app.reporting.services.executive_impact_engine import ExecutiveImpactEngine
from app.reporting.services.narrative_confidence_calculator import NarrativeConfidenceCalculator
from app.reporting.services.executive_directive_generator import ExecutiveDirectiveGenerator
from app.reporting.services.presentation_deck_engine import PresentationDeckEngine
from app.reporting.services.executive_briefing_engine import ExecutiveBriefingEngine
from app.reporting.services.board_report_generator import BoardReportGenerator


def test_executive_ownership_resolution():
    """Verify dynamic mapping of domain and titles to C-suite roles."""
    assert ExecutiveOwnershipResolver.resolve_owner("Operational Logistics", "Carrier SLA Enforcement") == "Chief Operating Officer (COO)"
    assert ExecutiveOwnershipResolver.resolve_owner("Customer Retention", "Win-back campaign") == "Chief Marketing Officer (CMO)"
    assert ExecutiveOwnershipResolver.resolve_owner("Revenue Management", "Discount Containment") == "Chief Financial Officer (CFO)"
    assert ExecutiveOwnershipResolver.resolve_owner("AI Platform", "Digital Twin Monte Carlo") == "Head of Data & AI"
    assert ExecutiveOwnershipResolver.resolve_owner("Corporate", "Commercial Expansion") == "Chief Executive Officer (CEO)"


def test_arr_calculated_from_real_metrics_not_constants():
    """Verify that ARR recovery is dynamically calculated from baseline telemetry and not fixed literals."""
    # Test Baseline 1: Small dataset (Revenue = 275)
    impact_small = ExecutiveImpactEngine.calculate_impact(base_revenue=275.0, improvement_pct=0.15, severity="CRITICAL", is_completed=True)
    assert impact_small["expected_arr_impact"] > 0
    assert impact_small["actual_arr_impact"] is not None
    assert impact_small["achievement_percentage"] == 95.0
    assert impact_small["expected_health_impact"] == 11.0

    # Test Baseline 2: Enterprise dataset (Revenue = 100,000)
    impact_enterprise = ExecutiveImpactEngine.calculate_impact(base_revenue=100000.0, improvement_pct=0.15, severity="CRITICAL", is_completed=True)
    assert impact_enterprise["expected_arr_impact"] == round(100000.0 * 12.0 * 50.0 * 0.15, 2)
    assert impact_enterprise["expected_arr_impact"] != impact_small["expected_arr_impact"]


def test_confidence_scores_not_hardcoded():
    """Verify confidence breakdown varies dynamically based on data quality and coverage."""
    conf_perfect = NarrativeConfidenceCalculator.calculate_confidence(
        total_findings=10,
        findings_with_causes=10,
        findings_with_recommendations=10,
        dataset_row_count=50,
        missing_metric_count=0,
        total_kpis=10,
    )
    assert conf_perfect.overall >= 0.90
    assert conf_perfect.telemetry >= 0.90

    conf_degraded = NarrativeConfidenceCalculator.calculate_confidence(
        total_findings=10,
        findings_with_causes=2,
        findings_with_recommendations=2,
        dataset_row_count=5,
        missing_metric_count=5,
        total_kpis=10,
    )
    assert conf_degraded.overall < conf_perfect.overall
    assert conf_degraded.graph < conf_perfect.graph
    assert conf_degraded.causal < conf_perfect.causal


def test_directives_generated_dynamically_from_recommendations():
    """Verify Board Directives are dynamically compiled with owners, ARR, and health impact."""
    report_id = uuid.uuid4()
    custom_recs = [
        {
            "title": "Hospital Bed Utilization Protocol",
            "description": "Optimize patient discharge scheduling across regional emergency wings.",
            "domain": "Healthcare Logistics",
            "severity": "CRITICAL",
            "status": "IN_PROGRESS",
            "due_days": 45,
            "improvement_pct": 0.25,
            "finding_title": "Elevated Emergency Department Wait Times",
            "kpi": "bed_occupancy_rate",
        }
    ]

    directives = ExecutiveDirectiveGenerator.generate_directives(
        report_id=report_id,
        recommendations=custom_recs,
        base_revenue=500.0,
    )

    assert len(directives) == 1
    assert directives[0].title == "Hospital Bed Utilization Protocol"
    assert directives[0].owner == "Chief Operating Officer (COO)"
    assert directives[0].status == "IN_PROGRESS"
    assert directives[0].actual_arr_impact is None  # In progress


def test_dataset_mutation_sensitivity_validation():
    """Verify reports and directives change 100% when underlying dataset metrics mutate."""
    report_id = uuid.uuid4()

    # Dataset A (E-Commerce)
    briefing_a = ExecutiveBriefingEngine.generate_briefing(
        persona="CEO",
        health_score=85.0,
        base_revenue=275.0,
        delivery_days=6.2,
        retention_rate=0.0,
    )
    directives_a = ExecutiveDirectiveGenerator.generate_directives(report_id=report_id, base_revenue=275.0)

    # Dataset B (Enterprise SaaS)
    briefing_b = ExecutiveBriefingEngine.generate_briefing(
        persona="CEO",
        health_score=92.5,
        base_revenue=150000.0,
        delivery_days=1.1,
        retention_rate=88.5,
    )
    directives_b = ExecutiveDirectiveGenerator.generate_directives(report_id=report_id, base_revenue=150000.0)

    # Directives and briefing narratives must NOT be identical
    assert briefing_a["summary"] != briefing_b["summary"]
    assert briefing_a["key_metrics"]["health_score"] != briefing_b["key_metrics"]["health_score"]
    assert briefing_a["key_metrics"]["arr_recovery"] != briefing_b["key_metrics"]["arr_recovery"]
    assert directives_a[0].expected_arr_impact != directives_b[0].expected_arr_impact


def test_presentation_deck_contains_dataset_specific_content():
    """Verify 8-slide boardroom presentation deck reflects dataset-specific telemetry."""
    report_id = uuid.uuid4()
    deck = PresentationDeckEngine.generate_deck(
        report_id=report_id,
        health_score=88.0,
        baseline_health=70.0,
        base_revenue=1000.0,
        retention_rate=15.0,
        delivery_days=4.2,
    )

    assert len(deck) == 8
    # Slide 2 contains dynamic health score
    assert "88.0" in deck[1].slide_title
    assert "+18.0 pts" in deck[1].slide_title
    # Slide 3 contains dynamic delivery days
    assert "4.2 days" in deck[2].bullet_points[0]
