"""CLI Seed script to populate standard business MetricDefinition templates."""

from typing import Dict, List
from app.core.constants import MetricCategory
from app.core.logging import logger
from app.database.session import SessionLocal
from app.models.metric_definition import MetricDefinition

DEFAULT_METRIC_DEFINITIONS: List[Dict[str, any]] = [
    # 1. Revenue Metrics
    {
        "metric_key": "total_revenue",
        "name": "Total Revenue",
        "metric_category": MetricCategory.REVENUE,
        "required_field": "revenue",
        "formula": "df['revenue'].sum()",
        "description": "Sum of all monetary transaction values in the dataset.",
    },
    {
        "metric_key": "average_revenue",
        "name": "Average Revenue",
        "metric_category": MetricCategory.REVENUE,
        "required_field": "revenue",
        "formula": "df['revenue'].mean()",
        "description": "Mean revenue per transaction.",
    },
    {
        "metric_key": "maximum_revenue",
        "name": "Maximum Revenue",
        "metric_category": MetricCategory.REVENUE,
        "required_field": "revenue",
        "formula": "df['revenue'].max()",
        "description": "Highest single transaction revenue amount.",
    },
    {
        "metric_key": "minimum_revenue",
        "name": "Minimum Revenue",
        "metric_category": MetricCategory.REVENUE,
        "required_field": "revenue",
        "formula": "df['revenue'].min()",
        "description": "Lowest single transaction revenue amount.",
    },
    {
        "metric_key": "revenue_per_customer",
        "name": "Revenue Per Customer",
        "metric_category": MetricCategory.REVENUE,
        "required_field": "revenue",
        "formula": "total_revenue / unique_customers",
        "description": "Average revenue generated per unique customer account.",
    },
    # 2. Order Metrics
    {
        "metric_key": "total_orders",
        "name": "Total Orders",
        "metric_category": MetricCategory.ORDERS,
        "required_field": "order_id",
        "formula": "df['order_id'].nunique()",
        "description": "Total count of unique orders.",
    },
    {
        "metric_key": "completed_orders",
        "name": "Completed Orders",
        "metric_category": MetricCategory.ORDERS,
        "required_field": "order_id",
        "formula": "status in completed_aliases count",
        "description": "Total successfully fulfilled orders.",
    },
    {
        "metric_key": "cancelled_orders",
        "name": "Cancelled Orders",
        "metric_category": MetricCategory.ORDERS,
        "required_field": "order_id",
        "formula": "status in cancelled_aliases count",
        "description": "Total cancelled or returned orders.",
    },
    {
        "metric_key": "completion_rate",
        "name": "Completion Rate (%)",
        "metric_category": MetricCategory.ORDERS,
        "required_field": "order_id",
        "formula": "completed / total * 100",
        "description": "Percentage of orders successfully completed and delivered.",
    },
    # 3. Customer Metrics
    {
        "metric_key": "unique_customers",
        "name": "Unique Customers",
        "metric_category": MetricCategory.CUSTOMERS,
        "required_field": "customer_id",
        "formula": "df['customer_id'].nunique()",
        "description": "Total unique customer accounts in dataset.",
    },
    # 4. Review Metrics
    {
        "metric_key": "average_review_score",
        "name": "Average Review Score",
        "metric_category": MetricCategory.REVIEWS,
        "required_field": "review_score",
        "formula": "df['review_score'].mean()",
        "description": "Average customer feedback rating.",
    },
    # 5. Delivery Metrics
    {
        "metric_key": "average_delivery_time",
        "name": "Avg Delivery Time",
        "metric_category": MetricCategory.DELIVERY,
        "required_field": "delivery_time",
        "formula": "df['delivery_time'].mean()",
        "description": "Average order shipping and delivery duration.",
    },
    # 6. Quality Metrics
    {
        "metric_key": "record_count",
        "name": "Total Records",
        "metric_category": MetricCategory.QUALITY,
        "required_field": "*",
        "formula": "len(df)",
        "description": "Total data records in dataset.",
    },
    {
        "metric_key": "column_count",
        "name": "Total Columns",
        "metric_category": MetricCategory.QUALITY,
        "required_field": "*",
        "formula": "len(df.columns)",
        "description": "Total schema columns in dataset.",
    },
    {
        "metric_key": "completeness_percentage",
        "name": "Data Completeness (%)",
        "metric_category": MetricCategory.QUALITY,
        "required_field": "*",
        "formula": "(1 - null_cells / total_cells) * 100",
        "description": "Overall non-null data completeness percentage.",
    },
]


def seed_metric_definitions():
    """Seeds default standard metric definitions into the database."""
    db = SessionLocal()
    try:
        created_count = 0
        updated_count = 0

        for item in DEFAULT_METRIC_DEFINITIONS:
            existing = (
                db.query(MetricDefinition)
                .filter(MetricDefinition.metric_key == item["metric_key"])
                .first()
            )

            if existing:
                existing.name = item["name"]
                existing.metric_category = item["metric_category"]
                existing.required_field = item["required_field"]
                existing.formula = item["formula"]
                existing.description = item["description"]
                existing.is_active = True
                updated_count += 1
            else:
                new_def = MetricDefinition(
                    name=item["name"],
                    metric_key=item["metric_key"],
                    metric_category=item["metric_category"],
                    required_field=item["required_field"],
                    formula=item["formula"],
                    description=item["description"],
                    is_active=True,
                )
                db.add(new_def)
                created_count += 1

        db.commit()
        print(f"MetricDefinitions seeded: {created_count} created, {updated_count} updated.")
        logger.info(f"MetricDefinitions seeded: {created_count} created, {updated_count} updated.")
    except Exception as e:
        db.rollback()
        print(f"Failed to seed metric definitions: {e}")
        logger.error(f"Failed to seed metric definitions: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_metric_definitions()
