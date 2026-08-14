"""Metric calculator engine computing structured business KPIs from parsed and mapped datasets."""

from dataclasses import dataclass
from typing import Any, Dict, List, Set, Tuple
import pandas as pd
from app.core.constants import MetricCategory
from app.core.logging import logger


@dataclass
class CalculatedMetric:
    """Dataclass representing a computed metric result."""
    metric_key: str
    metric_name: str
    metric_category: MetricCategory
    metric_value: Any


class KPICalculator:
    """Calculates category-specific KPIs from a pandas DataFrame and its verified column mappings."""

    def __init__(self, df: pd.DataFrame, mapped_fields: Dict[str, str]):
        """
        Args:
            df: Parsed pandas DataFrame containing dataset rows.
            mapped_fields: Dictionary of original_column_name -> standard_business_field.
        """
        self.raw_df = df
        self.mapped_fields = {orig: std for orig, std in mapped_fields.items() if std}
        self.working_df = self._prepare_working_dataframe()
        self.available_fields = set(self.mapped_fields.values())

    def _prepare_working_dataframe(self) -> pd.DataFrame:
        """Creates a DataFrame with standardized business column names."""
        df = self.raw_df.copy()
        rename_map = {orig: std for orig, std in self.mapped_fields.items() if orig in df.columns}
        return df.rename(columns=rename_map)

    def calculate_all(self) -> Tuple[List[CalculatedMetric], List[str]]:
        """
        Runs all category KPI calculators.
        
        Returns:
            Tuple of (list of CalculatedMetrics, list of skipped category names).
        """
        metrics: List[CalculatedMetric] = []
        skipped_categories: List[str] = []

        # 1. Dataset Quality Metrics (Always calculated)
        metrics.extend(self._calculate_quality_metrics())

        # 2. Revenue Metrics
        if "revenue" in self.available_fields:
            metrics.extend(self._calculate_revenue_metrics())
        else:
            skipped_categories.append(MetricCategory.REVENUE.value)

        # 3. Order Metrics
        if "order_id" in self.available_fields:
            metrics.extend(self._calculate_order_metrics())
        else:
            skipped_categories.append(MetricCategory.ORDERS.value)

        # 4. Customer Metrics
        if "customer_id" in self.available_fields:
            metrics.extend(self._calculate_customer_metrics())
        else:
            skipped_categories.append(MetricCategory.CUSTOMERS.value)

        # 5. Review Metrics
        if "review_score" in self.available_fields:
            metrics.extend(self._calculate_review_metrics())
        else:
            skipped_categories.append(MetricCategory.REVIEWS.value)

        # 6. Delivery Metrics
        if "delivery_time" in self.available_fields:
            metrics.extend(self._calculate_delivery_metrics())
        else:
            skipped_categories.append(MetricCategory.DELIVERY.value)

        return metrics, skipped_categories

    def _calculate_quality_metrics(self) -> List[CalculatedMetric]:
        """Calculates general dataset structural quality KPIs."""
        total_records = len(self.working_df)
        total_columns = len(self.working_df.columns)
        total_cells = total_records * total_columns

        if total_cells > 0:
            null_cells = int(self.working_df.isnull().sum().sum())
            completeness = round((1.0 - (null_cells / total_cells)) * 100.0, 2)
        else:
            completeness = 0.0

        return [
            CalculatedMetric(
                metric_key="record_count",
                metric_name="Total Records",
                metric_category=MetricCategory.QUALITY,
                metric_value=total_records,
            ),
            CalculatedMetric(
                metric_key="column_count",
                metric_name="Total Columns",
                metric_category=MetricCategory.QUALITY,
                metric_value=total_columns,
            ),
            CalculatedMetric(
                metric_key="completeness_percentage",
                metric_name="Data Completeness (%)",
                metric_category=MetricCategory.QUALITY,
                metric_value=completeness,
            ),
        ]

    def _calculate_revenue_metrics(self) -> List[CalculatedMetric]:
        """Calculates revenue aggregation KPIs with division-by-zero protection."""
        metrics: List[CalculatedMetric] = []
        rev_series = pd.to_numeric(self.working_df["revenue"], errors="coerce").dropna()

        if len(rev_series) > 0:
            tot_rev = round(float(rev_series.sum()), 2)
            avg_rev = round(float(rev_series.mean()), 2)
            max_rev = round(float(rev_series.max()), 2)
            min_rev = round(float(rev_series.min()), 2)
        else:
            tot_rev, avg_rev, max_rev, min_rev = 0.0, 0.0, 0.0, 0.0

        metrics.extend([
            CalculatedMetric(
                metric_key="total_revenue",
                metric_name="Total Revenue",
                metric_category=MetricCategory.REVENUE,
                metric_value=tot_rev,
            ),
            CalculatedMetric(
                metric_key="average_revenue",
                metric_name="Average Revenue",
                metric_category=MetricCategory.REVENUE,
                metric_value=avg_rev,
            ),
            CalculatedMetric(
                metric_key="maximum_revenue",
                metric_name="Maximum Revenue",
                metric_category=MetricCategory.REVENUE,
                metric_value=max_rev,
            ),
            CalculatedMetric(
                metric_key="minimum_revenue",
                metric_name="Minimum Revenue",
                metric_category=MetricCategory.REVENUE,
                metric_value=min_rev,
            ),
        ])

        # Cross-category KPI: revenue_per_customer (Requires both revenue and customer_id)
        if "customer_id" in self.available_fields:
            cust_series = self.working_df["customer_id"].dropna()
            unique_custs = int(cust_series.nunique())
            rev_per_cust = round(tot_rev / unique_custs, 2) if unique_custs > 0 else 0.0
            metrics.append(
                CalculatedMetric(
                    metric_key="revenue_per_customer",
                    metric_name="Revenue Per Customer",
                    metric_category=MetricCategory.REVENUE,
                    metric_value=rev_per_cust,
                )
            )

        return metrics

    def _calculate_order_metrics(self) -> List[CalculatedMetric]:
        """Calculates order volume and fulfillment rate KPIs."""
        metrics: List[CalculatedMetric] = []
        orders_series = self.working_df["order_id"].dropna()
        total_orders = int(orders_series.nunique())

        metrics.append(
            CalculatedMetric(
                metric_key="total_orders",
                metric_name="Total Orders",
                metric_category=MetricCategory.ORDERS,
                metric_value=total_orders,
            )
        )

        if "status" in self.available_fields:
            status_series = self.working_df["status"].astype(str).str.lower().str.strip()
            completed_aliases = {"completed", "delivered", "shipped", "paid", "success", "complete"}
            cancelled_aliases = {"cancelled", "canceled", "failed", "returned", "refunded"}

            completed_orders = int(status_series.isin(completed_aliases).sum())
            cancelled_orders = int(status_series.isin(cancelled_aliases).sum())
            completion_rate = round((completed_orders / total_orders * 100.0), 2) if total_orders > 0 else 0.0

            metrics.extend([
                CalculatedMetric(
                    metric_key="completed_orders",
                    metric_name="Completed Orders",
                    metric_category=MetricCategory.ORDERS,
                    metric_value=completed_orders,
                ),
                CalculatedMetric(
                    metric_key="cancelled_orders",
                    metric_name="Cancelled Orders",
                    metric_category=MetricCategory.ORDERS,
                    metric_value=cancelled_orders,
                ),
                CalculatedMetric(
                    metric_key="completion_rate",
                    metric_name="Completion Rate (%)",
                    metric_category=MetricCategory.ORDERS,
                    metric_value=completion_rate,
                ),
            ])

        return metrics

    def _calculate_customer_metrics(self) -> List[CalculatedMetric]:
        """Calculates customer metrics."""
        cust_series = self.working_df["customer_id"].dropna()
        unique_customers = int(cust_series.nunique())

        return [
            CalculatedMetric(
                metric_key="unique_customers",
                metric_name="Unique Customers",
                metric_category=MetricCategory.CUSTOMERS,
                metric_value=unique_customers,
            )
        ]

    def _calculate_review_metrics(self) -> List[CalculatedMetric]:
        """Calculates customer review and satisfaction KPIs."""
        review_series = pd.to_numeric(self.working_df["review_score"], errors="coerce").dropna()
        avg_score = round(float(review_series.mean()), 2) if len(review_series) > 0 else 0.0

        return [
            CalculatedMetric(
                metric_key="average_review_score",
                metric_name="Average Review Score",
                metric_category=MetricCategory.REVIEWS,
                metric_value=avg_score,
            )
        ]

    def _calculate_delivery_metrics(self) -> List[CalculatedMetric]:
        """Calculates shipping and fulfillment duration KPIs."""
        delivery_series = pd.to_numeric(self.working_df["delivery_time"], errors="coerce").dropna()
        avg_time = round(float(delivery_series.mean()), 2) if len(delivery_series) > 0 else 0.0

        return [
            CalculatedMetric(
                metric_key="average_delivery_time",
                metric_name="Avg Delivery Time",
                metric_category=MetricCategory.DELIVERY,
                metric_value=avg_time,
            )
        ]
