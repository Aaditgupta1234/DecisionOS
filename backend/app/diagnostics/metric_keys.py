"""Central registry of canonical metric keys used across Diagnostic Analyzers and KPI Engine."""


class MetricKeys:
    """Standardized KPI metric key constants to eliminate magic string literals."""

    # 1. Revenue Metrics
    TOTAL_REVENUE = "total_revenue"
    AVERAGE_REVENUE = "average_revenue"
    MAXIMUM_REVENUE = "maximum_revenue"
    MINIMUM_REVENUE = "minimum_revenue"
    REVENUE_PER_CUSTOMER = "revenue_per_customer"

    # 2. Customer Metrics
    UNIQUE_CUSTOMERS = "unique_customers"
    CHURN_RATE = "churn_rate"
    RETENTION_RATE = "retention_rate"
    REPEAT_CUSTOMER_RATE = "repeat_customer_rate"
    NEW_CUSTOMERS = "new_customers"
    CUSTOMER_LTV = "customer_ltv"

    # 3. Order & Operational Metrics
    TOTAL_ORDERS = "total_orders"
    COMPLETED_ORDERS = "completed_orders"
    CANCELLED_ORDERS = "cancelled_orders"
    COMPLETION_RATE = "completion_rate"
    CANCELLATION_RATE = "cancellation_rate"
    AVERAGE_DELIVERY_TIME = "average_delivery_time"
    AVERAGE_REVIEW_SCORE = "average_review_score"
    TOTAL_COST = "total_cost"
    AVERAGE_COST = "average_cost"
    GROSS_MARGIN = "gross_margin"

    # 4. Product Metrics
    PRODUCT_REVENUE_SHARE = "product_revenue_share"
    PRODUCT_CATEGORY = "product_category"
    PRODUCT_NAME = "product_name"
    PRODUCT_CONCENTRATION_RATIO = "product_concentration_ratio"

    # 5. Quality Metrics
    RECORD_COUNT = "record_count"
    COLUMN_COUNT = "column_count"
    COMPLETENESS_PERCENTAGE = "completeness_percentage"
