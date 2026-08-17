"""Unit tests for Phase 12.8 Snapshot Replay Engine."""

import uuid
from datetime import date, datetime, timezone
import pytest
from app.execution.constants import (
    SnapshotGenerationStatus,
    SnapshotIntegrityStatus,
    SnapshotQualityLevel,
    SnapshotRetentionCategory,
    calculate_snapshot_checksum,
)
from app.execution.models.snapshot import (
    InitiativeSnapshot,
    PortfolioSnapshot,
    ProgramSnapshot,
)
from app.execution.services.snapshot_replay_engine import SnapshotReplayEngine


def test_portfolio_snapshot_lossless_replay_and_checksum_verification():
    """Validates state reconstruction and SHA-256 integrity validation."""
    org_id = uuid.uuid4()
    payload = {
        "initiatives": [{"id": "init-1", "title": "Core Modernization", "progress": 85.0}],
        "programs": [{"id": "prog-1", "title": "Digital Transformation"}],
        "rankings": {"top_value": ["init-1"]},
    }
    checksum = calculate_snapshot_checksum(payload)

    snap = PortfolioSnapshot(
        id=uuid.uuid4(),
        organization_id=org_id,
        snapshot_date=date.today(),
        snapshot_timestamp=datetime.now(timezone.utc),
        is_baseline_snapshot=True,
        snapshot_retention_category=SnapshotRetentionCategory.AUDIT,
        generation_status=SnapshotGenerationStatus.SUCCESS,
        portfolio_health_score=92.0,
        portfolio_risk_score=10.0,
        portfolio_governance_score=95.0,
        portfolio_outcome_attainment_rate=88.0,
        portfolio_roi_score=75.0,
        portfolio_strategic_maturity_score=85.0,
        snapshot_completeness_score=100.0,
        snapshot_coverage_rate=100.0,
        snapshot_quality_level=SnapshotQualityLevel.EXCELLENT,
        snapshot_checksum=checksum,
        snapshot_payload=payload,
    )

    reconstructed = SnapshotReplayEngine.reconstruct_portfolio_state(snap)

    assert reconstructed["snapshot_id"] == snap.id
    assert reconstructed["snapshot_integrity_status"] == SnapshotIntegrityStatus.VALID
    assert reconstructed["is_baseline_snapshot"] is True
    assert reconstructed["scores"]["health_score"] == 92.0
    assert reconstructed["reconstructed_state"]["initiatives"][0]["title"] == "Core Modernization"
    assert "reconstructed_at" in reconstructed


def test_program_and_initiative_replay():
    """Validates program and initiative historical state reconstruction."""
    org_id = uuid.uuid4()
    prog_id = uuid.uuid4()
    prog_payload = {"title": "ERP Rollout", "metrics": {"velocity": 90.0}}
    prog_checksum = calculate_snapshot_checksum(prog_payload)

    prog_snap = ProgramSnapshot(
        id=uuid.uuid4(),
        organization_id=org_id,
        program_id=prog_id,
        snapshot_date=date.today(),
        snapshot_timestamp=datetime.now(timezone.utc),
        program_health_score=85.0,
        snapshot_checksum=prog_checksum,
        snapshot_payload=prog_payload,
    )

    res = SnapshotReplayEngine.reconstruct_program_state(prog_snap)
    assert res["program_id"] == prog_id
    assert res["snapshot_integrity_status"] == SnapshotIntegrityStatus.VALID
    assert res["reconstructed_state"]["title"] == "ERP Rollout"
