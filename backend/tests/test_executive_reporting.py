"""Unit tests for Phase 6.2 Executive Reporting & Boardroom Communication Platform."""

import uuid
import pytest
from app.reporting.services.executive_briefing_engine import ExecutiveBriefingEngine
from app.reporting.services.board_report_generator import BoardReportGenerator
from app.reporting.services.recovery_plan_generator import RecoveryPlanGenerator
from app.reporting.services.presentation_deck_engine import PresentationDeckEngine
from app.reporting.services.narrative_validation_engine import NarrativeValidationEngine
from app.reporting.services.report_verification_engine import ReportVerificationEngine
from app.reporting.services.report_governance_engine import ReportGovernanceEngine


def test_executive_briefing_engine():
    """Test persona-tailored executive summaries."""
    for persona in ["CEO", "COO", "CFO", "BOARD"]:
        data = ExecutiveBriefingEngine.generate_briefing(persona)
        assert data["persona"] == persona
        assert "title" in data
        assert "summary" in data
        assert "key_metrics" in data
        assert "executive_directive" in data


def test_board_report_generator():
    """Test comprehensive multi-section board report compilation."""
    portfolio_id = uuid.uuid4()
    report = BoardReportGenerator.generate_board_report(portfolio_id)

    assert "title" in report
    assert "executive_summary" in report
    assert len(report["sections"]) == 5
    assert report["evidence_coverage"]["coverage_percentage"] == 100.0


def test_recovery_plan_generator():
    """Test 30/60/90/180-day milestone recovery roadmap."""
    portfolio_id = uuid.uuid4()
    plan = RecoveryPlanGenerator.generate_plan(portfolio_id)

    assert len(plan["phases"]) == 4
    phase_names = [p["phase"] for p in plan["phases"]]
    assert phase_names == ["30_DAYS", "60_DAYS", "90_DAYS", "180_DAYS"]
    assert plan["total_target_arr"] == "$480,000"


def test_presentation_deck_with_ai_citations():
    """Test 8-slide presentation deck with embedded AI citations and speaker notes."""
    report_id = uuid.uuid4()
    slides = PresentationDeckEngine.generate_deck(report_id)

    assert len(slides) == 8
    assert slides[0].slide_type == "TITLE"
    assert slides[1].slide_type == "HEALTH_KPI"
    assert slides[2].slide_type == "ROOT_CAUSE"
    assert slides[3].slide_type == "RECOVERY_PATH"
    assert slides[4].slide_type == "SIMULATION"
    assert slides[5].slide_type == "FORECAST"
    assert slides[6].slide_type == "DIRECTIVES"
    assert slides[7].slide_type == "TITLE"

    # Verify AI citation injection
    for slide in slides:
        assert slide.citation_count >= 1
        assert len(slide.provenance_links) >= 1
        assert len(slide.speaker_notes) > 0


def test_narrative_validation_and_confidence():
    """Test narrative validation and 4-factor confidence scoring."""
    payload = {"summary": "Valid executive narrative"}
    res = NarrativeValidationEngine.validate_narrative(payload, 85.0, 14.1)

    assert res["is_valid"] is True
    assert res["report_quality_score"] == 96.8
    assert res["confidence_breakdown"].telemetry >= 0.80
    assert res["confidence_breakdown"].graph >= 0.80
    assert res["confidence_breakdown"].causal >= 0.80
    assert res["confidence_breakdown"].outcome >= 0.80
    assert res["confidence_breakdown"].overall >= 0.80


def test_report_integrity_verification():
    """Test cryptographic SHA-256 hash and snapshot verification."""
    report_id = uuid.uuid4()
    verify = ReportVerificationEngine.verify_report_integrity(report_id)

    assert verify.hash_valid is True
    assert verify.snapshot_valid is True
    assert verify.citations_valid is True
    assert verify.evidence_coverage == 100.0
    assert verify.report_quality_score == 96.8


def test_report_governance_diff_and_lineage():
    """Test version diffing, lineage graph generation, and audit trail."""
    report_id = uuid.uuid4()

    # Lineage graph
    lineage = ReportGovernanceEngine.get_lineage_graph(report_id)
    assert len(lineage.nodes) == 6
    assert len(lineage.edges) == 5
    assert lineage.coverage_percentage == 100.0

    # Version diff
    diff = ReportGovernanceEngine.compute_version_diff(report_id, 1, 2)
    assert diff.from_version == 1
    assert diff.to_version == 2
    assert "portfolio_health" in diff.kpis_changed
    assert len(diff.recommendations_added) >= 1

    # Audit trail
    trail = ReportGovernanceEngine.get_audit_trail(report_id)
    assert len(trail) == 4
    event_types = {e.event_type for e in trail}
    assert "REPORT_GENERATED" in event_types
    assert "REPORT_APPROVED" in event_types
    assert "REPORT_PUBLISHED" in event_types
