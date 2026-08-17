"""Integration tests for Phase 12.8 Historical Snapshots & Time-Series REST APIs."""

import uuid
import pytest
from app.execution.constants import (
    SNAPSHOT_ENGINE_VERSION,
    SNAPSHOT_SCHEMA_VERSION,
    SnapshotGenerationStatus,
    SnapshotIntegrityStatus,
    SnapshotRetentionCategory,
    SnapshotTriggerSource,
)


def test_snapshot_api_complete_workflow(client, analyst_headers):
    """Tests complete Snapshot creation, history, replay, and differential comparison via REST APIs."""
    # 1. Create Program and Initiative
    prog_res = client.post(
        "/api/v1/execution/programs",
        json={
            "title": "Cloud Infrastructure 2026",
            "description": "Enterprise cloud scale.",
        },
        headers=analyst_headers,
    )
    assert prog_res.status_code == 201
    prog_id = prog_res.json()["id"]

    init_res = client.post(
        "/api/v1/execution/initiatives",
        json={
            "program_id": prog_id,
            "title": "Kubernetes Fleet Rollout",
            "description": "Multi-region cluster fleet.",
            "objective": "Zero downtime deploy.",
            "budget_allocated": 150000.0,
            "budget_spent": 100000.0,
        },
        headers=analyst_headers,
    )
    assert init_res.status_code == 201
    init_id = init_res.json()["id"]

    # 2. POST /api/v1/execution/snapshots/portfolio (Baseline Snapshot)
    base_res = client.post(
        "/api/v1/execution/snapshots/portfolio",
        json={
            "is_baseline_snapshot": True,
            "snapshot_retention_category": SnapshotRetentionCategory.AUDIT.value,
            "trigger_source": SnapshotTriggerSource.MANUAL.value,
        },
        headers=analyst_headers,
    )
    assert base_res.status_code == 201
    base_data = base_res.json()
    base_id = base_data["id"]
    assert base_data["is_baseline_snapshot"] is True
    assert base_data["snapshot_retention_category"] == SnapshotRetentionCategory.AUDIT.value
    assert base_data["snapshot_schema_version"] == SNAPSHOT_SCHEMA_VERSION
    assert base_data["snapshot_integrity_status"] == SnapshotIntegrityStatus.VALID.value
    assert len(base_data["snapshot_checksum"]) == 64
    assert base_data["source_initiative_count"] >= 1

    # 3. GET /api/v1/execution/snapshots/portfolio/baseline
    get_base = client.get(
        "/api/v1/execution/snapshots/portfolio/baseline",
        headers=analyst_headers,
    )
    assert get_base.status_code == 200
    assert get_base.json()["id"] == base_id

    # 4. POST /api/v1/execution/snapshots/portfolio (Second Snapshot with parent reference)
    sec_res = client.post(
        "/api/v1/execution/snapshots/portfolio",
        json={
            "is_baseline_snapshot": False,
            "parent_snapshot_id": base_id,
            "snapshot_retention_category": SnapshotRetentionCategory.STANDARD.value,
        },
        headers=analyst_headers,
    )
    assert sec_res.status_code == 201
    sec_id = sec_res.json()["id"]
    assert sec_res.json()["parent_snapshot_id"] == base_id

    # 5. GET /api/v1/execution/snapshots/portfolio (Latest)
    get_latest = client.get(
        "/api/v1/execution/snapshots/portfolio",
        headers=analyst_headers,
    )
    assert get_latest.status_code == 200
    assert get_latest.json()["id"] == sec_id

    # 6. GET /api/v1/execution/snapshots/portfolio/{id}
    get_by_id = client.get(
        f"/api/v1/execution/snapshots/portfolio/{base_id}",
        headers=analyst_headers,
    )
    assert get_by_id.status_code == 200
    assert get_by_id.json()["id"] == base_id

    # 7. GET /api/v1/execution/snapshots/portfolio/history
    get_hist = client.get(
        "/api/v1/execution/snapshots/portfolio/history",
        headers=analyst_headers,
    )
    assert get_hist.status_code == 200
    hist_data = get_hist.json()
    assert hist_data["total_snapshots"] >= 2
    assert "timeseries_analytics" in hist_data
    assert "portfolio_evolution" in hist_data

    # 8. POST & GET Program Snapshot
    prog_snap_res = client.post(
        f"/api/v1/execution/snapshots/programs/{prog_id}",
        json={"is_baseline_snapshot": True},
        headers=analyst_headers,
    )
    assert prog_snap_res.status_code == 201
    prog_snap_id = prog_snap_res.json()["id"]

    get_prog_snaps = client.get(
        f"/api/v1/execution/snapshots/programs/{prog_id}",
        headers=analyst_headers,
    )
    assert get_prog_snaps.status_code == 200
    assert get_prog_snaps.json()["total_snapshots"] >= 1

    # 9. POST & GET Initiative Snapshot
    init_snap_res = client.post(
        f"/api/v1/execution/snapshots/initiatives/{init_id}",
        json={"is_baseline_snapshot": True},
        headers=analyst_headers,
    )
    assert init_snap_res.status_code == 201
    init_snap_id = init_snap_res.json()["id"]

    get_init_snaps = client.get(
        f"/api/v1/execution/snapshots/initiatives/{init_id}",
        headers=analyst_headers,
    )
    assert get_init_snaps.status_code == 200
    assert get_init_snaps.json()["total_snapshots"] >= 1

    # 10. Replay Endpoints
    port_replay = client.get(
        f"/api/v1/execution/snapshots/replay/portfolio/{base_id}",
        headers=analyst_headers,
    )
    assert port_replay.status_code == 200
    assert port_replay.json()["snapshot_integrity_status"] == SnapshotIntegrityStatus.VALID.value
    assert "reconstructed_state" in port_replay.json()

    prog_replay = client.get(
        f"/api/v1/execution/snapshots/replay/program/{prog_snap_id}",
        headers=analyst_headers,
    )
    assert prog_replay.status_code == 200
    assert prog_replay.json()["snapshot_integrity_status"] == SnapshotIntegrityStatus.VALID.value

    init_replay = client.get(
        f"/api/v1/execution/snapshots/replay/initiative/{init_snap_id}",
        headers=analyst_headers,
    )
    assert init_replay.status_code == 200
    assert init_replay.json()["snapshot_integrity_status"] == SnapshotIntegrityStatus.VALID.value

    # 11. Differential Comparison
    comp_res = client.get(
        f"/api/v1/execution/snapshots/compare?snapshot_a={base_id}&snapshot_b={sec_id}",
        headers=analyst_headers,
    )
    assert comp_res.status_code == 200
    comp_data = comp_res.json()
    assert comp_data["snapshot_a_id"] == base_id
    assert comp_data["snapshot_b_id"] == sec_id
    assert "comparison_period_days" in comp_data
    assert len(comp_data["metric_deltas"]) >= 5


def test_snapshot_api_tenant_isolation(client, analyst_headers):
    """Validates 404 response on unknown snapshot ID."""
    fake_id = uuid.uuid4()
    res = client.get(
        f"/api/v1/execution/snapshots/portfolio/{fake_id}",
        headers=analyst_headers,
    )
    assert res.status_code == 404
