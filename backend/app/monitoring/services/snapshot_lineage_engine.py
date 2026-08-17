"""Snapshot Lineage Depth & Topology Engine for Phase 13: Production Governance & Alert Monitoring."""

import uuid
from typing import Any, Dict, List, Optional, Set

from app.monitoring.constants import SNAPSHOT_LINEAGE_ENGINE_VERSION
from app.monitoring.schemas.production_monitoring import SnapshotLineageDepthResponse


class SnapshotLineageEngine:
    """Traverses snapshot parent-child lineage chains to compute exact lineage depth and root lineage trees."""

    @classmethod
    def compute_lineage_depth(
        cls,
        snapshot_id: uuid.UUID,
        all_snapshots: List[Any],
    ) -> SnapshotLineageDepthResponse:
        """Calculates exact lineage depth, root ancestor, and ancestor chain for a snapshot."""
        # Index snapshots by ID
        snap_map: Dict[uuid.UUID, Any] = {}
        for s in all_snapshots:
            sid_raw = getattr(s, "id", None)
            if sid_raw:
                snap_map[uuid.UUID(str(sid_raw))] = s

        current_id = snapshot_id
        ancestor_chain: List[uuid.UUID] = []
        visited: Set[uuid.UUID] = {current_id}
        depth = 0
        root_id = current_id
        parent_id: Optional[uuid.UUID] = None

        # Check immediate parent
        target_snap = snap_map.get(current_id)
        if target_snap:
            p_raw = getattr(target_snap, "parent_snapshot_id", None)
            if p_raw:
                parent_id = uuid.UUID(str(p_raw))

        # Traverse upwards to root
        while current_id in snap_map:
            snap = snap_map[current_id]
            parent_raw = getattr(snap, "parent_snapshot_id", None)
            if not parent_raw:
                root_id = current_id
                break

            parent_uuid = uuid.UUID(str(parent_raw))
            if parent_uuid in visited:
                # Cycle detected: break safely
                root_id = parent_uuid
                break

            visited.add(parent_uuid)
            ancestor_chain.append(parent_uuid)
            depth += 1
            current_id = parent_uuid
            root_id = parent_uuid

        # Compute branch span (number of children pointing to snapshot_id)
        child_count = sum(
            1 for s in all_snapshots if getattr(s, "parent_snapshot_id", None) and uuid.UUID(str(s.parent_snapshot_id)) == snapshot_id
        )

        return SnapshotLineageDepthResponse(
            snapshot_id=snapshot_id,
            lineage_depth=depth,
            parent_snapshot_id=parent_id,
            root_snapshot_id=root_id,
            ancestor_chain=ancestor_chain,
            branch_span=max(1, child_count),
            engine_version=SNAPSHOT_LINEAGE_ENGINE_VERSION,
        )
