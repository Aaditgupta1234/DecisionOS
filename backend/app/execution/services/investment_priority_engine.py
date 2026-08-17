"""Deterministic Investment Priority Engine for Phase 12.9."""

from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
from uuid import UUID

from app.execution.constants import (
    INVESTMENT_PRIORITY_ENGINE_VERSION,
    InvestmentPriority,
    calculate_investment_priority,
)
from app.execution.schemas.decision_support import InvestmentPriorityItem


class InvestmentPriorityEngine:
    """100% Deterministic engine evaluating expected value, risk-adjusted ROI, and investment priorities."""

    def __init__(self, version: str = INVESTMENT_PRIORITY_ENGINE_VERSION) -> None:
        self.version = version

    def compute_investment_priority(
        self,
        initiative_id: UUID,
        initiative_name: str,
        strategic_value: float,
        roi_score: float,
        risk_score: float,
        outcome_achievement: float,
        budget_allocated: float = 0.0,
        budget_spent: float = 0.0,
        created_at: Optional[datetime] = None,
    ) -> InvestmentPriorityItem:
        """Calculates expected value, risk-adjusted ROI, and investment priority tier."""
        now = created_at or datetime.now(timezone.utc)

        s_val = max(0.0, min(100.0, strategic_value))
        roi_val = max(0.0, min(100.0, roi_score))
        r_val = max(0.0, min(100.0, risk_score))
        out_val = max(0.0, min(100.0, outcome_achievement))

        # 1. Expected Value Score
        expected_value = round(
            0.40 * s_val + 0.35 * roi_val + 0.25 * out_val,
            2,
        )

        # 2. Risk-Adjusted ROI
        # Discount ROI by risk factor (max discount ~66.7% at risk=100)
        risk_discount_factor = max(0.0, 1.0 - (r_val / 150.0))
        risk_adjusted_roi = round(roi_val * risk_discount_factor, 2)

        # 3. Composite Investment Priority Score
        raw_inv_score = (0.60 * expected_value) + (0.40 * risk_adjusted_roi)
        investment_score = round(max(0.0, min(100.0, raw_inv_score)), 2)

        priority = calculate_investment_priority(investment_score)

        # Value Efficiency Ratio: budget utilization to value ratio
        spent = max(0.0, budget_spent)
        alloc = max(0.0, budget_allocated)
        if alloc > 0:
            utilization = spent / alloc
            val_eff = round((expected_value / 100.0) / max(0.1, utilization), 2)
        else:
            val_eff = 1.0

        return InvestmentPriorityItem(
            initiative_id=initiative_id,
            initiative_name=initiative_name,
            investment_priority=priority,
            investment_priority_score=investment_score,
            expected_value_score=expected_value,
            roi_score=roi_val,
            risk_score=r_val,
            risk_adjusted_roi=risk_adjusted_roi,
            budget_allocated=alloc,
            budget_spent=spent,
            value_efficiency_ratio=val_eff,
            created_at=now,
        )

    def sort_investment_priorities(
        self,
        items: List[InvestmentPriorityItem],
        strategic_values: Optional[Dict[UUID, float]] = None,
    ) -> List[InvestmentPriorityItem]:
        """Sorts investment items using deterministic 5-tuple tie-breaker."""
        strat_map = strategic_values or {}

        def sort_key(item: InvestmentPriorityItem) -> Tuple[float, float, float, datetime, str]:
            s_val = strat_map.get(item.initiative_id, item.expected_value_score)
            return (
                -item.investment_priority_score,
                -s_val,
                -item.roi_score,
                item.created_at,
                str(item.initiative_id),
            )

        return sorted(items, key=sort_key)

    def calculate_investment_capacity(
        self,
        items: List[InvestmentPriorityItem],
    ) -> float:
        """Calculates portfolio remaining investment capacity (100 - average budget utilization)."""
        if not items:
            return 100.0

        total_alloc = sum(i.budget_allocated for i in items)
        total_spent = sum(i.budget_spent for i in items)

        if total_alloc > 0:
            avg_util = (total_spent / total_alloc) * 100.0
        else:
            avg_util = 0.0

        return round(max(0.0, min(100.0, 100.0 - avg_util)), 2)
