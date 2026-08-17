"""Unit tests for Phase 13 SnapshotLineageEngine (Deferred 13.6)."""

import uuid
from app.monitoring.services.snapshot_lineage_engine import SnapshotLineageEngine


class DummySnap:
    def __init__(self, snap_id, parent_id=None):
        self.id = snap_id
        self.parent_snapshot_id = parent_id


def test_snapshot_lineage_engine_linear_chain():
    """Tests calculation of lineage depth along a linear snapshot ancestor chain."""
    snap_a = uuid.uuid4()  # Root Baseline
    snap_b = uuid.uuid4()  # Monthly
    snap_c = uuid.uuid4()  # Quarterly
    snap_d = uuid.uuid4()  # Executive

    snapshots = [
        DummySnap(snap_a, parent_id=None),
        DummySnap(snap_b, parent_id=snap_a),
        DummySnap(snap_c, parent_id=snap_b),
        DummySnap(snap_d, parent_id=snap_c),
    ]

    # Root snapshot depth
    res_a = SnapshotLineageEngine.compute_lineage_depth(snap_a, snapshots)
    assert res_a.lineage_depth == 0
    assert res_a.root_snapshot_id == snap_a
    assert len(res_a.ancestor_chain) == 0

    # Leaf snapshot depth
    res_d = SnapshotLineageEngine.compute_lineage_depth(snap_d, snapshots)
    assert res_d.lineage_depth == 3
    assert res_d.root_snapshot_id == snap_a
    assert res_d.parent_snapshot_id == snap_c
    assert res_d.ancestor_chain == [snap_c, snap_b, snap_a]


def test_snapshot_lineage_engine_cycle_prevention():
    """Tests that cyclic snapshot dependencies are broken gracefully without infinite loops."""
    snap_1 = uuid.uuid4()
    snap_2 = uuid.uuid4()

    # Cyclic
    snapshots = [
        DummySnap(snap_1, parent_id=snap_2),
        DummySnap(snap_2, parent_id=snap_1),
    ]

    res = SnapshotLineageEngine.compute_lineage_depth(snap_1, snapshots)
    assert res.lineage_depth >= 1
    assert res.root_snapshot_id in (snap_1, snap_2)
