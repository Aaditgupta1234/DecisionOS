"""Customer Diagnostic Analyzer identifying churn increases, retention problems, acquisition slowdowns, and growth acceleration."""

from typing import List, Optional
import pandas as pd

from app.core.config import settings
from app.core.constants import FindingCategory, FindingSeverity, FindingSubtype, FindingType
from app.diagnostics.base_analyzer import BaseDiagnosticAnalyzer
from app.diagnostics.evidence_builder import EvidenceBuilder
from app.diagnostics.helpers import (
    create_diagnostic_finding,
    extract_metrics_dict,
    load_lightweight_columns,
)
from app.diagnostics.metric_keys import MetricKeys
from app.diagnostics.severity import (
    calculate_confidence,
    calculate_severity,
    evaluate_catastrophic_escalation,
)
from app.models.dataset import Dataset
from app.models.dataset_metric import DatasetMetric
from app.models.diagnostic_finding import DiagnosticFinding


class CustomerDiagnosticAnalyzer(BaseDiagnosticAnalyzer):
    """
    Diagnostic analyzer detecting customer lifecycle risks and opportunities,
    including churn spikes, retention weaknesses, acquisition slowdowns, and customer surges.
    """

    async def analyze(
        self,
        dataset: Dataset,
        metrics: List[DatasetMetric],
    ) -> List[DiagnosticFinding]:
        """
        Executes multi-finding customer diagnostic evaluation.
        
        Args:
            dataset: The target Dataset instance.
            metrics: Pre-computed DatasetMetric records.
            
        Returns:
            List of detected DiagnosticFinding entities.
        """
        findings: List[DiagnosticFinding] = []
        metrics_map = extract_metrics_dict(metrics)

        # Tier 2: Attempt lightweight cohort analysis if raw CSV is available
        df = load_lightweight_columns(dataset, ["customer_id", "order_date"])

        if df is not None and not df.empty and "customer_id" in df.columns:
            # 1. Retention Problems (Repeat Purchase Rate from Data)
            retention_finding = self._check_dataframe_retention(dataset, df)
            if retention_finding:
                findings.append(retention_finding)

            # 2. Time-Series Customer Growth Slowdown & Acquisition Surge
            if "order_date" in df.columns:
                growth_findings = self._check_dataframe_customer_dynamics(dataset, df)
                findings.extend(growth_findings)

        # Tier 1 (Metrics-First): Check explicit customer summary metrics
        metric_findings = self._check_metrics_baseline(dataset, metrics_map)
        findings.extend(metric_findings)

        return findings

    def _check_dataframe_retention(
        self,
        dataset: Dataset,
        df: pd.DataFrame,
    ) -> Optional[DiagnosticFinding]:
        """Calculates repeat purchase frequency and flags low customer retention."""
        cust_col = df["customer_id"]
        if isinstance(cust_col, pd.DataFrame):
            cust_col = cust_col.iloc[:, 0]
        cust_counts = cust_col.dropna().value_counts()
        total_unique = len(cust_counts)

        if total_unique < 5:
            return None

        repeat_customers = int((cust_counts > 1).sum())
        repeat_rate = repeat_customers / total_unique
        threshold = settings.RETENTION_ALERT_THRESHOLD  # e.g. 0.25 (25%)

        if repeat_rate < threshold:
            confidence = calculate_confidence(sample_size=total_unique)
            shortfall = threshold - repeat_rate
            severity = calculate_severity(
                observed_deviation=shortfall,
                base_threshold=0.10,
                high_multiplier=1.5,
                critical_multiplier=2.0,
            )

            evidence = EvidenceBuilder.build_evidence(
                category=FindingCategory.CUSTOMER.value,
                subtype=FindingSubtype.RETENTION_PROBLEM.value,
                metric_name=MetricKeys.RETENTION_RATE,
                observed=round(repeat_rate * 100.0, 2),
                threshold=round(threshold * 100.0, 2),
                confidence=confidence,
                sample_size=total_unique,
                recommendation="Launch post-purchase email flows, loyalty reward points, and replenishment reminders.",
                context={
                    "total_unique_customers": total_unique,
                    "repeat_customers": repeat_customers,
                    "single_purchase_customers": total_unique - repeat_customers,
                },
            )

            return create_diagnostic_finding(
                dataset=dataset,
                finding_type=FindingType.CUSTOMER_CONCENTRATION,
                severity=severity,
                title=f"Low Customer Retention Rate ({round(repeat_rate * 100.0, 1)}%)",
                description=f"Only {round(repeat_rate * 100.0, 1)}% of customers ({repeat_customers}/{total_unique}) made a repeat purchase, below the {round(threshold * 100.0, 1)}% benchmark.",
                business_impact="Heavy reliance on one-time buyers drives up customer acquisition cost (CAC) payback periods.",
                metric_key=MetricKeys.RETENTION_RATE,
                confidence_score=confidence,
                supporting_data=evidence,
            )

        return None

    def _check_dataframe_customer_dynamics(
        self,
        dataset: Dataset,
        df: pd.DataFrame,
    ) -> List[DiagnosticFinding]:
        """Evaluates customer acquisition momentum (growth slowdown or acceleration) across time."""
        findings: List[DiagnosticFinding] = []
        try:
            working = df[["customer_id", "order_date"]].dropna().copy()
            working["order_date"] = pd.to_datetime(working["order_date"], errors="coerce")
            working = working.dropna()

            if len(working) < 5:
                return findings

            # Determine first-seen date per customer to compute new customer acquisition per period
            first_orders = working.groupby("customer_id")["order_date"].min().reset_index()
            first_orders.columns = ["customer_id", "first_date"]

            timespan_days = (first_orders["first_date"].max() - first_orders["first_date"].min()).days
            freq = "W" if timespan_days <= 60 else "M"

            try:
                period_acquisitions = (
                    first_orders.set_index("first_date")
                    .resample(freq)["customer_id"]
                    .nunique()
                    .reset_index()
                )
            except ValueError:
                freq = "ME" if freq == "M" else freq
                period_acquisitions = (
                    first_orders.set_index("first_date")
                    .resample(freq)["customer_id"]
                    .nunique()
                    .reset_index()
                )
            period_acquisitions.columns = ["period", "new_customers"]
            period_acquisitions = period_acquisitions[period_acquisitions["new_customers"] > 0]

            if len(period_acquisitions) < 2:
                return findings

            period_acquisitions["pct_change"] = period_acquisitions["new_customers"].pct_change()
            latest_change = period_acquisitions["pct_change"].iloc[-1]
            curr_acq = int(period_acquisitions["new_customers"].iloc[-1])
            prev_acq = int(period_acquisitions["new_customers"].iloc[-2])

            slowdown_threshold = settings.CUSTOMER_SLOWDOWN_THRESHOLD  # e.g. 0.05
            surge_threshold = settings.CUSTOMER_ACQUISITION_THRESHOLD  # e.g. 0.25

            # 1. Customer Acquisition Slowdown / Deceleration
            if latest_change is not None and latest_change <= -slowdown_threshold:
                drop_pct = abs(latest_change)
                severity = calculate_severity(
                    observed_deviation=drop_pct,
                    base_threshold=slowdown_threshold,
                    high_multiplier=2.0,
                    critical_multiplier=3.0,
                )
                confidence = calculate_confidence(sample_size=len(period_acquisitions))

                evidence = EvidenceBuilder.build_time_series_evidence(
                    category=FindingCategory.CUSTOMER.value,
                    subtype=FindingSubtype.CUSTOMER_GROWTH_SLOWDOWN.value,
                    metric_name=MetricKeys.UNIQUE_CUSTOMERS,
                    current_value=float(curr_acq),
                    previous_value=float(prev_acq),
                    change_percent=round(latest_change * 100.0, 2),
                    threshold=round(slowdown_threshold * 100.0, 2),
                    confidence=confidence,
                    period_count=len(period_acquisitions),
                    trend="negative",
                    recommendation="Optimize ad channel allocation, refresh landing page conversion funnels, and test referral programs.",
                )

                findings.append(
                    create_diagnostic_finding(
                        dataset=dataset,
                        finding_type=FindingType.CUSTOMER_CONCENTRATION,
                        severity=severity,
                        title=f"Customer Acquisition Slowdown (-{round(drop_pct * 100.0, 1)}%)",
                        description=f"New customer additions dropped from {prev_acq} to {curr_acq} over the latest period.",
                        business_impact="Slowing top-of-funnel velocity constrains future compound revenue growth.",
                        metric_key=MetricKeys.UNIQUE_CUSTOMERS,
                        confidence_score=confidence,
                        supporting_data=evidence,
                    )
                )

            # 2. Customer Acquisition Acceleration (Surge)
            elif latest_change is not None and latest_change >= surge_threshold:
                confidence = calculate_confidence(sample_size=len(period_acquisitions))
                evidence = EvidenceBuilder.build_time_series_evidence(
                    category=FindingCategory.CUSTOMER.value,
                    subtype=FindingSubtype.ACQUISITION_ACCELERATION.value,
                    metric_name=MetricKeys.UNIQUE_CUSTOMERS,
                    current_value=float(curr_acq),
                    previous_value=float(prev_acq),
                    change_percent=round(latest_change * 100.0, 2),
                    threshold=round(surge_threshold * 100.0, 2),
                    confidence=confidence,
                    period_count=len(period_acquisitions),
                    trend="positive",
                    recommendation="Ensure customer support onboarding capacity matches incoming user influx.",
                )

                findings.append(
                    create_diagnostic_finding(
                        dataset=dataset,
                        finding_type=FindingType.CUSTOMER_CONCENTRATION,
                        severity=FindingSeverity.LOW,
                        title=f"Customer Acquisition Surge (+{round(latest_change * 100.0, 1)}%)",
                        description=f"New customer acquisitions expanded from {prev_acq} to {curr_acq} in the latest period.",
                        business_impact="Strong market demand surge expands platform user base.",
                        metric_key=MetricKeys.UNIQUE_CUSTOMERS,
                        confidence_score=confidence,
                        supporting_data=evidence,
                    )
                )

        except Exception:
            pass

        return findings

    def _check_metrics_baseline(
        self,
        dataset: Dataset,
        metrics_map: dict,
    ) -> List[DiagnosticFinding]:
        """Tier 1: Evaluates customer health from summary KPI metrics (churn rate, customer counts)."""
        findings: List[DiagnosticFinding] = []

        # 1. Churn Rate Alert Check
        churn_val = metrics_map.get(MetricKeys.CHURN_RATE)
        churn_threshold = settings.CHURN_ALERT_THRESHOLD  # e.g. 0.10 (10%)

        if churn_val is not None and isinstance(churn_val, (int, float)):
            # Normalize percentage if formatted as 0-100
            churn_pct = (churn_val / 100.0) if churn_val > 1.0 else float(churn_val)
            if churn_pct >= churn_threshold:
                severity = calculate_severity(
                    observed_deviation=churn_pct,
                    base_threshold=churn_threshold,
                    high_multiplier=2.0,
                    critical_multiplier=3.0,
                )
                evidence = EvidenceBuilder.build_metric_evidence(
                    category=FindingCategory.CUSTOMER.value,
                    subtype=FindingSubtype.CHURN_INCREASE.value,
                    metric_name=MetricKeys.CHURN_RATE,
                    observed=round(churn_pct * 100.0, 2),
                    threshold=round(churn_threshold * 100.0, 2),
                    confidence=0.92,
                    sample_size=metrics_map.get(MetricKeys.UNIQUE_CUSTOMERS, 10),
                    recommendation="Identify high-risk customer segments, deploy proactive check-ins, and resolve satisfaction blockers.",
                )

                findings.append(
                    create_diagnostic_finding(
                        dataset=dataset,
                        finding_type=FindingType.CUSTOMER_CONCENTRATION,
                        severity=severity,
                        title=f"Elevated Customer Churn Rate ({round(churn_pct * 100.0, 1)}%)",
                        description=f"Customer churn rate of {round(churn_pct * 100.0, 1)}% exceeds acceptable SLA threshold of {round(churn_threshold * 100.0, 1)}%.",
                        business_impact="Accelerated customer attrition degrades lifetime value and inflates net replacement costs.",
                        metric_key=MetricKeys.CHURN_RATE,
                        confidence_score=0.92,
                        supporting_data=evidence,
                    )
                )

        # 2. Customer Satisfaction / Review Score Alert Check
        avg_review = metrics_map.get(MetricKeys.AVERAGE_REVIEW_SCORE)
        if avg_review is not None and isinstance(avg_review, (int, float)):
            review_val = float(avg_review)
            if review_val < 3.5:
                cat_sev, cat_flag, cat_mult = evaluate_catastrophic_escalation(
                    MetricKeys.AVERAGE_REVIEW_SCORE, review_val
                )
                severity = FindingSeverity.CRITICAL if review_val <= 2.0 else (
                    FindingSeverity.HIGH if review_val < 3.0 else FindingSeverity.MEDIUM
                )
                catastrophic_flag = cat_flag or (review_val <= 1.5)

                evidence = EvidenceBuilder.build_metric_evidence(
                    category=FindingCategory.CUSTOMER.value,
                    subtype=FindingSubtype.CHURN_INCREASE.value,
                    metric_name=MetricKeys.AVERAGE_REVIEW_SCORE,
                    observed=round(review_val, 2),
                    threshold=4.0,
                    confidence=0.90,
                    sample_size=metrics_map.get(MetricKeys.TOTAL_ORDERS, 20),
                    recommendation="Investigate root causes of customer dissatisfaction and deploy post-purchase recovery workflows.",
                    extra_context={
                        "catastrophic_flag": catastrophic_flag,
                        "escalation_multiplier": cat_mult,
                    },
                )

                findings.append(
                    create_diagnostic_finding(
                        dataset=dataset,
                        finding_type=FindingType.CUSTOMER_CONCENTRATION,
                        severity=severity,
                        title=f"Severe Customer Dissatisfaction (Avg Review: {round(review_val, 1)} / 5.0)",
                        description=f"Average customer review score dropped to {round(review_val, 1)} / 5.0, reflecting severe customer dissatisfaction.",
                        business_impact="Poor customer sentiment severely impairs retention and long-term brand equity.",
                        metric_key=MetricKeys.AVERAGE_REVIEW_SCORE,
                        confidence_score=0.90,
                        supporting_data=evidence,
                    )
                )

        return findings
