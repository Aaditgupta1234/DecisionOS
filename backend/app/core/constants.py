"""System constants and enumerations."""

from enum import Enum


class UserRole(str, Enum):
    ADMIN = "admin"
    ANALYST = "analyst"
    EXECUTIVE = "executive"
    VIEWER = "viewer"


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
