"""Deterministic Portfolio Balancing & Concentration Risk Engine for Phase 12.9."""

from typing import Any, Dict, List, Optional
from uuid import UUID

from app.execution.constants import (
    PORTFOLIO_BALANCING_ENGINE_VERSION,
    PortfolioBalanceStatus,
    calculate_portfolio_balance_status,
    calculate_portfolio_strategic_exposure,
)
from app.execution.schemas.decision_support import PortfolioBalanceMetrics


class PortfolioBalancingEngine:
    """100% Deterministic engine calculating portfolio balance, dispersion, and structural exposure."""

    def __init__(self, version: str = PORTFOLIO_BALANCING_ENGINE_VERSION) -> None:
        self.version = version

    def compute_portfolio_balance(
        self,
        initiative_values: Dict[UUID, float],
        initiative_risks: Dict[UUID, float],
        dependency_counts: Dict[UUID, int],
        spof_count: int = 0,
    ) -> PortfolioBalanceMetrics:
        """Computes comprehensive portfolio structural balance, concentration dispersion, and strategic exposure."""
        total_initiatives = len(initiative_values)
        if total_initiatives == 0:
            return PortfolioBalanceMetrics(
                portfolio_balance_score=100.0,
                risk_distribution_score=100.0,
                value_distribution_score=100.0,
                dependency_distribution_score=100.0,
                balance_status=PortfolioBalanceStatus.BALANCED,
                portfolio_strategic_exposure_score=0.0,
                largest_value_concentration_pct=0.0,
                largest_risk_concentration_pct=0.0,
                largest_dependency_cluster_size=0,
                imbalance_factors=[],
                pareto_value_ratio=0.0,
                single_point_of_failure_count=0,
            )

        # 1. Largest Value Concentration (%)
        total_value = sum(initiative_values.values())
        if total_value > 0:
            max_val = max(initiative_values.values())
            largest_val_pct = round((max_val / total_value) * 100.0, 2)
            # Pareto 20% value ratio
            sorted_vals = sorted(initiative_values.values(), reverse=True)
            top_20_count = max(1, int(total_initiatives * 0.20))
            pareto_val_pct = round((sum(sorted_vals[:top_20_count]) / total_value) * 100.0, 2)
        else:
            largest_val_pct = round(100.0 / total_initiatives, 2)
            pareto_val_pct = 20.0

        # 2. Largest Risk Concentration (%)
        total_risk = sum(initiative_risks.values())
        if total_risk > 0:
            max_risk = max(initiative_risks.values())
            largest_risk_pct = round((max_risk / total_risk) * 100.0, 2)
            avg_risk = total_risk / total_initiatives
        else:
            largest_risk_pct = 0.0
            avg_risk = 0.0

        # 3. Largest Dependency Cluster Size
        largest_cluster = max(dependency_counts.values()) if dependency_counts else 0

        # 4. Distribution Scores (0 to 100)
        # Value distribution penalty begins if single initiative holds > 10% value
        val_dist_score = round(max(0.0, min(100.0, 100.0 - max(0.0, largest_val_pct - 10.0))), 2)

        # Risk distribution penalty begins if single initiative holds > 15% risk
        risk_dist_score = round(max(0.0, min(100.0, 100.0 - max(0.0, largest_risk_pct - 15.0))), 2)

        # Dependency distribution score discounts based on max dependency cluster and SPOFs
        dep_dist_score = round(max(0.0, min(100.0, 100.0 - (largest_cluster * 10.0) - (spof_count * 12.5))), 2)

        # 5. Composite Portfolio Balance Score
        raw_balance = (0.35 * val_dist_score) + (0.35 * risk_dist_score) + (0.30 * dep_dist_score)
        balance_score = round(max(0.0, min(100.0, raw_balance)), 2)

        balance_status = calculate_portfolio_balance_status(balance_score)

        # 6. Strategic Exposure Score
        strat_exposure = calculate_portfolio_strategic_exposure(
            risk_exposure=min(100.0, avg_risk),
            dependency_exposure=min(100.0, (largest_cluster * 15.0) + (spof_count * 20.0)),
            concentration_exposure=min(100.0, largest_val_pct),
        )

        # 7. Imbalance Narrative Factors
        imbalance_factors: List[str] = []
        if largest_val_pct > 30.0:
            imbalance_factors.append(f"High value concentration: Single initiative captures {largest_val_pct}% of total portfolio value.")
        if largest_risk_pct > 35.0:
            imbalance_factors.append(f"High risk concentration: Single initiative carries {largest_risk_pct}% of total portfolio risk.")
        if spof_count > 0:
            imbalance_factors.append(f"Structural fragility: {spof_count} Single Points of Failure identified in dependency topology.")
        if largest_cluster >= 5:
            imbalance_factors.append(f"High dependency clustering: Initiative critical path touches {largest_cluster} dependent nodes.")
        if not imbalance_factors:
            imbalance_factors.append("Portfolio exhibits balanced distribution across value, risk, and dependencies.")

        return PortfolioBalanceMetrics(
            portfolio_balance_score=balance_score,
            risk_distribution_score=risk_dist_score,
            value_distribution_score=val_dist_score,
            dependency_distribution_score=dep_dist_score,
            balance_status=balance_status,
            portfolio_strategic_exposure_score=strat_exposure,
            largest_value_concentration_pct=largest_val_pct,
            largest_risk_concentration_pct=largest_risk_pct,
            largest_dependency_cluster_size=largest_cluster,
            imbalance_factors=imbalance_factors,
            pareto_value_ratio=pareto_val_pct,
            single_point_of_failure_count=spof_count,
        )
