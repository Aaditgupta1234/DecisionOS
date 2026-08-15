"""Constants, thresholds, and versioning for Phase 9.2 AI Narrative Engine."""

# Prompt & Report Versioning
NARRATIVE_PROMPT_VERSION = "1.0"
NARRATIVE_SCHEMA_VERSION = "1.0"

# Generation Defaults
DEFAULT_TEMPERATURE = 0.2
DEFAULT_MAX_TOKENS = 2500

# Word Count Boundaries for Output Validation
EXECUTIVE_SUMMARY_MIN_WORDS = 50
EXECUTIVE_SUMMARY_MAX_WORDS = 400

SECTION_NARRATIVE_MIN_WORDS = 25
SECTION_NARRATIVE_MAX_WORDS = 250

# Narrative Types
NARRATIVE_TYPE_EXECUTIVE = "executive_summary"
NARRATIVE_TYPE_KPI = "kpi"
NARRATIVE_TYPE_ROOT_CAUSE = "root_cause"
NARRATIVE_TYPE_RECOMMENDATION = "recommendation"
NARRATIVE_TYPE_FORECAST = "forecast"
NARRATIVE_TYPE_SCENARIO = "scenario"
NARRATIVE_TYPE_FULL_PACKAGE = "full_package"

# Hallucination and Speculation Flags to check in output validation
HALLUCINATION_TRIGGERS = [
    "i assume",
    "we assume",
    "probably due to",
    "likely because",
    "might indicate",
    "possibly due to",
    "hypothetically",
    "outside the dataset",
    "not in the data",
    "i believe",
    "we hypothesize",
]
