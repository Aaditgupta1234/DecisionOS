"""Unit tests for Phase 12.8 Snapshot Models and Enums."""

import uuid
from datetime import date, datetime, timezone
import pytest
from app.execution.constants import (
    PortfolioMomentumGrade,
    SnapshotChangeSeverity,
    SnapshotGenerationStatus,
    SnapshotIntegrityStatus,
    SnapshotQualityLevel,
    SnapshotRetentionCategory,
    SnapshotTriggerSource,
    TrendDirection,
    calculate_change_severity,
    calculate_portfolio_momentum_grade,
    calculate_snapshot_checksum,
    calculate_snapshot_completeness,
    calculate_snapshot_coverage_rate,
    calculate_snapshot_quality_level,
    calculate_trend_direction,
    verify_snapshot_checksum,
)
from app.execution.models.snapshot import (
    InitiativeSnapshot,
    PortfolioSnapshot,
    ProgramSnapshot,
)


def test_snapshot_helpers_and_quality():
    """Validates completeness score, coverage rate, quality level, and checksum helpers."""
    # Completeness
    assert calculate_snapshot_completeness(10, 10) == 100.0
    assert calculate_snapshot_completeness(8, 10) == 80.0
    assert calculate_snapshot_completeness(0, 0) == 100.0

    # Coverage
    assert calculate_snapshot_coverage_rate(150, 200) == 75.0
    assert calculate_snapshot_coverage_rate(200, 200) == 100.0

    # Quality Level
    assert calculate_snapshot_quality_level(95.0) == SnapshotQualityLevel.EXCELLENT
    assert calculate_snapshot_quality_level(82.0) == SnapshotQualityLevel.GOOD
    assert calculate_snapshot_quality_level(65.0) == SnapshotQualityLevel.PARTIAL
    assert calculate_snapshot_quality_level(45.0) == SnapshotQualityLevel.LIMITED

    # Change Severity
    assert calculate_change_severity(2.5) == SnapshotChangeSeverity.MINOR
    assert calculate_change_severity(8.0) == SnapshotChangeSeverity.MODERATE
    assert calculate_change_severity(22.0) == SnapshotChangeSeverity.MAJOR
    assert calculate_change_severity(35.0) == SnapshotChangeSeverity.CRITICAL

    # Momentum Grade
    assert calculate_portfolio_momentum_grade(90.0) == PortfolioMomentumGrade.ACCELERATING
    assert calculate_portfolio_momentum_grade(75.0) == PortfolioMomentumGrade.POSITIVE
    assert calculate_portfolio_momentum_grade(60.0) == PortfolioMomentumGrade.NEUTRAL
    assert calculate_portfolio_momentum_grade(40.0) == PortfolioMomentumGrade.NEGATIVE
    assert calculate_portfolio_momentum_grade(20.0) == PortfolioMomentumGrade.COLLAPSING


def test_checksum_calculation_and_verification():
    """Validates cryptographic SHA-256 generation and audit verification."""
    payload = {"kpi": "revenue", "score": 92.5, "initiatives": ["init-1", "init-2"]}
    checksum = calculate_snapshot_checksum(payload)
    assert len(checksum) == 64  # SHA-256 produces 64 hex characters

    # Valid check
    assert verify_snapshot_checksum(payload, checksum) == SnapshotIntegrityStatus.VALID

    # Tampered payload
    tampered = {"kpi": "revenue", "score": 99.9, "initiatives": ["init-1", "init-2"]}
    assert verify_snapshot_checksum(tampered, checksum) == SnapshotIntegrityStatus.INVALID

    # Empty expected checksum
    assert verify_snapshot_checksum(payload, "") == SnapshotIntegrityStatus.NOT_VERIFIED


def test_portfolio_snapshot_model_instantiation():
    """Validates full column initialization and defaults on PortfolioSnapshot model."""
    org_id = uuid.uuid4()
    parent_id = uuid.uuid4()
    user_id = uuid.uuid4()
    now = datetime.now(timezone.utc)

    snap = PortfolioSnapshot(
        organization_id=org_id,
        parent_snapshot_id=parent_id,
        snapshot_date=date.today(),
        snapshot_timestamp=now,
        is_baseline_snapshot=True,
        snapshot_retention_category=SnapshotRetentionCategory.AUDIT,
        snapshot_trigger_source=SnapshotTriggerSource.MANUAL,
        snapshot_created_by=user_id,
        generation_status=SnapshotGenerationStatus.SUCCESS,
        capture_duration_ms=450,
        portfolio_health_score=94.5,
        portfolio_risk_score=15.0,
        portfolio_governance_score=90.0,
        portfolio_outcome_attainment_rate=88.0,
        portfolio_roi_score=75.0,
        portfolio_strategic_maturity_score=85.0,
        snapshot_completeness_score=100.0,
        snapshot_coverage_rate=100.0,
        snapshot_quality_level=SnapshotQualityLevel.EXCELLENT,
        snapshot_checksum="abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
        source_initiative_count=20,
        source_program_count=4,
        source_outcome_count=45,
        source_benefit_count=30,
        source_risk_count=8,
        source_milestone_count=120,
        snapshot_payload={"state": "active"},
    )

    assert snap.is_baseline_snapshot is True
    assert snap.snapshot_retention_category == SnapshotRetentionCategory.AUDIT
    assert snap.snapshot_trigger_source == SnapshotTriggerSource.MANUAL
    assert snap.parent_snapshot_id == parent_id
    assert snap.portfolio_health_score == 94.5
    assert snap.source_initiative_count == 20
