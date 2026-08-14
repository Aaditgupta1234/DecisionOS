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
