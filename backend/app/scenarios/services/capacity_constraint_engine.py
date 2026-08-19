"""Operational Capacity Constraint Engine for Phase 6.4."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List
from app.scenarios.schemas.scenario_schemas import (
    CapacityConstraintResponse,
    ConstraintViolationResponse,
)


class CapacityConstraintEngine:
    """Enforces realistic operational resource limits and flags boundary violations."""

    @classmethod
    def get_portfolio_constraints(cls, portfolio_id: uuid.UUID) -> List[CapacityConstraintResponse]:
        """Returns baseline capacity constraints for a portfolio."""
        now = datetime.now(timezone.utc)
        return [
            CapacityConstraintResponse(
                id=uuid.uuid4(),
                portfolio_id=portfolio_id,
                resource_name="SUPPORT_FTES",
                max_capacity=50.0,
                current_utilization=42.0,
                unit="FTEs",
                created_at=now,
            ),
            CapacityConstraintResponse(
                id=uuid.uuid4(),
                portfolio_id=portfolio_id,
                resource_name="CARRIER_DISPATCH_SLOTS",
                max_capacity=10000.0,
                current_utilization=7850.0,
                unit="Parcels/Day",
                created_at=now,
            ),
            CapacityConstraintResponse(
                id=uuid.uuid4(),
                portfolio_id=portfolio_id,
                resource_name="WAREHOUSE_THROUGHPUT",
                max_capacity=25000.0,
                current_utilization=18900.0,
                unit="Units/Day",
                created_at=now,
            ),
            CapacityConstraintResponse(
                id=uuid.uuid4(),
                portfolio_id=portfolio_id,
                resource_name="MARKETING_BUDGET_CEILING",
                max_capacity=100000.0,
                current_utilization=45000.0,
                unit="USD",
                created_at=now,
            ),
        ]

    @classmethod
    def validate_scenario_constraints(cls, scenario_id: uuid.UUID, adjusted_params: Dict[str, Any]) -> List[ConstraintViolationResponse]:
        """Validates whether adjusted parameters exceed operational bandwidth."""
        violations: List[ConstraintViolationResponse] = []
        now = datetime.now(timezone.utc)

        # Example check: if customer volume or marketing surge requires >10,000 parcels/day
        marketing_pct = adjusted_params.get("marketing_budget_increase_pct", 0.0)
        retention_pct = adjusted_params.get("retention_lift_pct", 0.0)

        if marketing_pct > 80.0:
            violations.append(
                ConstraintViolationResponse(
                    id=uuid.uuid4(),
                    scenario_id=scenario_id,
                    resource_name="SUPPORT_FTES",
                    required_capacity=62.0,
                    limit_capacity=50.0,
                    deficit_percentage=24.0,
                    severity="CRITICAL",
                    created_at=now,
                )
            )

        return violations
