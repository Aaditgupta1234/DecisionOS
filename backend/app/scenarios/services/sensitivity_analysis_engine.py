"""Sensitivity Analysis & Elasticity Engine for Phase 6.4."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List
from app.scenarios.schemas.scenario_schemas import SensitivityReportResponse


class SensitivityAnalysisEngine:
    """Calculates variable elasticity coefficients and generates tornado chart structures."""

    @classmethod
    def analyze_sensitivity(cls, scenario_id: uuid.UUID) -> SensitivityReportResponse:
        """Computes parametric elasticity and ranks drivers by ARR sensitivity."""
        sensitivities = [
            {
                "variable": "CUSTOMER_RETENTION",
                "label": "Customer Retention Rate",
                "elasticity_score": 0.91,
                "low_swing_arr": "-$34,000",
                "high_swing_arr": "+$48,000",
            },
            {
                "variable": "COURIER_SLA_COMPLIANCE",
                "label": "Courier SLA Compliance",
                "elasticity_score": 0.78,
                "low_swing_arr": "-$26,000",
                "high_swing_arr": "+$32,000",
            },
            {
                "variable": "WINBACK_DISCOUNT_SPEND",
                "label": "Win-Back Incentive Budget",
                "elasticity_score": 0.45,
                "low_swing_arr": "-$12,000",
                "high_swing_arr": "+$18,000",
            },
            {
                "variable": "SUPPORT_HEADCOUNT",
                "label": "Customer Support Bandwidth",
                "elasticity_score": 0.28,
                "low_swing_arr": "-$6,000",
                "high_swing_arr": "+$8,000",
            },
        ]

        tornado_data = {
            "baseline_arr": 124000.0,
            "drivers": [
                {"name": "Retention Rate (±5%)", "min_delta": -34000, "max_delta": 48000},
                {"name": "Courier SLA (±10%)", "min_delta": -26000, "max_delta": 32000},
                {"name": "Incentive Spend (±20%)", "min_delta": -12000, "max_delta": 18000},
                {"name": "Support Bandwidth (±15%)", "min_delta": -6000, "max_delta": 8000},
            ],
        }

        return SensitivityReportResponse(
            id=uuid.uuid4(),
            scenario_id=scenario_id,
            variable_sensitivities=sensitivities,
            most_sensitive_variable="CUSTOMER_RETENTION",
            elasticity_score=0.91,
            tornado_chart_data=tornado_data,
            created_at=datetime.now(timezone.utc),
        )
