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
        self.available_fields = set(self.working_df.columns)

    def _prepare_working_dataframe(self) -> pd.DataFrame:
        """Creates a DataFrame with standardized business column names while preventing duplicate column collisions."""
        df = self.raw_df.copy()

        # 1. Resolve safe 1-to-1 canonical mappings
        used_canonical_targets: Set[str] = set()
        rename_map: Dict[str, str] = {}

        # Priority 1: Exact matches (source column name == canonical target)
        for orig, std in self.mapped_fields.items():
            if orig in df.columns and std and orig == std:
                rename_map[orig] = std
                used_canonical_targets.add(std)

        # Priority 2: Remaining mapped fields if target is not yet claimed
        for orig, std in self.mapped_fields.items():
            if orig in df.columns and std and orig not in rename_map:
                if std not in used_canonical_targets:
                    rename_map[orig] = std
                    used_canonical_targets.add(std)
                else:
                    logger.warning(
                        f"Duplicate canonical mapping detected: column '{orig}' also mapped to '{std}'. "
                        f"Retaining original column name '{orig}' to prevent duplicate column collisions."
                    )

        renamed_df = df.rename(columns=rename_map)

        # Guarantee all column headers in working_df are unique
        if renamed_df.columns.duplicated().any():
            unique_cols = []
            col_counts: Dict[str, int] = {}
            for col in renamed_df.columns:
                if col in col_counts:
                    col_counts[col] += 1
                    unique_cols.append(f"{col}_{col_counts[col]}")
                else:
                    col_counts[col] = 0
                    unique_cols.append(col)
            renamed_df.columns = unique_cols

        return renamed_df

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
        if "order_id" in self.available_fields or "orders" in self.available_fields:
            metrics.extend(self._calculate_order_metrics())
        else:
            skipped_categories.append(MetricCategory.ORDERS.value)

        # 4. Customer Metrics
        if (
            "customer_id" in self.available_fields
            or "customers" in self.available_fields
            or "returning_customers" in self.available_fields
            or "new_customers" in self.available_fields
        ):
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

        # Cross-category KPI: revenue_per_customer
        unique_custs = 0
        if "customer_id" in self.available_fields:
            cust_s = self.working_df["customer_id"].dropna()
            unique_custs = int(cust_s.nunique())
        elif "customers" in self.available_fields:
            num_s = pd.to_numeric(self.working_df["customers"], errors="coerce").dropna()
            if len(num_s) > 0 and num_s.sum() > 0:
                unique_custs = int(num_s.sum())
            else:
                unique_custs = int(self.working_df["customers"].dropna().nunique())

        if unique_custs > 0 or "customer_id" in self.available_fields or "customers" in self.available_fields:
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
        total_orders = 0

        if "order_id" in self.available_fields:
            orders_series = self.working_df["order_id"].dropna()
            total_orders = int(orders_series.nunique())
        elif "orders" in self.available_fields:
            num_orders = pd.to_numeric(self.working_df["orders"], errors="coerce").dropna()
            if len(num_orders) > 0:
                total_orders = int(num_orders.sum())
            else:
                total_orders = int(self.working_df["orders"].dropna().nunique())

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
        elif "cancellations" in self.available_fields or "cancellation_rate" in self.available_fields:
            if "cancellations" in self.available_fields:
                cxl_s = pd.to_numeric(self.working_df["cancellations"], errors="coerce").dropna()
                cancelled_orders = int(cxl_s.sum()) if len(cxl_s) > 0 else 0
                completed_orders = max(0, total_orders - cancelled_orders)
                completion_rate = round((completed_orders / total_orders * 100.0), 2) if total_orders > 0 else 0.0
            else:
                cxl_s = pd.to_numeric(self.working_df["cancellation_rate"], errors="coerce").dropna()
                if len(cxl_s) > 0:
                    mean_cxl = float(cxl_s.mean())
                    cxl_pct = mean_cxl * 100.0 if mean_cxl <= 1.0 else mean_cxl
                    cancelled_orders = int(round(total_orders * (cxl_pct / 100.0)))
                    completed_orders = max(0, total_orders - cancelled_orders)
                    completion_rate = round(max(0.0, min(100.0, 100.0 - cxl_pct)), 2)
                else:
                    cancelled_orders = 0
                    completed_orders = total_orders
                    completion_rate = 100.0

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
        """Calculates customer volume and retention metrics."""
        metrics: List[CalculatedMetric] = []
        unique_customers = 0

        if "customer_id" in self.available_fields:
            cust_series = self.working_df["customer_id"].dropna()
            unique_customers = int(cust_series.nunique())
        elif "customers" in self.available_fields:
            num_s = pd.to_numeric(self.working_df["customers"], errors="coerce").dropna()
            if len(num_s) > 0:
                unique_customers = int(num_s.sum())
            else:
                unique_customers = int(self.working_df["customers"].dropna().nunique())

        metrics.append(
            CalculatedMetric(
                metric_key="unique_customers",
                metric_name="Unique Customers",
                metric_category=MetricCategory.CUSTOMERS,
                metric_value=unique_customers,
            )
        )

        if "returning_customers" in self.available_fields:
            ret_s = pd.to_numeric(self.working_df["returning_customers"], errors="coerce").dropna()
            ret_count = int(ret_s.sum()) if len(ret_s) > 0 else int(self.working_df["returning_customers"].dropna().nunique())
            metrics.append(
                CalculatedMetric(
                    metric_key="returning_customers",
                    metric_name="Returning Customers",
                    metric_category=MetricCategory.CUSTOMERS,
                    metric_value=ret_count,
                )
            )
            if unique_customers > 0:
                rep_rate = round((ret_count / unique_customers) * 100.0, 2)
                metrics.append(
                    CalculatedMetric(
                        metric_key="repeat_customer_rate",
                        metric_name="Repeat Customer Rate (%)",
                        metric_category=MetricCategory.CUSTOMERS,
                        metric_value=rep_rate,
                    )
                )

        if "new_customers" in self.available_fields:
            new_s = pd.to_numeric(self.working_df["new_customers"], errors="coerce").dropna()
            new_count = int(new_s.sum()) if len(new_s) > 0 else int(self.working_df["new_customers"].dropna().nunique())
            metrics.append(
                CalculatedMetric(
                    metric_key="new_customers",
                    metric_name="New Customers",
                    metric_category=MetricCategory.CUSTOMERS,
                    metric_value=new_count,
                )
            )

        return metrics

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

