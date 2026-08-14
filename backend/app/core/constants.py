"""System constants and enumerations."""

from enum import Enum
from typing import Dict, List


class UserRole(str, Enum):
    ADMIN = "admin"
    ANALYST = "analyst"
    EXECUTIVE = "executive"
    VIEWER = "viewer"


class DatasetStatus(str, Enum):
    """Lifecycle states for dataset uploads and processing."""
    UPLOADED = "UPLOADED"
    PROCESSING = "PROCESSING"
    READY = "READY"
    FAILED = "FAILED"


class MetricsGenerationStatus(str, Enum):
    """Lifecycle states for dataset KPI calculation."""
    PENDING = "PENDING"
    GENERATED = "GENERATED"
    FAILED = "FAILED"


class DiagnosticGenerationStatus(str, Enum):
    """Lifecycle states for dataset root cause diagnostics."""
    PENDING = "PENDING"
    GENERATED = "GENERATED"
    FAILED = "FAILED"


class FindingSeverity(str, Enum):
    """Severity classification for diagnostic findings."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class FindingCategory(str, Enum):
    """Core business diagnostic categories for Phase 5.5."""
    REVENUE = "REVENUE"
    CUSTOMER = "CUSTOMER"
    OPERATIONAL = "OPERATIONAL"
    PRODUCT = "PRODUCT"


class FindingSubtype(str, Enum):
    """Fine-grained diagnostic anomaly and opportunity subtypes."""
    # Revenue Subtypes
    DECLINE = "DECLINE"
    STAGNATION = "STAGNATION"
    GROWTH_ACCELERATION = "GROWTH_ACCELERATION"
    VOLATILITY = "VOLATILITY"

    # Customer Subtypes
    CHURN_INCREASE = "CHURN_INCREASE"
    RETENTION_PROBLEM = "RETENTION_PROBLEM"
    CUSTOMER_GROWTH_SLOWDOWN = "CUSTOMER_GROWTH_SLOWDOWN"
    ACQUISITION_ACCELERATION = "ACQUISITION_ACCELERATION"

    # Operational Subtypes
    COST_SPIKE = "COST_SPIKE"
    MARGIN_COMPRESSION = "MARGIN_COMPRESSION"
    OPERATIONAL_INEFFICIENCY = "OPERATIONAL_INEFFICIENCY"
    DELIVERY_DELAY = "DELIVERY_DELAY"
    PRODUCTIVITY_IMPROVEMENT = "PRODUCTIVITY_IMPROVEMENT"

    # Product Subtypes
    UNDERPERFORMING_PRODUCT = "UNDERPERFORMING_PRODUCT"
    UNDERPERFORMING_PRODUCTS = "UNDERPERFORMING_PRODUCTS"
    PRODUCT_CONCENTRATION_RISK = "PRODUCT_CONCENTRATION_RISK"
    RAPID_PRODUCT_GROWTH = "RAPID_PRODUCT_GROWTH"
    PRODUCT_PERFORMANCE_DECLINE = "PRODUCT_PERFORMANCE_DECLINE"


class FindingType(str, Enum):
    """Canonical business diagnostic finding anomaly types."""
    REVENUE_DROP = "REVENUE_DROP"
    REVENUE_CONCENTRATION = "REVENUE_CONCENTRATION"
    HIGH_CANCELLATION_RATE = "HIGH_CANCELLATION_RATE"
    LOW_COMPLETION_RATE = "LOW_COMPLETION_RATE"
    CUSTOMER_CONCENTRATION = "CUSTOMER_CONCENTRATION"
    REVIEW_SCORE_DECLINE = "REVIEW_SCORE_DECLINE"
    DELIVERY_DELAY = "DELIVERY_DELAY"
    DATA_QUALITY_RISK = "DATA_QUALITY_RISK"


class RelationshipType(str, Enum):
    """Causal and correlational relationship classifications between diagnostic findings."""
    CAUSES = "CAUSES"
    CONTRIBUTES_TO = "CONTRIBUTES_TO"
    CORRELATES_WITH = "CORRELATES_WITH"
    AMPLIFIES = "AMPLIFIES"
    DEPENDENT_ON = "DEPENDENT_ON"


class RelationshipStrength(str, Enum):
    """Qualitative strength tier for causal relationships."""
    VERY_WEAK = "VERY_WEAK"
    WEAK = "WEAK"
    MODERATE = "MODERATE"
    STRONG = "STRONG"
    VERY_STRONG = "VERY_STRONG"


class MetricCategory(str, Enum):
    """Standard KPI categories."""
    REVENUE = "revenue"
    ORDERS = "orders"
    CUSTOMERS = "customers"
    REVIEWS = "reviews"
    DELIVERY = "delivery"
    QUALITY = "quality"


class DatasetType(str, Enum):
    FINANCIAL = "financial"
    SALES = "sales"
    OPERATIONS = "operations"
    CUSTOM = "custom"


class SupportedFileType(str, Enum):
    CSV = "csv"
    XLSX = "xlsx"
    JSON = "json"
    PARQUET = "parquet"


# File upload boundaries
MAX_UPLOAD_SIZE_BYTES = 50 * 1024 * 1024  # 50MB

# Standard business canonical fields and synonyms for automated schema mapping
STANDARD_BUSINESS_FIELDS: Dict[str, List[str]] = {
    "customer_id": [
        "customer_id", "customerid", "customer", "client_id", "clientid",
        "buyer_id", "user_id", "customer_identifier", "cust_id", "account_id"
    ],
    "order_id": [
        "order_id", "orderid", "transaction_id", "transactionid", "invoice_id",
        "invoice_no", "order_number", "order_no", "purchase_id"
    ],
    "order_date": [
        "order_date", "orderdate", "transaction_date", "purchase_date", "date",
        "created_at", "timestamp", "sale_date", "order_time"
    ],
    "revenue": [
        "revenue", "revenue_amount", "sales", "sales_amount", "amount",
        "total_amount", "total_price", "price", "gmv", "turnover", "net_sales"
    ],
    "status": [
        "status", "order_status", "fulfillment_status", "state", "payment_status",
        "delivery_status"
    ],
    "review_score": [
        "review_score", "rating", "score", "customer_satisfaction", "csat",
        "nps", "review_rating", "feedback_score"
    ],
    "delivery_time": [
        "delivery_time", "delivery_days", "shipping_time", "lead_time",
        "fulfillment_time", "transit_time"
    ],
    "product_category": [
        "product_category", "category", "product_type", "item_category",
        "department", "genre", "product_group"
    ],
}
