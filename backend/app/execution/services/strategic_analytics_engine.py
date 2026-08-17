"""Strategic Analytics Engine for Phase 12.7."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.execution.constants import (
    STRATEGIC_ANALYTICS_ENGINE_VERSION,
    STRATEGIC_SNAPSHOT_METRIC_VERSION,
    StrategicConfidenceLevel,
    StrategicHealthGrade,
    StrategicPriority,
    ValueEfficiencyGrade,
    calculate_portfolio_strategic_maturity_score,
    calculate_strategic_confidence_level,
    calculate_strategic_confidence_score,
    calculate_strategic_health_grade,
    calculate_strategic_priority,
    calculate_value_efficiency_grade,
)


class StrategicAnalyticsEngine:
    """
    Deterministic calculation engine for strategic value score, value efficiency,
    confidence score, health grades, priority classification, and maturity scores.
    """

    ENGINE_VERSION = STRATEGIC_ANALYTICS_ENGINE_VERSION
    SNAPSHOT_METRIC_VERSION = STRATEGIC_SNAPSHOT_METRIC_VERSION

    @classmethod
    def calculate_initiative_analytics(
        cls,
        outcome_achievement: float = 100.0,
        benefit_realization: float = 100.0,
        roi_score: float = 100.0,
        execution_health: float = 100.0,
        governance_maturity: float = 100.0,
        risk_score: float = 0.0,
        cost_variance_pct: float = 0.0,
        strategic_alignment_score: float = 100.0,
        outcome_data_reliability_score: float = 100.0,
        governance_compliance_score: float = 100.0,
        measurement_quality_score: float = 100.0,
        metric_coverage_rate: float = 100.0,
    ) -> Dict[str, Any]:
        """
        Calculates all deterministic strategic analytics metrics for a single initiative.
        """
        now = datetime.now(timezone.utc)
        warnings: List[str] = []

        # 1. Strategic Value Score (0-100)
        # 30% Outcome + 25% Benefits + 20% ROI + 15% Health + 10% Governance
        val_score = (
            0.30 * outcome_achievement
            + 0.25 * benefit_realization
            + 0.20 * roi_score
            + 0.15 * execution_health
            + 0.10 * governance_maturity
        )
        strategic_value_score = round(max(0.0, min(100.0, val_score)), 2)

        # 2. Value Efficiency Score (0-100)
        # Value Delivered / (Execution Cost Factor + Risk Factor)
        # Value Delivered: avg of outcome, benefit, roi
        val_delivered = (outcome_achievement + benefit_realization + roi_score) / 3.0
        # Cost factor: 1.0 + cost overruns (if any), normalized
        cost_penalty = max(0.0, cost_variance_pct) / 100.0
        # Risk factor: 0.0 - 1.0
        risk_penalty = max(0.0, min(100.0, risk_score)) / 100.0
        denominator = 1.0 + (0.5 * cost_penalty) + (0.5 * risk_penalty)
        
        raw_efficiency = val_delivered / max(0.1, denominator)
        value_efficiency_score = round(max(0.0, min(100.0, raw_efficiency)), 2)
        value_efficiency_grade = calculate_value_efficiency_grade(value_efficiency_score)

        # 3. Strategic Confidence Score (0-100)
        confidence_score = calculate_strategic_confidence_score(
            outcome_data_reliability_score=outcome_data_reliability_score,
            governance_compliance_score=governance_compliance_score,
            measurement_quality_score=measurement_quality_score,
            metric_coverage_rate=metric_coverage_rate,
        )
        confidence_level = calculate_strategic_confidence_level(confidence_score)

        # 4. Strategic Health Grade
        strategic_health_grade = calculate_strategic_health_grade(
            strategic_value_score=strategic_value_score,
            alignment_score=strategic_alignment_score,
            execution_health_score=execution_health,
        )

        # 5. Strategic Priority
        strategic_priority = calculate_strategic_priority(
            value_score=strategic_value_score,
            risk_score=risk_score,
            health_score=execution_health,
            outcome_realization=outcome_achievement,
        )

        # Data quality checks
        if metric_coverage_rate < 70.0:
            warnings.append(f"Metric coverage rate is low ({metric_coverage_rate:.1f}%). Analytics precision may be reduced.")
        if outcome_data_reliability_score < 60.0:
            warnings.append(f"Outcome data reliability is sub-optimal ({outcome_data_reliability_score:.1f}%).")
        if governance_compliance_score < 60.0:
            warnings.append("Governance compliance records are incomplete or overdue.")

        return {
            "strategic_value_score": strategic_value_score,
            "value_efficiency_score": value_efficiency_score,
            "value_efficiency_grade": value_efficiency_grade,
            "strategic_health_grade": strategic_health_grade,
            "strategic_confidence_score": confidence_score,
            "strategic_confidence_level": confidence_level,
            "strategic_priority": strategic_priority,
            "strategic_alignment_score": round(max(0.0, min(100.0, strategic_alignment_score)), 2),
            "outcome_achievement_component": round(outcome_achievement, 2),
            "benefit_realization_component": round(benefit_realization, 2),
            "roi_score_component": round(roi_score, 2),
            "execution_health_component": round(execution_health, 2),
            "governance_maturity_component": round(governance_maturity, 2),
            "data_quality_warnings": warnings,
            "engine_version": cls.ENGINE_VERSION,
            "calculated_at": now,
            "snapshot_metric_version": cls.SNAPSHOT_METRIC_VERSION,
            "snapshot_compatible": True,
        }

    @classmethod
    def calculate_portfolio_analytics(
        cls,
        initiatives_metrics: List[Dict[str, Any]],
        governance_maturity: float = 100.0,
        execution_health: float = 100.0,
        outcome_achievement: float = 100.0,
        benefits_realization: float = 100.0,
        strategic_kpis_defined: int = 0,
        strategic_kpis_measured: int = 0,
    ) -> Dict[str, Any]:
        """
        Aggregates portfolio-level strategic analytics and calculates flagship maturity KPI.
        """
        now = datetime.now(timezone.utc)
        warnings: List[str] = []

        if not initiatives_metrics:
            maturity = calculate_portfolio_strategic_maturity_score(
                governance_maturity, execution_health, outcome_achievement, benefits_realization
            )
            warnings.append("No active initiatives found in portfolio scope.")
            default_metrics = cls.calculate_initiative_analytics(
                outcome_achievement=outcome_achievement,
                benefit_realization=benefits_realization,
                roi_score=100.0,
                execution_health=execution_health,
                governance_maturity=governance_maturity,
                risk_score=0.0,
            )
            return {
                "portfolio_strategic_maturity_score": maturity,
                "portfolio_strategic_value_score": default_metrics["strategic_value_score"],
                "portfolio_value_efficiency_score": default_metrics["value_efficiency_score"],
                "portfolio_strategic_confidence_score": default_metrics["strategic_confidence_score"],
                "portfolio_strategic_confidence_level": default_metrics["strategic_confidence_level"],
                "portfolio_strategic_health_grade": default_metrics["strategic_health_grade"],
                "portfolio_value_efficiency_grade": default_metrics["value_efficiency_grade"],
                "priority_distribution": {},
                "strategic_kpis_defined": strategic_kpis_defined,
                "strategic_kpis_measured": strategic_kpis_measured,
                "strategic_kpi_coverage_rate": 100.0 if strategic_kpis_defined == 0 else 0.0,
                "metrics": default_metrics,
                "data_quality_warnings": warnings,
                "engine_version": cls.ENGINE_VERSION,
                "calculated_at": now,
                "snapshot_metric_version": cls.SNAPSHOT_METRIC_VERSION,
                "snapshot_compatible": True,
            }

        n = len(initiatives_metrics)
        avg_value = sum(m.get("strategic_value_score", 0.0) for m in initiatives_metrics) / n
        avg_eff = sum(m.get("value_efficiency_score", 0.0) for m in initiatives_metrics) / n
        avg_conf = sum(m.get("strategic_confidence_score", 0.0) for m in initiatives_metrics) / n
        avg_align = sum(m.get("strategic_alignment_score", 0.0) for m in initiatives_metrics) / n
        
        avg_out = sum(m.get("outcome_achievement_component", 0.0) for m in initiatives_metrics) / n
        avg_ben = sum(m.get("benefit_realization_component", 0.0) for m in initiatives_metrics) / n
        avg_roi = sum(m.get("roi_score_component", 0.0) for m in initiatives_metrics) / n
        avg_hlt = sum(m.get("execution_health_component", 0.0) for m in initiatives_metrics) / n
        avg_gov = sum(m.get("governance_maturity_component", 0.0) for m in initiatives_metrics) / n

        # Portfolio Maturity KPI
        portfolio_maturity = calculate_portfolio_strategic_maturity_score(
            governance_maturity=avg_gov,
            execution_health=avg_hlt,
            outcome_achievement=avg_out,
            benefits_realization=avg_ben,
        )

        port_val = round(avg_value, 2)
        port_eff = round(avg_eff, 2)
        port_conf = round(avg_conf, 2)
        port_align = round(avg_align, 2)

        conf_level = calculate_strategic_confidence_level(port_conf)
        eff_grade = calculate_value_efficiency_grade(port_eff)
        health_grade = calculate_strategic_health_grade(port_val, port_align, avg_hlt)

        # Priority distribution counts
        priority_counts: Dict[str, int] = {}
        for m in initiatives_metrics:
            p = str(m.get("strategic_priority", StrategicPriority.MONITOR.value))
            priority_counts[p] = priority_counts.get(p, 0) + 1

        # Strategic KPI coverage
        if strategic_kpis_defined > 0:
            coverage_rate = round((strategic_kpis_measured / strategic_kpis_defined) * 100.0, 2)
        else:
            coverage_rate = 100.0

        if coverage_rate < 70.0:
            warnings.append(f"Strategic KPI measurement coverage is below 70% ({coverage_rate:.1f}%).")
        if port_conf < 60.0:
            warnings.append("Portfolio-level strategic confidence is LOW due to data quality across initiatives.")

        # Aggregate warnings from initiatives
        for m in initiatives_metrics:
            for w in m.get("data_quality_warnings", []):
                if w not in warnings:
                    warnings.append(w)

        summary_metrics = {
            "strategic_value_score": port_val,
            "value_efficiency_score": port_eff,
            "value_efficiency_grade": eff_grade,
            "strategic_health_grade": health_grade,
            "strategic_confidence_score": port_conf,
            "strategic_confidence_level": conf_level,
            "strategic_priority": StrategicPriority.MONITOR,
            "strategic_alignment_score": port_align,
            "outcome_achievement_component": round(avg_out, 2),
            "benefit_realization_component": round(avg_ben, 2),
            "roi_score_component": round(avg_roi, 2),
            "execution_health_component": round(avg_hlt, 2),
            "governance_maturity_component": round(avg_gov, 2),
            "data_quality_warnings": warnings,
            "engine_version": cls.ENGINE_VERSION,
            "calculated_at": now,
            "snapshot_metric_version": cls.SNAPSHOT_METRIC_VERSION,
            "snapshot_compatible": True,
        }

        return {
            "portfolio_strategic_maturity_score": portfolio_maturity,
            "portfolio_strategic_value_score": port_val,
            "portfolio_value_efficiency_score": port_eff,
            "portfolio_strategic_confidence_score": port_conf,
            "portfolio_strategic_confidence_level": conf_level,
            "portfolio_strategic_health_grade": health_grade,
            "portfolio_value_efficiency_grade": eff_grade,
            "priority_distribution": priority_counts,
            "strategic_kpis_defined": strategic_kpis_defined,
            "strategic_kpis_measured": strategic_kpis_measured,
            "strategic_kpi_coverage_rate": coverage_rate,
            "metrics": summary_metrics,
            "data_quality_warnings": warnings,
            "engine_version": cls.ENGINE_VERSION,
            "calculated_at": now,
            "snapshot_metric_version": cls.SNAPSHOT_METRIC_VERSION,
            "snapshot_compatible": True,
        }
