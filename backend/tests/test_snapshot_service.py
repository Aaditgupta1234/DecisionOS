"""Unit tests for Phase 12.8 Snapshot Service."""

import uuid
from datetime import date, datetime, timedelta, timezone
import pytest
from app.execution.constants import (
    SnapshotGenerationStatus,
    SnapshotIntegrityStatus,
    SnapshotQualityLevel,
    SnapshotRetentionCategory,
    SnapshotTriggerSource,
)
from app.execution.models.initiative import StrategicInitiative
from app.execution.models.program import StrategicProgram
from app.execution.schemas.snapshot import (
    CreatePortfolioSnapshotRequest,
    CreateProgramSnapshotRequest,
)
from app.execution.services.snapshot_service import SnapshotService


@pytest.mark.anyio
async def test_snapshot_service_crud_and_comparison(db_session):
    """Tests SnapshotService creation, baseline querying, differential comparison, and replay."""
    sample_org_id = uuid.uuid4()
    service = SnapshotService(db_session)

    # 1. Create a program and initiative to populate state
    prog = StrategicProgram(
        id=uuid.uuid4(),
        organization_id=sample_org_id,
        title="Enterprise Scalability Program",
        description="Scalability roadmap",
    )
    db_session.add(prog)
    db_session.commit()

    init = StrategicInitiative(
        id=uuid.uuid4(),
        organization_id=sample_org_id,
        program_id=prog.id,
        title="Microservices Migration",
        description="Migrate monolith to services",
        objective="Improve throughput",
        budget_allocated=200000.0,
        budget_spent=150000.0,
        execution_health_score=88.0,
    )
    db_session.add(init)
    db_session.commit()

    # 2. Capture Baseline Snapshot
    req_base = CreatePortfolioSnapshotRequest(
        is_baseline_snapshot=True,
        snapshot_retention_category=SnapshotRetentionCategory.AUDIT,
        trigger_source=SnapshotTriggerSource.MANUAL,
    )
    base_res = await service.create_portfolio_snapshot(sample_org_id, req_base)
    assert base_res.is_baseline_snapshot is True
    assert base_res.snapshot_retention_category == SnapshotRetentionCategory.AUDIT
    assert base_res.snapshot_integrity_status == SnapshotIntegrityStatus.VALID
    assert base_res.source_initiative_count >= 1

    # 3. Retrieve Baseline Snapshot
    fetched_base = await service.get_baseline_portfolio_snapshot(sample_org_id)
    assert fetched_base.id == base_res.id

    # 4. Capture second snapshot with parent reference
    req_sec = CreatePortfolioSnapshotRequest(
        is_baseline_snapshot=False,
        parent_snapshot_id=base_res.id,
        snapshot_retention_category=SnapshotRetentionCategory.STANDARD,
    )
    sec_res = await service.create_portfolio_snapshot(sample_org_id, req_sec)
    assert sec_res.parent_snapshot_id == base_res.id

    # 5. List Snapshot History with Time-Series Analytics
    history = await service.list_portfolio_snapshots_history(sample_org_id)
    assert history.total_snapshots >= 2
    assert history.timeseries_analytics is not None
    assert history.portfolio_evolution is not None

    # 6. Replay Snapshot
    replay_res = await service.replay_portfolio_snapshot(sample_org_id, base_res.id)
    assert replay_res.snapshot_id == base_res.id
    assert replay_res.snapshot_integrity_status == SnapshotIntegrityStatus.VALID
    assert "initiatives" in replay_res.reconstructed_state

    # 7. Compare Snapshots
    comp_res = await service.compare_snapshots(
        organization_id=sample_org_id,
        snapshot_a_id=base_res.id,
        snapshot_b_id=sec_res.id,
    )
    assert comp_res.snapshot_a_id == base_res.id
    assert comp_res.snapshot_b_id == sec_res.id
    assert len(comp_res.metric_deltas) >= 5
    assert "comparison_period_days" in comp_res.model_dump()
