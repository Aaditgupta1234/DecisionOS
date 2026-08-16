"""Portfolio Benefits & Outcomes Aggregation Engine for Phase 12.6."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.execution.constants import (
    OUTCOME_ENGINE_VERSION,
    OUTCOME_SNAPSHOT_METRIC_VERSION,
    BenefitConcentrationRisk,
    BenefitRealizationStatus,
    BenefitTrend,
    BenefitType,
    ConfidenceTrend,
    MeasurementQuality,
    MeasurementRecency,
    MeasurementStability,
    OutcomeConfidenceLevel,
    OutcomeCriticality,
    OutcomeExecutionStatus,
    OutcomeHealth,
    OutcomeMetricType,
    OutcomeStatus,
    OutcomeValueClassification,
    PortfolioOutcomeHealthGrade,
    ROIClassification,
    ROITrend,
    TargetDateStatus,
    calculate_benefit_concentration_risk,
    calculate_benefit_trend,
    calculate_confidence_trend,
    calculate_portfolio_outcome_health_grade,
    calculate_roi_classification,
    calculate_roi_trend,
)


class PortfolioBenefitsEngine:
    """
    Deterministic intelligence engine for rolling up strategic outcomes,
    benefits realization, ROI distribution, concentration risks, and portfolio health.
    """

    ENGINE_VERSION = OUTCOME_ENGINE_VERSION

    @classmethod
    def calculate_portfolio_summary(
        cls,
        outcomes: List[Dict[str, Any]],
        benefits: List[Dict[str, Any]],
        investment_costs: Optional[List[float]] = None,
        previous_realized_value: Optional[float] = None,
        previous_roi: Optional[float] = None,
        previous_confidence_score: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Executes full deterministic portfolio benefits aggregation.
        """
        now = datetime.now(timezone.utc)

        # 1. Benefits Financial Totals
        total_expected = sum(b.get("expected_value", 0.0) for b in benefits)
        total_realized = sum(b.get("realized_value", 0.0) for b in benefits)
        total_gap = sum(b.get("realization_gap", 0.0) for b in benefits)
        total_cost = sum(investment_costs) if investment_costs else sum(b.get("investment_cost", 0.0) for b in benefits)

        # Value at Risk
        value_at_risk = round(max(0.0, total_expected - total_realized), 2)

        # Portfolio Realization %
        if total_expected > 0:
            port_realization = (total_realized / total_expected) * 100.0
        elif total_expected == 0 and total_realized > 0:
            port_realization = 100.0
        else:
            port_realization = 0.0
        portfolio_realization_pct = round(max(0.0, min(200.0, port_realization)), 2)

        # Value Realization Efficiency (0-200%)
        portfolio_value_realization_efficiency = portfolio_realization_pct

        # Portfolio ROI
        if total_cost > 0:
            port_roi = ((total_realized - total_cost) / total_cost) * 100.0
        elif total_cost == 0 and total_realized > 0:
            port_roi = 100.0
        else:
            port_roi = 0.0
        portfolio_roi = round(port_roi, 2)
        portfolio_roi_classification = calculate_roi_classification(portfolio_roi)

        # 5-Tier ROI Distribution
        exceptional_roi_count = 0
        strong_roi_count = 0
        acceptable_roi_count = 0
        poor_roi_count = 0
        negative_roi_count = 0

        for b in benefits:
            cost = b.get("investment_cost", 0.0)
            realized = b.get("realized_value", 0.0)
            if cost > 0:
                item_roi = ((realized - cost) / cost) * 100.0
            else:
                item_roi = 100.0 if realized > 0 else 0.0

            cls_roi = calculate_roi_classification(item_roi)
            if cls_roi == ROIClassification.EXCEPTIONAL:
                exceptional_roi_count += 1
            elif cls_roi == ROIClassification.STRONG:
                strong_roi_count += 1
            elif cls_roi == ROIClassification.ACCEPTABLE:
                acceptable_roi_count += 1
            elif cls_roi == ROIClassification.POOR:
                poor_roi_count += 1
            else:
                negative_roi_count += 1

        # 2. Outcomes Attainment & Health
        total_outcomes = len(outcomes)
        achieved_outcomes = sum(1 for o in outcomes if o.get("status") == OutcomeStatus.ACHIEVED)
        partially_achieved_outcomes = sum(1 for o in outcomes if o.get("status") == OutcomeStatus.PARTIALLY_ACHIEVED)
        missed_outcomes = sum(1 for o in outcomes if o.get("status") == OutcomeStatus.MISSED)
        in_progress_outcomes = sum(1 for o in outcomes if o.get("status") == OutcomeStatus.IN_PROGRESS)
        not_started_outcomes = sum(1 for o in outcomes if o.get("status") == OutcomeStatus.NOT_STARTED)

        completed_outcomes_count = achieved_outcomes + partially_achieved_outcomes + missed_outcomes
        if completed_outcomes_count > 0:
            attainment_rate = (achieved_outcomes / completed_outcomes_count) * 100.0
        elif total_outcomes > 0:
            attainment_rate = (achieved_outcomes / total_outcomes) * 100.0
        else:
            attainment_rate = 0.0
        portfolio_attainment_rate = round(max(0.0, min(100.0, attainment_rate)), 2)

        # Attainment distribution % shares
        outcome_attainment_dist = {
            "ACHIEVED": round((achieved_outcomes / max(1, total_outcomes)) * 100.0, 2),
            "PARTIALLY_ACHIEVED": round((partially_achieved_outcomes / max(1, total_outcomes)) * 100.0, 2),
            "MISSED": round((missed_outcomes / max(1, total_outcomes)) * 100.0, 2),
            "IN_PROGRESS": round((in_progress_outcomes / max(1, total_outcomes)) * 100.0, 2),
            "NOT_STARTED": round((not_started_outcomes / max(1, total_outcomes)) * 100.0, 2),
        }

        # Outcome Health Counts
        healthy_cnt = sum(1 for o in outcomes if o.get("outcome_health") == OutcomeHealth.HEALTHY)
        watch_cnt = sum(1 for o in outcomes if o.get("outcome_health") == OutcomeHealth.WATCH)
        at_risk_cnt = sum(1 for o in outcomes if o.get("outcome_health") == OutcomeHealth.AT_RISK)
        critical_cnt = sum(1 for o in outcomes if o.get("outcome_health") == OutcomeHealth.CRITICAL)

        portfolio_health_grade = calculate_portfolio_outcome_health_grade(
            healthy_cnt, watch_cnt, at_risk_cnt, critical_cnt
        )

        # Outcome Execution Status Counts
        on_track_cnt = sum(1 for o in outcomes if o.get("execution_status") == OutcomeExecutionStatus.ON_TRACK)
        at_risk_exec_cnt = sum(1 for o in outcomes if o.get("execution_status") == OutcomeExecutionStatus.AT_RISK)
        off_track_cnt = sum(1 for o in outcomes if o.get("execution_status") == OutcomeExecutionStatus.OFF_TRACK)
        completed_exec_cnt = sum(1 for o in outcomes if o.get("execution_status") == OutcomeExecutionStatus.COMPLETED)

        # Target Pipeline Intelligence
        due_30_days_cnt = sum(
            1 for o in outcomes
            if o.get("status") not in (OutcomeStatus.ACHIEVED, OutcomeStatus.COMPLETED if hasattr(OutcomeStatus, "COMPLETED") else None)
            and o.get("days_until_target") is not None
            and 0 <= o.get("days_until_target", 999) <= 30
        )
        overdue_outcomes_cnt = sum(
            1 for o in outcomes
            if o.get("status") not in (OutcomeStatus.ACHIEVED, OutcomeStatus.COMPLETED if hasattr(OutcomeStatus, "COMPLETED") else None)
            and (
                o.get("target_date_status") == TargetDateStatus.OVERDUE
                or (o.get("days_until_target") is not None and o.get("days_until_target", 0) < 0)
            )
        )

        # Value Classification Counts
        trans_cnt = sum(1 for b in benefits if b.get("value_classification") == OutcomeValueClassification.TRANSFORMATIONAL)
        high_val_cnt = sum(1 for b in benefits if b.get("value_classification") == OutcomeValueClassification.HIGH)
        med_val_cnt = sum(1 for b in benefits if b.get("value_classification") == OutcomeValueClassification.MEDIUM)
        low_val_cnt = sum(1 for b in benefits if b.get("value_classification") == OutcomeValueClassification.LOW)

        # Measurement Quality Counts
        high_qual_cnt = sum(1 for o in outcomes if o.get("measurement_quality") == MeasurementQuality.HIGH)
        med_qual_cnt = sum(1 for o in outcomes if o.get("measurement_quality") == MeasurementQuality.MEDIUM)
        low_qual_cnt = sum(1 for o in outcomes if o.get("measurement_quality") == MeasurementQuality.LOW)

        # 3. Concentration Analysis
        # Pareto benefit concentration (% produced by top 20% initiatives)
        benefit_values = sorted([b.get("realized_value", 0.0) for b in benefits], reverse=True)
        top_20_count = max(1, int(len(benefit_values) * 0.20))
        top_20_val = sum(benefit_values[:top_20_count])
        if total_realized > 0:
            top_20_concentration = round((top_20_val / total_realized) * 100.0, 2)
        else:
            top_20_concentration = 0.0
        concentration_risk = calculate_benefit_concentration_risk(top_20_concentration)

        # Outcome target concentration index
        target_values = sorted([o.get("target_value", 0.0) for o in outcomes], reverse=True)
        top_20_target_count = max(1, int(len(target_values) * 0.20))
        top_20_target_sum = sum(target_values[:top_20_target_count])
        total_target_sum = sum(target_values)
        outcome_concentration_idx = round(
            (top_20_target_sum / total_target_sum) * 100.0 if total_target_sum > 0 else 0.0, 2
        )

        # Dependency exposure score
        dep_counts = [o.get("dependent_initiatives_count", 1) for o in outcomes]
        avg_deps = sum(dep_counts) / max(1, len(dep_counts))
        dep_exposure_score = round(min(100.0, avg_deps * 20.0), 2)

        # 4. Benefit Type Distribution (7 categories summing to 100.0%)
        type_totals = {bt.value: 0.0 for bt in BenefitType}
        for b in benefits:
            bt_val = b.get("benefit_type")
            key = bt_val.value if hasattr(bt_val, "value") else str(bt_val)
            if key in type_totals:
                type_totals[key] += b.get("realized_value", 0.0)

        benefit_type_dist = {}
        for k, v in type_totals.items():
            benefit_type_dist[k] = round((v / total_realized) * 100.0 if total_realized > 0 else 0.0, 2)

        # 5. Confidence & Coverage
        high_conf_outcomes = sum(1 for o in outcomes if o.get("confidence_level") == OutcomeConfidenceLevel.HIGH)
        med_conf_outcomes = sum(1 for o in outcomes if o.get("confidence_level") == OutcomeConfidenceLevel.MEDIUM)
        low_conf_outcomes = sum(1 for o in outcomes if o.get("confidence_level") == OutcomeConfidenceLevel.LOW)

        high_conf_benefits = sum(1 for b in benefits if b.get("confidence_level") == OutcomeConfidenceLevel.HIGH)
        med_conf_benefits = sum(1 for b in benefits if b.get("confidence_level") == OutcomeConfidenceLevel.MEDIUM)
        low_conf_benefits = sum(1 for b in benefits if b.get("confidence_level") == OutcomeConfidenceLevel.LOW)

        conf_coverage = (
            ((high_conf_outcomes * 100.0) + (med_conf_outcomes * 60.0) + (low_conf_outcomes * 20.0))
            / max(1, total_outcomes)
        ) if total_outcomes > 0 else 100.0
        confidence_coverage_score = round(max(0.0, min(100.0, conf_coverage)), 2)

        benefits_measured = sum(1 for b in benefits if b.get("realized_value", 0.0) > 0)
        benefits_expected_cnt = len(benefits)
        benefit_coverage_rate = round(
            (benefits_measured / max(1, benefits_expected_cnt)) * 100.0, 2
        )

        # 6. Averages
        avg_m_age = (
            sum(o.get("measurement_age_days", 0) for o in outcomes) / max(1, total_outcomes)
            if total_outcomes > 0 else 0.0
        )
        avg_out_age = (
            sum(o.get("outcome_age_days", 0) for o in outcomes) / max(1, total_outcomes)
            if total_outcomes > 0 else 0.0
        )
        delay_list = [o.get("realization_delay_days") for o in outcomes if o.get("realization_delay_days") is not None]
        avg_delay = (sum(delay_list) / len(delay_list)) if delay_list else 0.0

        avg_velocity = (
            sum(o.get("realization_velocity", 0.0) for o in outcomes) / max(1, total_outcomes)
            if total_outcomes > 0 else 0.0
        )
        avg_completeness = (
            sum(o.get("measurement_completeness_score", 100.0) for o in outcomes) / max(1, total_outcomes)
            if total_outcomes > 0 else 100.0
        )
        avg_reliability = (
            sum(o.get("measurement_reliability_score", 100.0) for o in outcomes) / max(1, total_outcomes)
            if total_outcomes > 0 else 100.0
        )
        avg_data_reliability = (
            sum(o.get("outcome_data_reliability_score", 100.0) for o in outcomes) / max(1, total_outcomes)
            if total_outcomes > 0 else 100.0
        )
        avg_predictability = (
            sum(o.get("outcome_predictability_score", 100.0) for o in outcomes) / max(1, total_outcomes)
            if total_outcomes > 0 else 100.0
        )
        avg_stability = (
            sum(o.get("measurement_stability_score", 100.0) for o in outcomes) / max(1, total_outcomes)
            if total_outcomes > 0 else 100.0
        )

        avg_benefit_score = (
            sum(b.get("benefit_score", 0.0) for b in benefits) / max(1, len(benefits))
            if benefits else 0.0
        )

        # 7. Trends
        benefit_trend = calculate_benefit_trend(total_realized, previous_realized_value)
        roi_trend = calculate_roi_trend(portfolio_roi, previous_roi)
        conf_trend = calculate_confidence_trend(confidence_coverage_score, previous_confidence_score)

        return {
            "total_expected_value": round(total_expected, 2),
            "total_realized_value": round(total_realized, 2),
            "total_realization_gap": round(total_gap, 2),
            "value_at_risk": value_at_risk,
            "portfolio_realization_percentage": portfolio_realization_pct,
            "portfolio_value_realization_efficiency": portfolio_value_realization_efficiency,
            "portfolio_roi": portfolio_roi,
            "portfolio_benefit_score": round(avg_benefit_score, 2),
            "portfolio_roi_classification": portfolio_roi_classification,
            "exceptional_roi_count": exceptional_roi_count,
            "strong_roi_count": strong_roi_count,
            "acceptable_roi_count": acceptable_roi_count,
            "poor_roi_count": poor_roi_count,
            "negative_roi_count": negative_roi_count,
            "portfolio_outcome_health_grade": portfolio_health_grade,
            "outcomes_due_next_30_days": due_30_days_cnt,
            "overdue_outcomes_count": overdue_outcomes_cnt,
            "portfolio_outcome_attainment_rate": portfolio_attainment_rate,
            "portfolio_outcomes_achieved_rate": portfolio_attainment_rate,
            "outcome_attainment_distribution": outcome_attainment_dist,
            "healthy_outcomes_count": healthy_cnt,
            "watch_outcomes_count": watch_cnt,
            "at_risk_outcomes_count": at_risk_cnt,
            "critical_outcomes_count": critical_cnt,
            "on_track_outcomes_count": on_track_cnt,
            "at_risk_execution_outcomes_count": at_risk_exec_cnt,
            "off_track_outcomes_count": off_track_cnt,
            "completed_outcomes_count": completed_exec_cnt,
            "transformational_benefits_count": trans_cnt,
            "high_value_benefits_count": high_val_cnt,
            "medium_value_benefits_count": med_val_cnt,
            "low_value_benefits_count": low_val_cnt,
            "high_quality_measurements": high_qual_cnt,
            "medium_quality_measurements": med_qual_cnt,
            "low_quality_measurements": low_qual_cnt,
            "top_20_percent_benefit_concentration": top_20_concentration,
            "benefit_concentration_risk": concentration_risk,
            "outcome_concentration_index": outcome_concentration_idx,
            "portfolio_dependency_exposure_score": dep_exposure_score,
            "benefit_type_distribution": benefit_type_dist,
            "high_confidence_outcomes": high_conf_outcomes,
            "medium_confidence_outcomes": med_conf_outcomes,
            "low_confidence_outcomes": low_conf_outcomes,
            "confidence_coverage_score": confidence_coverage_score,
            "high_confidence_benefits": high_conf_benefits,
            "medium_confidence_benefits": med_conf_benefits,
            "low_confidence_benefits": low_conf_benefits,
            "benefits_measured_count": benefits_measured,
            "benefits_expected_count": benefits_expected_cnt,
            "benefit_measurement_coverage_rate": benefit_coverage_rate,
            "average_measurement_age_days": round(avg_m_age, 1),
            "average_outcome_age_days": round(avg_out_age, 1),
            "average_realization_delay_days": round(avg_delay, 1),
            "average_realization_velocity": round(avg_velocity, 4),
            "average_measurement_completeness_score": round(avg_completeness, 2),
            "average_measurement_reliability_score": round(avg_reliability, 2),
            "average_outcome_data_reliability_score": round(avg_data_reliability, 2),
            "average_outcome_predictability_score": round(avg_predictability, 2),
            "average_measurement_stability_score": round(avg_stability, 2),
            "benefit_realization_trend": benefit_trend,
            "roi_trend": roi_trend,
            "confidence_trend": conf_trend,
            "engine_version": cls.ENGINE_VERSION,
            "snapshot_metric_version": OUTCOME_SNAPSHOT_METRIC_VERSION,
            "calculated_at": now,
        }
