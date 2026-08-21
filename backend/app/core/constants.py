"""System constants and enumerations."""

from enum import Enum
from typing import Dict, List


class UserRole(str, Enum):
    ADMIN = "admin"
    ANALYST = "analyst"
    EXECUTIVE = "executive"
    VIEWER = "viewer"


class OrgRole(str, Enum):
    """Organization-scoped RBAC roles for multi-tenant tenancy."""
    OWNER = "OWNER"
    ADMIN = "ADMIN"
    ANALYST = "ANALYST"
    VIEWER = "VIEWER"


class ChatMessageRole(str, Enum):
    """Roles for conversational AI chat messages."""
    USER = "USER"
    ASSISTANT = "ASSISTANT"


class StrategyPlanStatus(str, Enum):
    """Lifecycle states for strategic execution plans."""
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    ARCHIVED = "ARCHIVED"


class TimeHorizon(str, Enum):
    """Execution time horizons for strategic roadmap milestones and actions."""
    IMMEDIATE = "IMMEDIATE"      # Days 1 - 7
    DAYS_30 = "30_DAYS"          # Days 8 - 30
    DAYS_60 = "60_DAYS"          # Days 31 - 60
    DAYS_90 = "90_DAYS"          # Days 61 - 90


class TargetDirection(str, Enum):
    """Target KPI trajectory direction for strategy success criteria."""
    IMPROVE = "IMPROVE"
    INCREASE = "INCREASE"
    DECREASE = "DECREASE"
    STABILIZE = "STABILIZE"
    MAINTAIN = "MAINTAIN"


class ScenarioStatus(str, Enum):
    """Lifecycle states for scenario simulations."""
    DRAFT = "DRAFT"
    COMPLETED = "COMPLETED"
    ARCHIVED = "ARCHIVED"


class ScenarioAdjustmentType(str, Enum):
    """Supported mathematical adjustment types for scenario assumptions."""
    RELATIVE_PERCENT = "RELATIVE_PERCENT"        # projected = baseline * (1 + val / 100)
    PERCENTAGE_POINTS = "PERCENTAGE_POINTS"      # projected = baseline + val (e.g. 20% - 5pts = 15%)
    ABSOLUTE_VALUE = "ABSOLUTE_VALUE"            # projected = baseline + val


class ForecastHorizon(str, Enum):
    """Supported forecast horizons for time-series projections."""
    HORIZON_30_DAYS = "30_DAYS"
    HORIZON_90_DAYS = "90_DAYS"
    HORIZON_180_DAYS = "180_DAYS"
    HORIZON_365_DAYS = "365_DAYS"


class ForecastFrequency(str, Enum):
    """Supported temporal observation frequencies."""
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"


class ForecastStatus(str, Enum):
    """Lifecycle states for analytical forecasts."""
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    ARCHIVED = "ARCHIVED"


class ForecastTrend(str, Enum):
    """Directional trend classification for forecasted trajectories."""
    INCREASING = "INCREASING"
    DECREASING = "DECREASING"
    STABLE = "STABLE"
    VOLATILE = "VOLATILE"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"


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


class RecommendationType(str, Enum):
    """Business recommendation domain taxonomy."""
    REVENUE_GROWTH = "REVENUE_GROWTH"
    CUSTOMER_RETENTION = "CUSTOMER_RETENTION"
    CUSTOMER_ACQUISITION = "CUSTOMER_ACQUISITION"
    PRODUCT_OPTIMIZATION = "PRODUCT_OPTIMIZATION"
    PRICING_STRATEGY = "PRICING_STRATEGY"
    PROCESS_IMPROVEMENT = "PROCESS_IMPROVEMENT"
    OPERATIONAL_EFFICIENCY = "OPERATIONAL_EFFICIENCY"
    COST_OPTIMIZATION = "COST_OPTIMIZATION"
    RISK_MITIGATION = "RISK_MITIGATION"


class RecommendationPriority(str, Enum):
    """Priority tier for recommendation execution."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ExpectedTimeToValue(str, Enum):
    """Estimated implementation timeframe for business returns."""
    IMMEDIATE = "IMMEDIATE"      # 1-7 days (quick win)
    SHORT_TERM = "SHORT_TERM"    # 1-4 weeks
    MEDIUM_TERM = "MEDIUM_TERM"  # 1-3 months
    LONG_TERM = "LONG_TERM"      # 3+ months (strategic)


class RecommendationStatus(str, Enum):
    """Lifecycle tracking states for business recommendations."""
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    IMPLEMENTED = "IMPLEMENTED"
    ARCHIVED = "ARCHIVED"


class RecommendationSource(str, Enum):
    """Origin source of the recommendation."""
    RULE_ENGINE = "RULE_ENGINE"
    AI_INSIGHT = "AI_INSIGHT"
    USER_CUSTOM = "USER_CUSTOM"
    HYBRID = "HYBRID"


class BusinessHealthStatus(str, Enum):
    """Categorical business health classification based on comprehensive diagnostic health score."""
    EXCELLENT = "EXCELLENT"      # 90 - 100
    HEALTHY = "HEALTHY"          # 75 - 89
    WATCH_LIST = "WATCH_LIST"    # 60 - 74
    AT_RISK = "AT_RISK"          # 40 - 59
    CRITICAL = "CRITICAL"        # 0 - 39


class ReportExportFormat(str, Enum):
    """Supported export formats for business intelligence reports."""
    PDF = "PDF"
    PPTX = "PPTX"
    JSON = "JSON"
    HTML = "HTML"


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
        "customer_id", "customerid", "client_id", "clientid",
        "buyer_id", "user_id", "customer_identifier", "cust_id", "account_id"
    ],
    "customers": [
        "customers", "customer_count", "total_customers", "active_customers",
        "num_customers", "unique_customers", "client_count"
    ],
    "returning_customers": [
        "returning_customers", "repeat_customers", "returning_customer_count",
        "repeat_customer_count", "retained_customers"
    ],
    "new_customers": [
        "new_customers", "new_customer_count", "acquired_customers", "first_time_customers"
    ],
    "order_id": [
        "order_id", "orderid", "transaction_id", "transactionid", "invoice_id",
        "invoice_no", "order_number", "order_no", "purchase_id"
    ],
    "orders": [
        "orders", "order_count", "total_orders", "num_orders", "transaction_count"
    ],
    "order_date": [
        "order_date", "orderdate", "transaction_date", "purchase_date", "date",
        "created_at", "timestamp", "sale_date", "order_time", "month", "period", "day"
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
        "delivery_time", "delivery_time_days", "delivery_days", "shipping_time",
        "lead_time", "fulfillment_time", "transit_time"
    ],
    "product_category": [
        "product_category", "category", "product_type", "item_category",
        "department", "genre", "product_group", "business_segment", "segment"
    ],
    "cancellation_rate": [
        "cancellation_rate", "cancel_rate", "cancellation_percentage", "order_cancellation_rate"
    ],
    "churn_rate": [
        "churn_rate", "customer_churn_rate", "attrition_rate"
    ],
    "region": [
        "region", "territory", "geography", "zone", "market_region", "location"
    ],
}

