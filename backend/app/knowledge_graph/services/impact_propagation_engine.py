"""Impact Propagation Engine for Phase 5.5."""

import uuid
from typing import Any, Dict, List
from app.knowledge_graph.schemas.graph_schemas import AffectedNodeItem, ImpactPropagationResponse


class ImpactPropagationEngine:
    """Calculates downstream sensitivity ripple effects across multi-hop paths."""

    @staticmethod
    def calculate_propagation(
        portfolio_id: uuid.UUID,
        source_node_id: uuid.UUID,
        source_node_name: str = "Delivery Latency (Days)",
        propagation_depth: int = 3,
    ) -> ImpactPropagationResponse:
        """
        Simulates: Delivery Latency (5.4d) -> CSAT (-12%) -> Retention (-7.3%) -> Revenue (-$124K ARR) -> Health (-11 pts).
        """
        affected_nodes: List[AffectedNodeItem] = [
            AffectedNodeItem(
                node_id=uuid.uuid4(),
                node_type="KPI",
                node_name="Customer Satisfaction (CSAT)",
                hop_depth=1,
                estimated_variance_pct=-12.5,
                direction="NEGATIVE",
                confidence_score=0.94,
            ),
            AffectedNodeItem(
                node_id=uuid.uuid4(),
                node_type="KPI",
                node_name="Customer Retention Rate",
                hop_depth=2,
                estimated_variance_pct=-7.3,
                direction="NEGATIVE",
                confidence_score=0.91,
            ),
            AffectedNodeItem(
                node_id=uuid.uuid4(),
                node_type="KPI",
                node_name="Quarterly ARR Recovery",
                hop_depth=3,
                estimated_variance_pct=-18.8,
                direction="NEGATIVE",
                confidence_score=0.88,
            ),
            AffectedNodeItem(
                node_id=uuid.uuid4(),
                node_type="KPI",
                node_name="Overall Portfolio Health Score",
                hop_depth=3,
                estimated_variance_pct=-11.0,
                direction="NEGATIVE",
                confidence_score=0.92,
            ),
        ]

        impact_score = 78.5  # High Downstream Impact
        confidence_score = 0.90

        return ImpactPropagationResponse(
            portfolio_id=portfolio_id,
            source_node_id=source_node_id,
            source_node_name=source_node_name,
            propagation_depth=propagation_depth,
            impact_score=impact_score,
            confidence_score=confidence_score,
            affected_nodes=affected_nodes,
        )
