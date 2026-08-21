"""Operational Diagnostic Analyzer detecting cost surges, margin compression, delivery delays, and fulfillment efficiency."""

import logging
from typing import Dict, List, Optional
import pandas as pd

from app.core.config import settings
from app.core.constants import FindingCategory, FindingSeverity, FindingSubtype, FindingType, MetricCategory
from app.diagnostics.base_analyzer import BaseDiagnosticAnalyzer
from app.diagnostics.evidence_builder import EvidenceBuilder
from app.diagnostics.helpers import (
    compute_time_series_aggregates,
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

logger = logging.getLogger(__name__)


class OperationalDiagnosticAnalyzer(BaseDiagnosticAnalyzer):
    """
    Diagnostic analyzer evaluating operational fulfillment, logistics delays, order failure rates,
    cost fluctuations, and efficiency opportunities.
    """

    async def analyze(
        self,
        dataset: Dataset,
        metrics: List[DatasetMetric],
    ) -> List[DiagnosticFinding]:
        """
        Executes multi-finding operational diagnostic evaluation.
        
        Args:
            dataset: The target Dataset instance.
            metrics: Pre-computed DatasetMetric records.
            
        Returns:
            List of detected DiagnosticFinding entities.
        """
        findings: List[DiagnosticFinding] = []
        metrics_map = extract_metrics_dict(metrics)

        # Tier 2: Attempt lightweight operational analysis if raw CSV is available
        raw_df = load_lightweight_columns(dataset, ["order_date", "delivery_time", "status", "cost", "revenue"])

        if raw_df is not None and not raw_df.empty:
            # 1. Cost Surge Analysis (if cost and date are present)
            if "cost" in raw_df.columns and "order_date" in raw_df.columns:
                cost_finding = self._check_time_series_cost_spike(dataset, raw_df)
                if cost_finding:
                    findings.append(cost_finding)

            # 2. Margin Compression Analysis (if both revenue and cost are present)
            if "revenue" in raw_df.columns and "cost" in raw_df.columns:
                margin_finding = self._check_dataframe_margin_compression(dataset, raw_df)
                if margin_finding:
                    findings.append(margin_finding)

        # Tier 1 (Metrics-First Baseline): Evaluates fulfillment KPIs from DatasetMetrics
        metric_findings = self._check_metrics_baseline(dataset, metrics_map)
        findings.extend(metric_findings)

        return findings

    def _check_time_series_cost_spike(
        self,
        dataset: Dataset,
        raw_df,
    ) -> Optional[DiagnosticFinding]:
        """Detects sudden spikes in operational and fulfillment costs across periods."""
        ts_cost = compute_time_series_aggregates(raw_df, date_col="order_date", value_col="cost")
        if ts_cost is None or len(ts_cost) < 2:
            return None

        latest_pct_change = ts_cost["pct_change"].iloc[-1]
        threshold = settings.COST_SPIKE_THRESHOLD  # e.g. 0.20 (20%)

        if latest_pct_change is not None and latest_pct_change >= threshold:
            curr_cost = float(ts_cost["total"].iloc[-1])
            prev_cost = float(ts_cost["total"].iloc[-2])
            severity = calculate_severity(
                observed_deviation=latest_pct_change,
                base_threshold=threshold,
                high_multiplier=1.75,
                critical_multiplier=2.5,
            )
            confidence = calculate_confidence(sample_size=len(ts_cost))

            evidence = EvidenceBuilder.build_time_series_evidence(
                category=FindingCategory.OPERATIONAL.value,
                subtype=FindingSubtype.COST_SPIKE.value,
                metric_name=MetricKeys.TOTAL_COST,
                current_value=curr_cost,
                previous_value=prev_cost,
                change_percent=round(latest_pct_change * 100.0, 2),
                threshold=round(threshold * 100.0, 2),
                confidence=confidence,
                period_count=len(ts_cost),
                trend="positive",
                recommendation="Audit supplier rate cards, negotiate shipping bulk discounts, and optimize route dispatch.",
            )

            return create_diagnostic_finding(
                dataset=dataset,
                finding_type=FindingType.DATA_QUALITY_RISK,
                severity=severity,
                title=f"Abnormal Operational Cost Surge (+{round(latest_pct_change * 100.0, 1)}%)",
                description=f"Operating costs increased by {round(latest_pct_change * 100.0, 1)}% from ${prev_cost:,.2f} to ${curr_cost:,.2f} over the latest period.",
                business_impact="Cost inflation directly erodes gross margins and operational cash flow.",
                metric_key=MetricKeys.TOTAL_COST,
                confidence_score=confidence,
                supporting_data=evidence,
            )

        return None

    def _check_dataframe_margin_compression(
        self,
        dataset: Dataset,
        raw_df,
    ) -> Optional[DiagnosticFinding]:
        """Detects gross profit margin contraction when costs rise faster than revenues."""
        try:
            threshold = settings.MARGIN_COMPRESSION_THRESHOLD  # e.g. 0.05 (5% margin drop)

            if "order_date" in raw_df.columns and "revenue" in raw_df.columns and "cost" in raw_df.columns:
                working = raw_df[["order_date", "revenue", "cost"]].dropna().copy()
                working["order_date"] = pd.to_datetime(working["order_date"], errors="coerce")
                working["revenue"] = pd.to_numeric(working["revenue"], errors="coerce")
                working["cost"] = pd.to_numeric(working["cost"], errors="coerce")
                working = working.dropna().sort_values(by="order_date")

                if len(working) < 2:
                    return None

                min_dt = working["order_date"].min()
                max_dt = working["order_date"].max()
                months_span = (max_dt.year - min_dt.year) * 12 + (max_dt.month - min_dt.month)
                timespan_days = (max_dt - min_dt).days

                if months_span >= 1:
                    freq = "ME"
                elif timespan_days >= 14:
                    freq = "W"
                else:
                    freq = "D"

                try:
                    rev_grouped = working.set_index("order_date").resample(freq)["revenue"].sum()
                    cost_grouped = working.set_index("order_date").resample(freq)["cost"].sum()
                except ValueError:
                    freq = "M" if freq == "ME" else freq
                    rev_grouped = working.set_index("order_date").resample(freq)["revenue"].sum()
                    cost_grouped = working.set_index("order_date").resample(freq)["cost"].sum()

                period_df = pd.DataFrame({"revenue": rev_grouped, "cost": cost_grouped}).reset_index()
                period_df = period_df[period_df["revenue"] > 0].copy()

                if len(period_df) >= 2:
                    period_df["margin"] = (period_df["revenue"] - period_df["cost"]) / period_df["revenue"]
                    curr_margin = float(period_df["margin"].iloc[-1])
                    prev_margin = float(period_df["margin"].iloc[-2])
                    margin_drop = prev_margin - curr_margin

                    if margin_drop >= threshold or curr_margin < threshold:
                        severity = calculate_severity(
                            observed_deviation=margin_drop if margin_drop > 0 else (threshold - curr_margin),
                            base_threshold=threshold,
                            high_multiplier=2.0,
                            critical_multiplier=3.0,
                        )
                        confidence = calculate_confidence(sample_size=len(period_df))

                        evidence = EvidenceBuilder.build_metric_evidence(
                            category=FindingCategory.OPERATIONAL.value,
                            subtype=FindingSubtype.MARGIN_COMPRESSION.value,
                            metric_name=MetricKeys.GROSS_MARGIN,
                            observed=round(curr_margin * 100.0, 2),
                            threshold=round(threshold * 100.0, 2),
                            confidence=confidence,
                            sample_size=len(period_df),
                            recommendation="Review product pricing structures, re-negotiate procurement costs, and eliminate unprofitable discounts.",
                            change_percent=round(-margin_drop * 100.0, 2) if margin_drop > 0 else None,
                            trend="negative",
                            extra_context={
                                "previous_margin_pct": round(prev_margin * 100.0, 2),
                                "current_margin_pct": round(curr_margin * 100.0, 2),
                                "margin_contraction_points": round(margin_drop * 100.0, 2),
                            },
                        )

                        return create_diagnostic_finding(
                            dataset=dataset,
                            finding_type=FindingType.REVENUE_DROP,
                            severity=severity,
                            title=f"Gross Margin Compression (-{round(margin_drop * 100.0, 1)} pts to {round(curr_margin * 100.0, 1)}%)",
                            description=f"Gross margin contracted by {round(margin_drop * 100.0, 1)} percentage points from {round(prev_margin * 100.0, 1)}% to {round(curr_margin * 100.0, 1)}% due to cost surges.",
                            business_impact="Operating profitability contraction threatens enterprise unit economics and EBITDA margins.",
                            metric_key=MetricKeys.GROSS_MARGIN,
                            confidence_score=confidence,
                            supporting_data=evidence,
                        )

            # Fallback for non-temporal datasets
            total_rev = float(raw_df["revenue"].sum())
            total_cost = float(raw_df["cost"].sum())
            if total_rev > 0:
                gross_margin = (total_rev - total_cost) / total_rev
                if gross_margin < threshold:
                    margin_deficit = threshold - gross_margin
                    severity = calculate_severity(
                        observed_deviation=margin_deficit,
                        base_threshold=0.05,
                        high_multiplier=2.0,
                        critical_multiplier=3.0,
                    )
                    evidence = EvidenceBuilder.build_metric_evidence(
                        category=FindingCategory.OPERATIONAL.value,
                        subtype=FindingSubtype.MARGIN_COMPRESSION.value,
                        metric_name=MetricKeys.GROSS_MARGIN,
                        observed=round(gross_margin * 100.0, 2),
                        threshold=round(threshold * 100.0, 2),
                        confidence=0.90,
                        sample_size=len(raw_df),
                        recommendation="Review product pricing structures and re-negotiate procurement costs.",
                    )
                    return create_diagnostic_finding(
                        dataset=dataset,
                        finding_type=FindingType.REVENUE_DROP,
                        severity=severity,
                        title=f"Gross Margin Compression ({round(gross_margin * 100.0, 1)}%)",
                        description=f"Gross margin contracted to {round(gross_margin * 100.0, 1)}%, falling below the target {round(threshold * 100.0, 1)}% floor.",
                        business_impact="Low operating profitability threatens corporate sustainability.",
                        metric_key=MetricKeys.GROSS_MARGIN,
                        confidence_score=0.90,
                        supporting_data=evidence,
                    )
        except Exception as e:
            logger.debug(f"Margin compression analysis failed: {e}")

        return None

    def _check_metrics_baseline(
        self,
        dataset: Dataset,
        metrics_map: dict,
    ) -> List[DiagnosticFinding]:
        """Tier 1: Evaluates fulfillment KPIs (delivery delays, cancellation spikes, productivity)."""
        findings: List[DiagnosticFinding] = []

        # 1. Delivery Delay Anomaly
        avg_delivery = metrics_map.get(MetricKeys.AVERAGE_DELIVERY_TIME)
        delay_threshold = settings.OPERATIONAL_DELAY_THRESHOLD  # e.g. 5.0 days

        if avg_delivery is not None and isinstance(avg_delivery, (int, float)):
            if avg_delivery >= delay_threshold:
                excess_days = avg_delivery - delay_threshold
                severity = calculate_severity(
                    observed_deviation=excess_days,
                    base_threshold=1.0,
                    high_multiplier=2.0,
                    critical_multiplier=3.0,
                )
                catastrophic_flag = False
                escalation_multiplier = 1.0

                # Catastrophic escalation (10d -> CRITICAL, 15d -> CRITICAL+catastrophic, 20d -> 1.5x)
                cat_sev, cat_flag, cat_mult = evaluate_catastrophic_escalation(
                    MetricKeys.AVERAGE_DELIVERY_TIME, avg_delivery
                )
                if cat_sev == FindingSeverity.CRITICAL:
                    severity = FindingSeverity.CRITICAL
                    catastrophic_flag = cat_flag
                    escalation_multiplier = cat_mult

                evidence = EvidenceBuilder.build_metric_evidence(
                    category=FindingCategory.OPERATIONAL.value,
                    subtype=FindingSubtype.DELIVERY_DELAY.value,
                    metric_name=MetricKeys.AVERAGE_DELIVERY_TIME,
                    observed=round(float(avg_delivery), 2),
                    threshold=round(float(delay_threshold), 2),
                    confidence=0.92,
                    sample_size=metrics_map.get(MetricKeys.TOTAL_ORDERS, 10),
                    recommendation="Reallocate orders to regional fulfillment hubs and partner with expedited local courier networks.",
                    extra_context={
                        "catastrophic_flag": catastrophic_flag,
                        "escalation_multiplier": escalation_multiplier,
                    },
                )

                findings.append(
                    create_diagnostic_finding(
                        dataset=dataset,
                        finding_type=FindingType.DELIVERY_DELAY,
                        severity=severity,
                        title=f"Excessive Delivery Lead Time ({round(float(avg_delivery), 1)} Days)",
                        description=f"Average shipping and delivery turnaround is {round(float(avg_delivery), 1)} days, breaching the {delay_threshold} days SLA.",
                        business_impact="Extended transit times drive up customer dissatisfaction and support inquiry tickets.",
                        metric_key=MetricKeys.AVERAGE_DELIVERY_TIME,
                        confidence_score=0.92,
                        supporting_data=evidence,
                    )
                )

        # 2. Order Cancellation / Fulfillment Inefficiency
        completion_rate = metrics_map.get(MetricKeys.COMPLETION_RATE)
        canc_threshold = settings.OPERATIONAL_CANCELLATION_THRESHOLD  # e.g. 0.15 (15%)

        if completion_rate is not None and isinstance(completion_rate, (int, float)):
            comp_val = completion_rate if completion_rate <= 1.0 else (completion_rate / 100.0)
            canc_rate = 1.0 - comp_val

            if canc_rate >= canc_threshold:
                severity = calculate_severity(
                    observed_deviation=canc_rate,
                    base_threshold=canc_threshold,
                    high_multiplier=1.75,
                    critical_multiplier=2.5,
                )
                catastrophic_flag = False
                escalation_multiplier = 1.0

                # Catastrophic escalation (50% -> CRITICAL, 75% -> CRITICAL+catastrophic, 90% -> 1.5x)
                cat_sev, cat_flag, cat_mult = evaluate_catastrophic_escalation(
                    MetricKeys.CANCELLATION_RATE, canc_rate
                )
                if cat_sev == FindingSeverity.CRITICAL:
                    severity = FindingSeverity.CRITICAL
                    catastrophic_flag = cat_flag
                    escalation_multiplier = cat_mult

                evidence = EvidenceBuilder.build_metric_evidence(
                    category=FindingCategory.OPERATIONAL.value,
                    subtype=FindingSubtype.OPERATIONAL_INEFFICIENCY.value,
                    metric_name=MetricKeys.COMPLETION_RATE,
                    observed=round(canc_rate * 100.0, 2),
                    threshold=round(canc_threshold * 100.0, 2),
                    confidence=0.95,
                    sample_size=metrics_map.get(MetricKeys.TOTAL_ORDERS, 20),
                    recommendation="Audit stock availability synchronization and address payment gateway checkout drop-offs.",
                    extra_context={
                        "completion_rate": round(comp_val * 100.0, 2),
                        "cancelled_orders": metrics_map.get(MetricKeys.CANCELLED_ORDERS),
                        "catastrophic_flag": catastrophic_flag,
                        "escalation_multiplier": escalation_multiplier,
                    },
                )

                findings.append(
                    create_diagnostic_finding(
                        dataset=dataset,
                        finding_type=FindingType.HIGH_CANCELLATION_RATE,
                        severity=severity,
                        title=f"High Order Cancellation Rate ({round(canc_rate * 100.0, 1)}%)",
                        description=f"Order cancellation rate reached {round(canc_rate * 100.0, 1)}%, exceeding the {round(canc_threshold * 100.0, 1)}% maximum allowable limit.",
                        business_impact="High cancellations trigger lost inventory holding costs and unrealized GMV revenue.",
                        metric_key=MetricKeys.COMPLETION_RATE,
                        confidence_score=0.95,
                        supporting_data=evidence,
                    )
                )

            # 3. Productivity & Fulfillment Efficiency Opportunity
            elif comp_val >= 0.95 and (avg_delivery is None or avg_delivery <= 3.0):
                evidence = EvidenceBuilder.build_metric_evidence(
                    category=FindingCategory.OPERATIONAL.value,
                    subtype=FindingSubtype.PRODUCTIVITY_IMPROVEMENT.value,
                    metric_name=MetricKeys.COMPLETION_RATE,
                    observed=round(comp_val * 100.0, 2),
                    threshold=95.0,
                    confidence=0.90,
                    sample_size=metrics_map.get(MetricKeys.TOTAL_ORDERS, 20),
                    recommendation="Maintain standard fulfillment workflows and benchmark peak hub protocols.",
                )

                findings.append(
                    create_diagnostic_finding(
                        dataset=dataset,
                        finding_type=FindingType.LOW_COMPLETION_RATE,
                        severity=FindingSeverity.LOW,
                        title=f"High Fulfillment Productivity ({round(comp_val * 100.0, 1)}% Completion)",
                        description=f"Fulfillment operations achieved a {round(comp_val * 100.0, 1)}% successful completion rate.",
                        business_impact="High operational reliability boosts customer trust and repeat ordering frequency.",
                        metric_key=MetricKeys.COMPLETION_RATE,
                        confidence_score=0.90,
                        supporting_data=evidence,
                    )
                )

        return findings
