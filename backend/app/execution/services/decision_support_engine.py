"""Deterministic Executive Decision Support Engine for Phase 12.9."""

from datetime import date, datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from app.execution.constants import (
    DECISION_SUPPORT_ENGINE_VERSION,
    DecisionReadinessLevel,
    ExecutiveActionPriority,
    ExecutiveImpactTier,
    InterventionRecommendation,
    InvestmentPriority,
    PortfolioActionabilityLevel,
    StrategicConfidenceLevel,
    calculate_decision_confidence,
    calculate_decision_freshness,
    calculate_decision_priority,
    calculate_decision_readiness,
    calculate_executive_impact_tier,
    calculate_portfolio_actionability,
    classify_intervention_recommendation,
)
from app.execution.schemas.decision_support import (
    DecisionDriverItem,
    ExecutiveDecisionItem,
)


class DecisionSupportEngine:
    """100% Deterministic mathematical engine evaluating executive decisions, confidence, and actionability."""

    def __init__(self, version: str = DECISION_SUPPORT_ENGINE_VERSION) -> None:
        self.version = version

    def compute_decision_item(
        self,
        initiative_id: UUID,
        initiative_name: str,
        program_id: Optional[UUID],
        strategic_value: float,
        risk_score: float,
        health_score: float,
        roi_score: float,
        outcome_achievement: float,
        governance_maturity: float,
        strategic_confidence: float = 85.0,
        snapshot_completeness: float = 100.0,
        metric_coverage: float = 100.0,
        budget: float = 0.0,
        has_critical_blockers: bool = False,
        previous_recommendation: Optional[InterventionRecommendation] = None,
        days_in_current_state: int = 0,
        supporting_metric_count: int = 0,
        supporting_finding_count: int = 0,
        supporting_snapshot_count: int = 0,
        created_at: Optional[datetime] = None,
    ) -> ExecutiveDecisionItem:
        """Computes a single deterministic ExecutiveDecisionItem with complete driver explainability."""
        now = created_at or datetime.now(timezone.utc)

        # Clamping inputs (0.0 to 100.0)
        s_val = max(0.0, min(100.0, strategic_value))
        r_val = max(0.0, min(100.0, risk_score))
        h_val = max(0.0, min(100.0, health_score))
        roi_val = max(0.0, min(100.0, roi_score))
        out_val = max(0.0, min(100.0, outcome_achievement))
        gov_val = max(0.0, min(100.0, governance_maturity))
        inverted_risk = 100.0 - r_val

        # Deterministic Weighted Decision Score
        w_strat = 0.25
        w_risk = 0.20
        w_health = 0.20
        w_roi = 0.15
        w_outcome = 0.10
        w_gov = 0.10

        raw_score = (
            w_strat * s_val
            + w_risk * inverted_risk
            + w_health * h_val
            + w_roi * roi_val
            + w_outcome * out_val
            + w_gov * gov_val
        )
        decision_score = round(max(0.0, min(100.0, raw_score)), 2)

        # Priority & Action
        priority = calculate_decision_priority(decision_score)
        action, reasons = classify_intervention_recommendation(
            health_score=h_val,
            risk_score=r_val,
            roi_score=roi_val,
            strategic_value=s_val,
            has_critical_blockers=has_critical_blockers,
        )

        # Confidence
        conf_score, conf_lvl = calculate_decision_confidence(
            strategic_confidence=strategic_confidence,
            snapshot_completeness=snapshot_completeness,
            coverage_rate=metric_coverage,
        )

        # Impact Tier
        impact_tier = calculate_executive_impact_tier(
            strategic_value=s_val,
            budget=budget,
            roi_score=roi_val,
        )

        # Driver breakdown (100% explainability)
        drivers: List[DecisionDriverItem] = [
            DecisionDriverItem(
                factor_name="Strategic Value",
                factor_weight=w_strat,
                factor_value=round(s_val, 2),
                impact_description=f"Contributes {round(w_strat * s_val, 2)} points to decision score",
            ),
            DecisionDriverItem(
                factor_name="Risk Attenuation",
                factor_weight=w_risk,
                factor_value=round(inverted_risk, 2),
                impact_description=f"Contributes {round(w_risk * inverted_risk, 2)} points (100 - risk {round(r_val, 2)})",
            ),
            DecisionDriverItem(
                factor_name="Execution Health",
                factor_weight=w_health,
                factor_value=round(h_val, 2),
                impact_description=f"Contributes {round(w_health * h_val, 2)} points based on milestone velocity",
            ),
            DecisionDriverItem(
                factor_name="ROI Realization",
                factor_weight=w_roi,
                factor_value=round(roi_val, 2),
                impact_description=f"Contributes {round(w_roi * roi_val, 2)} points based on benefit cost efficiency",
            ),
            DecisionDriverItem(
                factor_name="Outcome Attainment",
                factor_weight=w_outcome,
                factor_value=round(out_val, 2),
                impact_description=f"Contributes {round(w_outcome * out_val, 2)} points to decision score",
            ),
            DecisionDriverItem(
                factor_name="Governance Maturity",
                factor_weight=w_gov,
                factor_value=round(gov_val, 2),
                impact_description=f"Contributes {round(w_gov * gov_val, 2)} points from compliance reviews",
            ),
        ]

        rec_changed = (
            previous_recommendation is not None
            and previous_recommendation != action
        )

        urgency_days = 3 if priority == ExecutiveActionPriority.CRITICAL else (7 if priority == ExecutiveActionPriority.HIGH else 14)

        return ExecutiveDecisionItem(
            initiative_id=initiative_id,
            initiative_name=initiative_name,
            program_id=program_id,
            decision_priority=priority,
            impact_tier=impact_tier,
            recommended_action=action,
            previous_recommendation=previous_recommendation,
            recommendation_changed=rec_changed,
            recommendation_reason_codes=reasons,
            decision_score=decision_score,
            decision_confidence_score=conf_score,
            decision_confidence_level=conf_lvl,
            decision_drivers=drivers,
            decision_driver_coverage_pct=100.0,
            supporting_metric_count=supporting_metric_count,
            supporting_finding_count=supporting_finding_count,
            supporting_snapshot_count=supporting_snapshot_count,
            days_in_current_state=days_in_current_state,
            urgency_days=urgency_days,
            estimated_business_impact=f"{impact_tier.value} priority impact on portfolio execution.",
            created_at=now,
        )

    def sort_decision_items(
        self,
        items: List[ExecutiveDecisionItem],
        strategic_values: Optional[Dict[UUID, float]] = None,
        roi_scores: Optional[Dict[UUID, float]] = None,
    ) -> List[ExecutiveDecisionItem]:
        """Sorts decision items using deterministic 5-tuple tie-breaker."""
        strat_map = strategic_values or {}
        roi_map = roi_scores or {}

        def sort_key(item: ExecutiveDecisionItem) -> Tuple[float, float, float, datetime, str]:
            s_val = strat_map.get(item.initiative_id, item.decision_score)
            r_val = roi_map.get(item.initiative_id, item.decision_score)
            return (
                -item.decision_score,
                -s_val,
                -r_val,
                item.created_at,
                str(item.initiative_id),
            )

        return sorted(items, key=sort_key)

    def calculate_portfolio_consensus(
        self,
        decision_items: List[ExecutiveDecisionItem],
        investment_priorities: Dict[UUID, InvestmentPriority],
    ) -> float:
        """Calculates deterministic consensus score (0-100) between decision priorities and investment tiers."""
        if not decision_items:
            return 100.0

        matches = 0
        total = len(decision_items)

        for item in decision_items:
            inv_tier = investment_priorities.get(item.initiative_id, InvestmentPriority.LOW)
            # High alignment pairs:
            # (CRITICAL/HIGH action with STRATEGIC/HIGH investment) or (LOW action with LOW investment)
            is_high_action = item.decision_priority in [ExecutiveActionPriority.CRITICAL, ExecutiveActionPriority.HIGH]
            is_high_inv = inv_tier in [InvestmentPriority.STRATEGIC, InvestmentPriority.HIGH]
            is_low_action = item.decision_priority == ExecutiveActionPriority.LOW
            is_low_inv = inv_tier == InvestmentPriority.LOW

            if (is_high_action and is_high_inv) or (is_low_action and is_low_inv) or (not is_high_action and not is_high_inv):
                matches += 1

        return round((matches / max(1, total)) * 100.0, 2)

    def calculate_recommendation_stability(
        self,
        items: List[ExecutiveDecisionItem],
    ) -> float:
        """Calculates % of initiatives with unchanged recommendations."""
        if not items:
            return 100.0
        unchanged = sum(1 for i in items if not i.recommendation_changed)
        return round((unchanged / len(items)) * 100.0, 2)
