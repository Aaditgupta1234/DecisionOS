"""Context Builder & Snapshot Pinning Engine for Phase 6.0."""

import uuid
from typing import Any, Dict, List
from app.knowledge_graph.services.knowledge_graph_builder import KnowledgeGraphBuilder


class ContextBuilder:
    """Pins graph snapshot version and aggregates multi-engine verified intelligence."""

    @staticmethod
    def build_pinned_context(
        portfolio_id: uuid.UUID,
        snapshot_version: int = 1,
    ) -> Dict[str, Any]:
        """
        Retrieves snapshot and compiles deterministic context slice.
        """
        snapshot = KnowledgeGraphBuilder.capture_snapshot(portfolio_id, version=snapshot_version)
        overview = KnowledgeGraphBuilder.build_graph(portfolio_id, snapshot_version)
        stats = KnowledgeGraphBuilder.get_statistics(portfolio_id)
        coverage = KnowledgeGraphBuilder.get_coverage(portfolio_id)

        return {
            "pinned_snapshot_id": snapshot.id,
            "pinned_snapshot_version": snapshot_version,
            "freshness_score": snapshot.freshness_score,
            "ai_ready": snapshot.ai_ready,
            "ai_context_score": snapshot.ai_context_score,
            "total_nodes": overview.total_nodes,
            "total_edges": overview.total_edges,
            "nodes": [n.model_dump() for n in overview.nodes],
            "edges": [e.model_dump() for e in overview.edges],
            "entity_stats": stats.model_dump(),
            "coverage": coverage.model_dump(),
        }
