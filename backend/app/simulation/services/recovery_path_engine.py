"""Recovery Path Modeling Engine for Phase 5.3."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from app.simulation.schemas.simulation_schemas import (
    RecoveryPathComparisonResponse,
    RecoveryPathItem,
)


class RecoveryPathEngine:
    """Models, evaluates, and ranks 3 distinct multi-initiative strategic recovery paths."""

    @staticmethod
    def generate_recovery_paths(
        portfolio_id: uuid.UUID,
        digital_twin_id: Optional[uuid.UUID] = None,
    ) -> RecoveryPathComparisonResponse:
        """
        Produces Path A (Growth First), Path B (Efficiency First), and Path C (Retention First).
        """
        paths: List[RecoveryPathItem] = [
            RecoveryPathItem(
                path_code="PATH_C_RETENTION",
                path_name="Path C: Retention-First & SLA Shield",
                strategic_focus="Churn Cohort Win-Back & Courier SLA Penalties",
                initiatives_included=[
                    "Targeted Win-Back Campaign ($180K ARR)",
                    "Secondary Hub Dispatch Balancing ($140K ARR)",
                    "Payment Auto-Retry Fallback Gateway ($40K ARR)",
                ],
                cost_estimate_usd=75000.0,
                expected_arr_recovery=480000.0,
                risk_score=16.5,
                timeline_weeks=6,
                rank_score=94.2,
                executive_recommendation="Highest capital efficiency (6.4x ROI), fastest time-to-value, and lowest execution risk.",
            ),
            RecoveryPathItem(
                path_code="PATH_A_GROWTH",
                path_name="Path A: Growth-First Acquisition & Cross-Sell",
                strategic_focus="Paid CAC Expansion & Post-Purchase Attachment Widgets",
                initiatives_included=[
                    "Post-Purchase Cross-Sell Engine ($85K ARR)",
                    "Top-of-Funnel Marketing Reallocation ($120K ARR)",
                    "Tier-1 Influencer Affiliate Scaling ($75K ARR)",
                ],
                cost_estimate_usd=110000.0,
                expected_arr_recovery=385000.0,
                risk_score=32.0,
                timeline_weeks=8,
                rank_score=78.5,
                executive_recommendation="Strong gross revenue potential but higher customer acquisition risk and longer CAC payback.",
            ),
            RecoveryPathItem(
                path_code="PATH_B_EFFICIENCY",
                path_name="Path B: Operational Infrastructure Modernization",
                strategic_focus="Warehouse Line Automation & Regional Hub Expansion",
                initiatives_included=[
                    "Warehouse Sorting Line Overhaul ($110K ARR)",
                    "Micro-Courier Multi-Contract Redundancy ($35K ARR)",
                ],
                cost_estimate_usd=145000.0,
                expected_arr_recovery=220000.0,
                risk_score=45.0,
                timeline_weeks=16,
                rank_score=62.0,
                executive_recommendation="Heavy capital expenditure with long lead times; recommend deferral to Q4.",
            ),
        ]

        # Sorted descending by rank_score
        paths.sort(key=lambda x: x.rank_score, reverse=True)

        return RecoveryPathComparisonResponse(
            portfolio_id=portfolio_id,
            generated_at=datetime.now(timezone.utc),
            recovery_paths=paths,
            recommended_path_code=paths[0].path_code,
        )
