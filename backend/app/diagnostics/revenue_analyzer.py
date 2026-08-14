"""Revenue Diagnostic Analyzer identifying revenue drops, stagnation, growth acceleration, and volatility."""

from typing import List
import numpy as np

from app.core.config import settings
from app.core.constants import FindingCategory, FindingSeverity, FindingSubtype, FindingType
from app.diagnostics.base_analyzer import BaseDiagnosticAnalyzer
from app.diagnostics.evidence_builder import EvidenceBuilder
from app.diagnostics.helpers import (
    compute_time_series_aggregates,
    create_diagnostic_finding,
    extract_metrics_dict,
    load_lightweight_columns,
)
from app.diagnostics.metric_keys import MetricKeys
from app.diagnostics.severity import calculate_confidence, calculate_severity
from app.models.dataset import Dataset
from app.models.dataset_metric import DatasetMetric
from app.models.diagnostic_finding import DiagnosticFinding


class RevenueDiagnosticAnalyzer(BaseDiagnosticAnalyzer):
    """
    Diagnostic analyzer evaluating revenue performance across both aggregated metrics
    and time-series trajectory (period-over-period decline, stagnation, acceleration, and volatility).
    """

    async def analyze(
        self,
        dataset: Dataset,
        metrics: List[DatasetMetric],
    ) -> List[DiagnosticFinding]:
        """
        Executes multi-finding revenue diagnostic evaluation.
        
        Args:
            dataset: The target Dataset instance.
            metrics: Pre-computed DatasetMetric records.
            
        Returns:
            List of detected DiagnosticFinding entities.
        """
        findings: List[DiagnosticFinding] = []
        metrics_map = extract_metrics_dict(metrics)

        # Tier 2: Attempt lightweight time-series analysis if raw CSV is available
        ts_df = None
        raw_df = load_lightweight_columns(dataset, ["order_date", "revenue"])
        if raw_df is not None and not raw_df.empty:
            ts_df = compute_time_series_aggregates(raw_df, date_col="order_date", value_col="revenue")

        if ts_df is not None and len(ts_df) >= 2:
            # 1. Evaluate Time-Series Revenue Decline & Sustained Downtrend
            decline_finding = self._check_time_series_decline(dataset, ts_df)
            if decline_finding:
                findings.append(decline_finding)

            # 2. Evaluate Revenue Stagnation (Sub-threshold minimal growth)
            stagnation_finding = self._check_time_series_stagnation(dataset, ts_df)
            if stagnation_finding:
                findings.append(stagnation_finding)

            # 3. Evaluate Growth Acceleration (Strong positive surge)
            acceleration_finding = self._check_time_series_acceleration(dataset, ts_df)
            if acceleration_finding:
                findings.append(acceleration_finding)

            # 4. Evaluate Revenue Volatility (Coefficient of variation)
            volatility_finding = self._check_time_series_volatility(dataset, ts_df)
            if volatility_finding:
                findings.append(volatility_finding)

        else:
            # Tier 1 (Metrics-First Fallback): Evaluate purely from summary DatasetMetrics
            metric_findings = self._check_metrics_baseline(dataset, metrics_map)
            findings.extend(metric_findings)

        return findings

    def _check_time_series_decline(
        self,
        dataset: Dataset,
        ts_df,
    ) -> DiagnosticFinding | None:
        """Detects period-over-period revenue decline or consecutive multi-period drops."""
        # Latest period percentage change
        latest_pct_change = ts_df["pct_change"].iloc[-1]
        threshold = settings.REVENUE_DECLINE_THRESHOLD  # e.g. 0.15

        # Check consecutive negative periods
        negative_periods = 0
        for pct in reversed(ts_df["pct_change"].dropna().tolist()):
            if pct < 0:
                negative_periods += 1
            else:
                break

        # Trigger if latest period drop exceeds threshold OR 2+ consecutive declines occurred
        if (latest_pct_change is not None and latest_pct_change <= -threshold) or negative_periods >= 2:
            drop_pct = abs(latest_pct_change) if latest_pct_change is not None else 0.0
            curr_rev = float(ts_df["total"].iloc[-1])
            prev_rev = float(ts_df["total"].iloc[-2]) if len(ts_df) >= 2 else curr_rev
            diff = prev_rev - curr_rev

            severity = calculate_severity(
                observed_deviation=drop_pct,
                base_threshold=threshold,
                high_multiplier=2.0,
                critical_multiplier=3.0,
            )
            confidence = calculate_confidence(sample_size=len(ts_df))

            evidence = EvidenceBuilder.build_time_series_evidence(
                category=FindingCategory.REVENUE.value,
                subtype=FindingSubtype.DECLINE.value,
                metric_name=MetricKeys.TOTAL_REVENUE,
                current_value=curr_rev,
                previous_value=prev_rev,
                change_percent=round(latest_pct_change * 100.0, 2) if latest_pct_change is not None else 0.0,
                threshold=round(threshold * 100.0, 2),
                confidence=confidence,
                period_count=len(ts_df),
                trend="negative",
                recommendation="Investigate core channel attrition, launch win-back campaigns, and audit sales pipeline conversion.",
                extra_context={
                    "consecutive_decline_periods": negative_periods,
                    "estimated_revenue_loss": round(diff, 2) if diff > 0 else 0.0,
                },
            )

            title = (
                f"Sustained Revenue Decline ({negative_periods} Consecutive Periods)"
                if negative_periods >= 2
                else f"Significant Revenue Decline of {round(drop_pct * 100.0, 1)}%"
            )

            return create_diagnostic_finding(
                dataset=dataset,
                finding_type=FindingType.REVENUE_DROP,
                severity=severity,
                title=title,
                description=f"Revenue fell by {round(drop_pct * 100.0, 1)}% from ${prev_rev:,.2f} to ${curr_rev:,.2f} over the latest period.",
                business_impact=f"Estimated top-line contraction of ${diff:,.2f}, creating significant budget and cash-flow risks.",
                metric_key=MetricKeys.TOTAL_REVENUE,
                confidence_score=confidence,
                supporting_data=evidence,
            )

        return None

    def _check_time_series_stagnation(
        self,
        dataset: Dataset,
        ts_df,
    ) -> DiagnosticFinding | None:
        """Detects flat or minimal revenue growth over multiple periods."""
        threshold = settings.REVENUE_STAGNATION_THRESHOLD  # e.g. 0.02 (2%)
        valid_changes = ts_df["pct_change"].dropna().tolist()

        if len(valid_changes) < 2:
            return None

        # Check if recent periods have growth between 0.0% and threshold
        recent_changes = valid_changes[-3:]
        avg_growth = float(np.mean(recent_changes))

        if 0.0 <= avg_growth <= threshold:
            confidence = calculate_confidence(sample_size=len(ts_df))
            curr_rev = float(ts_df["total"].iloc[-1])
            prev_rev = float(ts_df["total"].iloc[-2])

            evidence = EvidenceBuilder.build_time_series_evidence(
                category=FindingCategory.REVENUE.value,
                subtype=FindingSubtype.STAGNATION.value,
                metric_name=MetricKeys.TOTAL_REVENUE,
                current_value=curr_rev,
                previous_value=prev_rev,
                change_percent=round(avg_growth * 100.0, 2),
                threshold=round(threshold * 100.0, 2),
                confidence=confidence,
                period_count=len(ts_df),
                trend="flat",
                recommendation="Review product pricing tiers, explore adjacent market segments, and optimize cross-sell programs.",
            )

            return create_diagnostic_finding(
                dataset=dataset,
                finding_type=FindingType.REVENUE_DROP,
                severity=FindingSeverity.MEDIUM,
                title=f"Revenue Growth Stagnation ({round(avg_growth * 100.0, 1)}% Average Growth)",
                description=f"Revenue growth flattened over recent periods with an average growth rate of only {round(avg_growth * 100.0, 1)}%.",
                business_impact="Stalled top-line expansion reduces competitive advantage and market share velocity.",
                metric_key=MetricKeys.TOTAL_REVENUE,
                confidence_score=confidence,
                supporting_data=evidence,
            )

        return None

    def _check_time_series_acceleration(
        self,
        dataset: Dataset,
        ts_df,
    ) -> DiagnosticFinding | None:
        """Detects breakout positive growth acceleration exceeding growth benchmarks."""
        latest_pct_change = ts_df["pct_change"].iloc[-1]
        threshold = settings.REVENUE_GROWTH_THRESHOLD  # e.g. 0.20 (20%)

        if latest_pct_change is not None and latest_pct_change >= threshold:
            curr_rev = float(ts_df["total"].iloc[-1])
            prev_rev = float(ts_df["total"].iloc[-2]) if len(ts_df) >= 2 else curr_rev
            confidence = calculate_confidence(sample_size=len(ts_df))

            evidence = EvidenceBuilder.build_time_series_evidence(
                category=FindingCategory.REVENUE.value,
                subtype=FindingSubtype.GROWTH_ACCELERATION.value,
                metric_name=MetricKeys.TOTAL_REVENUE,
                current_value=curr_rev,
                previous_value=prev_rev,
                change_percent=round(latest_pct_change * 100.0, 2),
                threshold=round(threshold * 100.0, 2),
                confidence=confidence,
                period_count=len(ts_df),
                trend="positive",
                recommendation="Scale inventory fulfillment and operational capacity to sustain strong demand surge.",
            )

            return create_diagnostic_finding(
                dataset=dataset,
                finding_type=FindingType.REVENUE_DROP,
                severity=FindingSeverity.LOW,
                title=f"Strong Revenue Growth Acceleration (+{round(latest_pct_change * 100.0, 1)}%)",
                description=f"Revenue surged by {round(latest_pct_change * 100.0, 1)}% from ${prev_rev:,.2f} to ${curr_rev:,.2f}.",
                business_impact="High revenue expansion opportunity; maintain fulfillment quality during volume surge.",
                metric_key=MetricKeys.TOTAL_REVENUE,
                confidence_score=confidence,
                supporting_data=evidence,
            )

        return None

    def _check_time_series_volatility(
        self,
        dataset: Dataset,
        ts_df,
    ) -> DiagnosticFinding | None:
        """Detects excessive periodic revenue fluctuations based on coefficient of variation."""
        threshold = settings.REVENUE_VOLATILITY_THRESHOLD  # e.g. 0.30 (30% CV)
        cv = float(ts_df["cv"].iloc[-1]) if "cv" in ts_df.columns else 0.0

        if cv >= threshold:
            confidence = calculate_confidence(sample_size=len(ts_df), variance=cv)
            severity = calculate_severity(
                observed_deviation=cv,
                base_threshold=threshold,
                high_multiplier=1.75,
                critical_multiplier=2.5,
            )

            min_rev = float(ts_df["total"].min())
            max_rev = float(ts_df["total"].max())

            evidence = EvidenceBuilder.build_evidence(
                category=FindingCategory.REVENUE.value,
                subtype=FindingSubtype.VOLATILITY.value,
                metric_name=MetricKeys.TOTAL_REVENUE,
                observed=round(cv * 100.0, 2),
                threshold=round(threshold * 100.0, 2),
                confidence=confidence,
                sample_size=len(ts_df),
                recommendation="Introduce recurring subscription contracts and diversify revenue channels to stabilize income.",
                context={
                    "min_period_revenue": min_rev,
                    "max_period_revenue": max_rev,
                    "coefficient_of_variation": round(cv, 3),
                },
            )

            return create_diagnostic_finding(
                dataset=dataset,
                finding_type=FindingType.REVENUE_DROP,
                severity=severity,
                title=f"Elevated Revenue Volatility (CV: {round(cv * 100.0, 1)}%)",
                description=f"Periodic revenue exhibits wide swings between ${min_rev:,.2f} and ${max_rev:,.2f} with a volatility coefficient of {round(cv * 100.0, 1)}%.",
                business_impact="Unpredictable revenue fluctuations heighten working capital strain and inventory planning risks.",
                metric_key=MetricKeys.TOTAL_REVENUE,
                confidence_score=confidence,
                supporting_data=evidence,
            )

        return None

    def _check_metrics_baseline(
        self,
        dataset: Dataset,
        metrics_map: dict,
    ) -> List[DiagnosticFinding]:
        """Tier 1: Evaluates summary metric values when time-series raw data is not accessible."""
        findings: List[DiagnosticFinding] = []
        total_rev = metrics_map.get(MetricKeys.TOTAL_REVENUE)
        rev_per_cust = metrics_map.get(MetricKeys.REVENUE_PER_CUSTOMER)

        if total_rev is not None and isinstance(total_rev, (int, float)):
            if total_rev <= 0:
                evidence = EvidenceBuilder.build_metric_evidence(
                    category=FindingCategory.REVENUE.value,
                    subtype=FindingSubtype.DECLINE.value,
                    metric_name=MetricKeys.TOTAL_REVENUE,
                    observed=total_rev,
                    threshold=0.0,
                    confidence=0.95,
                    sample_size=1,
                    recommendation="Review transaction pipeline to diagnose complete revenue stoppage.",
                )
                findings.append(
                    create_diagnostic_finding(
                        dataset=dataset,
                        finding_type=FindingType.REVENUE_DROP,
                        severity=FindingSeverity.CRITICAL,
                        title="Zero or Negative Revenue Detected",
                        description="Dataset reflects zero or negative monetary revenue.",
                        business_impact="Complete cessation of top-line cash generation.",
                        metric_key=MetricKeys.TOTAL_REVENUE,
                        confidence_score=0.95,
                        supporting_data=evidence,
                    )
                )

        if rev_per_cust is not None and isinstance(rev_per_cust, (int, float)):
            # If revenue per customer is exceptionally low (e.g. < $5)
            if 0 < rev_per_cust < 5.0:
                evidence = EvidenceBuilder.build_metric_evidence(
                    category=FindingCategory.REVENUE.value,
                    subtype=FindingSubtype.STAGNATION.value,
                    metric_name=MetricKeys.REVENUE_PER_CUSTOMER,
                    observed=rev_per_cust,
                    threshold=5.0,
                    confidence=0.85,
                    sample_size=metrics_map.get(MetricKeys.UNIQUE_CUSTOMERS, 1),
                    recommendation="Introduce product bundles and upsells to increase basket size per customer.",
                )
                findings.append(
                    create_diagnostic_finding(
                        dataset=dataset,
                        finding_type=FindingType.REVENUE_DROP,
                        severity=FindingSeverity.MEDIUM,
                        title=f"Low Revenue Per Customer (${rev_per_cust:,.2f})",
                        description=f"Average revenue generated per customer is only ${rev_per_cust:,.2f}.",
                        business_impact="Depressed average order value restrains profitability.",
                        metric_key=MetricKeys.REVENUE_PER_CUSTOMER,
                        confidence_score=0.85,
                        supporting_data=evidence,
                    )
                )

        return findings
