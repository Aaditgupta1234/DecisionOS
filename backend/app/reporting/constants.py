"""Constants, Enums, and Configuration Tokens for Phase 9.5 Reporting Engine."""

from enum import Enum


class ReportType(str, Enum):
    """Supported report categories for DecisionOS."""
    EXECUTIVE_SUMMARY = "EXECUTIVE_SUMMARY"
    KPI_PERFORMANCE = "KPI_PERFORMANCE"
    DIAGNOSTIC = "DIAGNOSTIC"
    ROOT_CAUSE = "ROOT_CAUSE"
    RECOMMENDATION_ROADMAP = "RECOMMENDATION_ROADMAP"
    FORECAST = "FORECAST"
    SCENARIO_PLANNING = "SCENARIO_PLANNING"
    EXECUTIVE_INTELLIGENCE = "EXECUTIVE_INTELLIGENCE"
    FULL_BOARD_PACKAGE = "FULL_BOARD_PACKAGE"


class ExportFormat(str, Enum):
    """Supported export output formats."""
    PDF = "PDF"
    HTML = "HTML"


class ReportStatus(str, Enum):
    """Lifecycle status for a generated report export."""
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


REPORT_TEMPLATE_VERSION = "1.0"
REPORT_SCHEMA_VERSION = "1.0"
DEFAULT_STORAGE_DIR = "storage/reports"

# Document & Branding Styling Constants
PRIMARY_COLOR_HEX = "#0F172A"      # Slate 900
SECONDARY_COLOR_HEX = "#3B82F6"    # Blue 500
ACCENT_COLOR_HEX = "#10B981"       # Emerald 500
WARNING_COLOR_HEX = "#F59E0B"      # Amber 500
DANGER_COLOR_HEX = "#EF4444"       # Rose 500
TEXT_COLOR_HEX = "#1E293B"         # Slate 800
MUTED_COLOR_HEX = "#64748B"        # Slate 500
BG_LIGHT_HEX = "#F8FAFC"           # Slate 50
BORDER_COLOR_HEX = "#E2E8F0"       # Slate 200

# Report Titles
REPORT_TITLES = {
    ReportType.EXECUTIVE_SUMMARY: "Executive Summary Briefing",
    ReportType.KPI_PERFORMANCE: "KPI & Operational Performance Report",
    ReportType.DIAGNOSTIC: "Comprehensive Diagnostic Anomaly Report",
    ReportType.ROOT_CAUSE: "Root Cause & Causal Attribution Report",
    ReportType.RECOMMENDATION_ROADMAP: "Strategic Recommendation Roadmap",
    ReportType.FORECAST: "Predictive Forecast & Horizon Outlook",
    ReportType.SCENARIO_PLANNING: "Scenario Simulation & Sensitivity Analysis",
    ReportType.EXECUTIVE_INTELLIGENCE: "Executive Intelligence & Risk Report",
    ReportType.FULL_BOARD_PACKAGE: "Executive Boardroom Intelligence Package",
}
