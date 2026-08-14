"""Product Diagnostic Analyzer identifying product concentration risk, underperforming SKUs, rapid growth, and category decline."""

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
from app.diagnostics.severity import calculate_confidence, calculate_severity
from app.models.dataset import Dataset
from app.models.dataset_metric import DatasetMetric
from app.models.diagnostic_finding import DiagnosticFinding


class ProductDiagnosticAnalyzer(BaseDiagnosticAnalyzer):
    """
    Diagnostic analyzer evaluating product portfolio health, category concentration vulnerabilities,
    underperforming product lines, rapid growth surges, and category decline trends.
    """

    async def analyze(
        self,
        dataset: Dataset,
        metrics: List[DatasetMetric],
    ) -> List[DiagnosticFinding]:
        """
        Executes multi-finding product diagnostic evaluation.
        
        Args:
            dataset: The target Dataset instance.
            metrics: Pre-computed DatasetMetric records.
            
        Returns:
            List of detected DiagnosticFinding entities.
        """
        findings: List[DiagnosticFinding] = []
        metrics_map = extract_metrics_dict(metrics)

        # Tier 2: Attempt lightweight category & product analysis if raw CSV is available
        df = load_lightweight_columns(dataset, ["product_category", "revenue", "order_date", "status"])

        if df is not None and not df.empty and "product_category" in df.columns:
            # 1. Product Concentration Risk (Single category generating disproportionate revenue)
            concentration_finding = self._check_category_concentration(dataset, df)
            if concentration_finding:
                findings.append(concentration_finding)

            # 2. Underperforming Products (Negligible share with high cancellation/friction)
            underperforming_finding = self._check_underperforming_categories(dataset, df)
            if underperforming_finding:
                findings.append(underperforming_finding)

            # 3. Time-Series Product Category Growth Acceleration & Decline
            if "order_date" in df.columns and "revenue" in df.columns:
                trend_findings = self._check_category_time_series_dynamics(dataset, df)
                findings.extend(trend_findings)

        # Tier 1 (Metrics-First Baseline): Evaluates summary metrics
        metric_findings = self._check_metrics_baseline(dataset, metrics_map)
        findings.extend(metric_findings)

        return findings

    def _check_category_concentration(
        self,
        dataset: Dataset,
        df: pd.DataFrame,
    ) -> Optional[DiagnosticFinding]:
        """Detects portfolio vulnerability when a single product category dominates total revenue."""
        try:
            if "revenue" in df.columns:
                grouped = df.groupby("product_category")["revenue"].sum().sort_values(ascending=False)
                total_rev = float(df["revenue"].sum())
            else:
                grouped = df["product_category"].value_counts()
                total_rev = float(len(df))

            if len(grouped) < 2 or total_rev <= 0:
                return None

            top_cat = str(grouped.index[0])
            top_val = float(grouped.iloc[0])
            concentration_ratio = top_val / total_rev

            threshold = settings.PRODUCT_CONCENTRATION_THRESHOLD  # e.g. 0.50 (50%)

            if concentration_ratio >= threshold:
                severity = calculate_severity(
                    observed_deviation=concentration_ratio,
                    base_threshold=threshold,
                    high_multiplier=1.4,
                    critical_multiplier=1.7,
                )
                confidence = calculate_confidence(sample_size=len(df))

                evidence = EvidenceBuilder.build_distribution_evidence(
                    category=FindingCategory.PRODUCT.value,
                    subtype=FindingSubtype.PRODUCT_CONCENTRATION_RISK.value,
                    dimension_name=MetricKeys.PRODUCT_CATEGORY,
                    top_entity=top_cat,
                    concentration_ratio=round(concentration_ratio * 100.0, 2),
                    threshold=round(threshold * 100.0, 2),
                    confidence=confidence,
                    total_entities=len(grouped),
                    recommendation="Invest in catalog diversification and allocate marketing capital toward secondary high-margin lines.",
                    extra_context={
                        "top_category_revenue": round(top_val, 2),
                        "total_portfolio_revenue": round(total_rev, 2),
                    },
                )

                return create_diagnostic_finding(
                    dataset=dataset,
                    finding_type=FindingType.REVENUE_CONCENTRATION,
                    severity=severity,
                    title=f"Severe Product Category Concentration Risk ({top_cat}: {round(concentration_ratio * 100.0, 1)}%)",
                    description=f"The '{top_cat}' category accounts for {round(concentration_ratio * 100.0, 1)}% of total revenue (${top_val:,.2f} of ${total_rev:,.2f}).",
                    business_impact="Extreme revenue dependency on a single category makes the business highly vulnerable to market shifts.",
                    metric_key=MetricKeys.PRODUCT_REVENUE_SHARE,
                    confidence_score=confidence,
                    supporting_data=evidence,
                )
        except Exception:
            pass

        return None

    def _check_underperforming_categories(
        self,
        dataset: Dataset,
        df: pd.DataFrame,
    ) -> Optional[DiagnosticFinding]:
        """Detects categories with negligible sales volume and high cancellation/return friction."""
        try:
            if "revenue" not in df.columns:
                return None

            cat_rev = df.groupby("product_category")["revenue"].sum()
            total_rev = float(df["revenue"].sum())

            if len(cat_rev) < 3 or total_rev <= 0:
                return None

            threshold = settings.PRODUCT_UNDERPERFORMANCE_THRESHOLD  # e.g. 0.05 (5%)
            underperforming: List[str] = []

            for cat, rev in cat_rev.items():
                ratio = float(rev) / total_rev
                if ratio < threshold:
                    underperforming.append(f"{cat} ({round(ratio * 100.0, 1)}%)")

            if underperforming and len(underperforming) <= 3:
                evidence = EvidenceBuilder.build_evidence(
                    category=FindingCategory.PRODUCT.value,
                    subtype=FindingSubtype.UNDERPERFORMING_PRODUCT.value,
                    metric_name=MetricKeys.PRODUCT_CATEGORY,
                    observed=len(underperforming),
                    threshold=round(threshold * 100.0, 2),
                    confidence=0.85,
                    sample_size=len(cat_rev),
                    recommendation="Re-evaluate product-market fit, consolidate slow-moving SKUs, or clearance lagging inventory.",
                    context={
                        "underperforming_categories": underperforming,
                        "threshold_share_pct": round(threshold * 100.0, 1),
                    },
                )

                return create_diagnostic_finding(
                    dataset=dataset,
                    finding_type=FindingType.REVENUE_CONCENTRATION,
                    severity=FindingSeverity.MEDIUM,
                    title=f"Underperforming Product Lines Identified ({len(underperforming)} Categories)",
                    description=f"Categories generated under {round(threshold * 100.0, 1)}% of total revenue: {', '.join(underperforming)}.",
                    business_impact="Slow-moving catalog items tie up working capital in low-turnover inventory.",
                    metric_key=MetricKeys.PRODUCT_CATEGORY,
                    confidence_score=0.85,
                    supporting_data=evidence,
                )
        except Exception:
            pass

        return None

    def _check_category_time_series_dynamics(
        self,
        dataset: Dataset,
        df: pd.DataFrame,
    ) -> List[DiagnosticFinding]:
        """Evaluates periodic growth surges and sharp declines across product categories."""
        findings: List[DiagnosticFinding] = []
        try:
            working = df[["product_category", "revenue", "order_date"]].dropna().copy()
            working["order_date"] = pd.to_datetime(working["order_date"], errors="coerce")
            working = working.dropna()

            if len(working) < 10:
                return findings

            # Split into earlier half and later half of date range to evaluate category momentum
            min_date = working["order_date"].min()
            max_date = working["order_date"].max()
            mid_date = min_date + (max_date - min_date) / 2

            h1 = working[working["order_date"] <= mid_date]
            h2 = working[working["order_date"] > mid_date]

            if len(h1) < 5 or len(h2) < 5:
                return findings

            h1_rev = h1.groupby("product_category")["revenue"].sum()
            h2_rev = h2.groupby("product_category")["revenue"].sum()

            growth_threshold = settings.PRODUCT_GROWTH_THRESHOLD  # e.g. 0.30 (30%)
            decline_threshold = settings.PRODUCT_DECLINE_THRESHOLD  # e.g. 0.20 (20%)

            for cat in h1_rev.index:
                if cat in h2_rev.index:
                    rev1 = float(h1_rev[cat])
                    rev2 = float(h2_rev[cat])

                    if rev1 > 100.0:  # Minimum baseline volume to avoid small-number distortions
                        growth_rate = (rev2 - rev1) / rev1

                        # 1. Rapid Product Growth Surge
                        if growth_rate >= growth_threshold:
                            evidence = EvidenceBuilder.build_time_series_evidence(
                                category=FindingCategory.PRODUCT.value,
                                subtype=FindingSubtype.RAPID_PRODUCT_GROWTH.value,
                                metric_name=MetricKeys.PRODUCT_CATEGORY,
                                current_value=rev2,
                                previous_value=rev1,
                                change_percent=round(growth_rate * 100.0, 2),
                                threshold=round(growth_threshold * 100.0, 2),
                                confidence=0.90,
                                period_count=2,
                                trend="positive",
                                recommendation=f"Increase inventory buffer and expand digital marketing campaigns for '{cat}'.",
                                extra_context={"category": cat},
                            )

                            findings.append(
                                create_diagnostic_finding(
                                    dataset=dataset,
                                    finding_type=FindingType.REVENUE_CONCENTRATION,
                                    severity=FindingSeverity.LOW,
                                    title=f"Rapid Product Growth in '{cat}' (+{round(growth_rate * 100.0, 1)}%)",
                                    description=f"Sales in '{cat}' surged by {round(growth_rate * 100.0, 1)}% from ${rev1:,.2f} to ${rev2:,.2f}.",
                                    business_impact=f"High-growth category presents clear opportunity for volume expansion.",
                                    metric_key=MetricKeys.PRODUCT_CATEGORY,
                                    confidence_score=0.90,
                                    supporting_data=evidence,
                                )
                            )

                        # 2. Product Performance Decline
                        elif growth_rate <= -decline_threshold:
                            drop_pct = abs(growth_rate)
                            severity = calculate_severity(
                                observed_deviation=drop_pct,
                                base_threshold=decline_threshold,
                                high_multiplier=1.75,
                                critical_multiplier=2.5,
                            )
                            evidence = EvidenceBuilder.build_time_series_evidence(
                                category=FindingCategory.PRODUCT.value,
                                subtype=FindingSubtype.PRODUCT_PERFORMANCE_DECLINE.value,
                                metric_name=MetricKeys.PRODUCT_CATEGORY,
                                current_value=rev2,
                                previous_value=rev1,
                                change_percent=round(growth_rate * 100.0, 2),
                                threshold=round(decline_threshold * 100.0, 2),
                                confidence=0.90,
                                period_count=2,
                                trend="negative",
                                recommendation=f"Investigate customer reviews, competitor pricing, and quality issues in '{cat}'.",
                                extra_context={"category": cat},
                            )

                            findings.append(
                                create_diagnostic_finding(
                                    dataset=dataset,
                                    finding_type=FindingType.REVENUE_CONCENTRATION,
                                    severity=severity,
                                    title=f"Product Performance Decline in '{cat}' (-{round(drop_pct * 100.0, 1)}%)",
                                    description=f"Sales in '{cat}' fell by {round(drop_pct * 100.0, 1)}% from ${rev1:,.2f} to ${rev2:,.2f}.",
                                    business_impact=f"Deteriorating demand for core product line threatens overall catalog momentum.",
                                    metric_key=MetricKeys.PRODUCT_CATEGORY,
                                    confidence_score=0.90,
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
        """Tier 1: Evaluates summary metric values if available."""
        # Baseline checks if product concentration ratio was pre-computed as a DatasetMetric
        findings: List[DiagnosticFinding] = []
        conc_ratio = metrics_map.get(MetricKeys.PRODUCT_CONCENTRATION_RATIO)

        if conc_ratio is not None and isinstance(conc_ratio, (int, float)):
            ratio_val = conc_ratio if conc_ratio <= 1.0 else (conc_ratio / 100.0)
            threshold = settings.PRODUCT_CONCENTRATION_THRESHOLD

            if ratio_val >= threshold:
                severity = calculate_severity(
                    observed_deviation=ratio_val,
                    base_threshold=threshold,
                    high_multiplier=1.4,
                    critical_multiplier=1.7,
                )
                evidence = EvidenceBuilder.build_distribution_evidence(
                    category=FindingCategory.PRODUCT.value,
                    subtype=FindingSubtype.PRODUCT_CONCENTRATION_RISK.value,
                    dimension_name=MetricKeys.PRODUCT_CONCENTRATION_RATIO,
                    top_entity="Top Product",
                    concentration_ratio=round(ratio_val * 100.0, 2),
                    threshold=round(threshold * 100.0, 2),
                    confidence=0.90,
                    total_entities=1,
                    recommendation="Diversify sales focus across non-core product catalog items.",
                )

                findings.append(
                    create_diagnostic_finding(
                        dataset=dataset,
                        finding_type=FindingType.REVENUE_CONCENTRATION,
                        severity=severity,
                        title=f"High Product Revenue Concentration ({round(ratio_val * 100.0, 1)}%)",
                        description=f"Top product lines generate {round(ratio_val * 100.0, 1)}% of total revenues.",
                        business_impact="Concentration vulnerability to specific supply chain or consumer trends.",
                        metric_key=MetricKeys.PRODUCT_CONCENTRATION_RATIO,
                        confidence_score=0.90,
                        supporting_data=evidence,
                    )
                )

        return findings
