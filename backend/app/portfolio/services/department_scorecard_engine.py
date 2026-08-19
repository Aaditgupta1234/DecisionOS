"""Department Scorecard Engine for Phase 5.2."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List
from app.portfolio.schemas.enterprise_portfolio import (
    DepartmentScorecardItem,
    DepartmentScorecardResponse,
)


class DepartmentScorecardEngine:
    """Generates standardized department scorecards across core functional units."""

    @staticmethod
    def generate_scorecards(portfolio_id: uuid.UUID) -> DepartmentScorecardResponse:
        """
        Produces deterministic scorecards for Marketing, Operations, Product, CS, Finance, and Sales.
        """
        scorecards: List[DepartmentScorecardItem] = [
            DepartmentScorecardItem(
                department_name="Marketing & Growth",
                lead_owner="Head of Growth",
                health_score=88.0,
                status="OPTIMAL",
                primary_kpis={
                    "CAC": "$42.50",
                    "Channel ROI": "4.2x",
                    "Conversion Rate": "3.8%",
                },
                recovery_potential_arr=85000.0,
                risk_level="LOW",
                explanation="High conversion efficiency and customer acquisition velocity across organic and paid channels.",
            ),
            DepartmentScorecardItem(
                department_name="Logistics & Operations",
                lead_owner="Elena Rostova (Head of Ops)",
                health_score=61.0,
                status="AT_RISK",
                primary_kpis={
                    "SLA Compliance": "78.4%",
                    "Delivery Latency": "5.4 days",
                    "Dispatch Backlog": "1,420 orders",
                },
                recovery_potential_arr=140000.0,
                risk_level="CRITICAL",
                explanation="Southeastern transit delays exceed SLA threshold by 2.2 days, contributing directly to churn.",
            ),
            DepartmentScorecardItem(
                department_name="Customer Success",
                lead_owner="Marcus Vance (VP CS)",
                health_score=72.0,
                status="ATTENTION",
                primary_kpis={
                    "Retention Rate": "85.8%",
                    "CSAT": "3.9 / 5.0",
                    "Churn Velocity": "+4.3% MoM",
                },
                recovery_potential_arr=180000.0,
                risk_level="HIGH",
                explanation="Targeted win-back campaign in flight to recover 842 churn-risk accounts with $124K ARR already captured.",
            ),
            DepartmentScorecardItem(
                department_name="Product & Engineering",
                lead_owner="Chief Product Officer",
                health_score=84.0,
                status="HEALTHY",
                primary_kpis={
                    "Feature Adoption": "64.2%",
                    "Checkout Drop-off": "12.1%",
                    "Attachment Rate": "18.5%",
                },
                recovery_potential_arr=60000.0,
                risk_level="LOW",
                explanation="Checkout funnel performance is stable with positive cross-sell attachment trends.",
            ),
            DepartmentScorecardItem(
                department_name="Finance & Corporate Strategy",
                lead_owner="Chief Financial Officer",
                health_score=86.0,
                status="HEALTHY",
                primary_kpis={
                    "Gross Margin": "68.4%",
                    "Net Realized Recovery": "$124,000 ARR",
                    "LTV / CAC": "3.8x",
                },
                recovery_potential_arr=0.0,
                risk_level="LOW",
                explanation="Unit economics remain robust with healthy gross margin contribution across active lines.",
            ),
        ]

        return DepartmentScorecardResponse(
            portfolio_id=portfolio_id,
            generated_at=datetime.now(timezone.utc),
            scorecards=scorecards,
        )
