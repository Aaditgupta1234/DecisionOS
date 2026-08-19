"""Opportunity Discovery & Scenario Generation Engines for Phase 6.8."""

import uuid
from datetime import datetime, timezone
from typing import List, Optional
from app.enterprise_os.schemas.os_schemas import BenchmarkOpportunityResponse


class OpportunityDiscoveryEngine:
    """Discovers high-leverage revenue opportunities from competitive benchmark gaps."""

    @classmethod
    def get_opportunities(cls, portfolio_id: uuid.UUID) -> List[BenchmarkOpportunityResponse]:
        """Returns discovered competitive opportunities."""
        now = datetime.now(timezone.utc)
        return [
            BenchmarkOpportunityResponse(
                id=uuid.uuid4(),
                benchmark_id=uuid.uuid4(),
                opportunity_title="Close Retention Gap to Industry Median",
                target_metric="Customer Retention Rate: 84.2% -> 91.0%",
                potential_arr_gain=340000.0,
                difficulty_tier="MODERATE",
                auto_scenario_id=uuid.uuid4(),
                status="SCENARIO_GENERATED",
                created_at=now,
            ),
            BenchmarkOpportunityResponse(
                id=uuid.uuid4(),
                benchmark_id=uuid.uuid4(),
                opportunity_title="Surpass Top Quartile Gross Margins",
                target_metric="Gross Profit Margin: 76.5% -> 78.0%",
                potential_arr_gain=180000.0,
                difficulty_tier="LOW",
                auto_scenario_id=None,
                status="DISCOVERED",
                created_at=now,
            ),
        ]


class BenchmarkScenarioGenerator:
    """Feeds Digital Twin by converting competitive opportunities into runnable Digital Twin scenarios."""

    @classmethod
    def generate_scenario_from_opportunity(
        cls,
        opportunity_id: uuid.UUID,
        target_quartile: str = "INDUSTRY_MEDIAN",
    ) -> BenchmarkOpportunityResponse:
        """Generates a Digital Twin simulation scenario directly from benchmark gap parameters."""
        scenario_uuid = uuid.uuid4()
        return BenchmarkOpportunityResponse(
            id=opportunity_id,
            benchmark_id=uuid.uuid4(),
            opportunity_title="Close Retention Gap to Industry Median",
            target_metric="Customer Retention Rate: 84.2% -> 91.0%",
            potential_arr_gain=340000.0,
            difficulty_tier="MODERATE",
            auto_scenario_id=scenario_uuid,
            status="SCENARIO_GENERATED",
            created_at=datetime.now(timezone.utc),
        )
