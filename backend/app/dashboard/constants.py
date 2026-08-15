"""
Constants and Enums for Phase 9.6 Executive Dashboard & Intelligence Workspace.
"""

from enum import Enum
from typing import Dict, Any

API_VERSION: str = "v1"
WORKSPACE_VERSION: str = "1.0"
SNAPSHOT_VERSION: str = "1.0"
HASH_SCHEMA_VERSION: str = "1.0"
QUESTION_GENERATION_VERSION: str = "1.0"

CACHE_TTL_SECONDS: int = 60
MAX_SNAPSHOT_AGE_MINUTES: int = 15
MIN_REFRESH_INTERVAL_SECONDS: int = 30
MAX_SNAPSHOTS_PER_DATASET: int = 25
TELEMETRY_RETENTION_DAYS: int = 90
SNAPSHOT_BUILD_TIMEOUT_SECONDS: int = 60

DEFAULT_FORECAST_ENGINE: str = "Prophet"
DEFAULT_FORECAST_VERSION: str = "1.1.5"


class QuestionCategory(str, Enum):
    FORECAST = "FORECAST"
    ROOT_CAUSE = "ROOT_CAUSE"
    RECOMMENDATION = "RECOMMENDATION"
    HEALTH_SCORE = "HEALTH_SCORE"
    GENERAL = "GENERAL"


class SnapshotStatus(str, Enum):
    PENDING = "PENDING"
    BUILDING = "BUILDING"
    READY = "READY"
    FAILED = "FAILED"


class SnapshotTrigger(str, Enum):
    MANUAL = "MANUAL"
    AUTOMATIC = "AUTOMATIC"
    DATASET_UPDATED = "DATASET_UPDATED"
    REPORT_GENERATED = "REPORT_GENERATED"
    INSIGHTS_UPDATED = "INSIGHTS_UPDATED"
    FORECAST_UPDATED = "FORECAST_UPDATED"


HEALTH_STATUS_COLORS: Dict[str, str] = {
    "OPTIMAL": "#10B981",     # Emerald
    "HEALTHY": "#34D399",     # Green
    "WATCH_LIST": "#FBBF24",   # Amber
    "AT_RISK": "#F97316",      # Orange
    "CRITICAL": "#EF4444",     # Red
}

AVAILABLE_SECTIONS_DEFAULT: Dict[str, bool] = {
    "overview": True,
    "kpis": True,
    "findings": True,
    "root_causes": True,
    "recommendations": True,
    "forecasts": True,
    "scenarios": True,
    "narratives": True,
    "insights": True,
    "reports": True,
    "chat": True,
}
