"""Unit tests for Anti-Hallucination Validation Engine and Governance Scorecard."""

import uuid
import pytest
from app.reporting.services.report_verification_engine import ReportVerificationEngine
from app.reporting.services.executive_directive_generator import ExecutiveDirectiveGenerator
from app.reporting.services.narrative_confidence_calculator import NarrativeConfidenceCalculator


def test_anti_hallucination_validation_passes_valid_directives():
    """Verify validation passes and permits publication for fully data-grounded reports."""
    report_id = uuid.uuid4()
    directives = ExecutiveDirectiveGenerator.generate_directives(report_id=report_id)
    confidence = NarrativeConfidenceCalculator.calculate_confidence()

    validation = ReportVerificationEngine.validate_anti_hallucination(
        directives=[d.model_dump() for d in directives],
        confidence_breakdown=confidence.model_dump(),
    )

    assert validation["is_valid"] is True
    assert validation["can_publish"] is True
    assert len(validation["blocking_errors"]) == 0
    assert validation["governance_scorecard"]["overall_governance_health"] > 95.0
    assert validation["governance_scorecard"]["evidence_coverage"] == 100.0


def test_anti_hallucination_validation_blocks_orphan_or_ungrounded_directives():
    """Verify validation fails and blocks publication when an ungrounded directive is introduced."""
    bad_directives = [
        {
            "id": "DIR-MOCK",
            "title": "Hallucinated Directive Without Evidence",
            "expected_arr_impact": 500000.0,
            "evidence_chain": [],  # Broken lineage
        }
    ]

    validation = ReportVerificationEngine.validate_anti_hallucination(directives=bad_directives)

    assert validation["is_valid"] is False
    assert validation["can_publish"] is False
    assert len(validation["blocking_errors"]) > 0
    assert validation["governance_scorecard"]["overall_governance_health"] < 70.0
