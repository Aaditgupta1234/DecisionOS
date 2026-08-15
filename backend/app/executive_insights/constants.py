"""Constants and configuration tokens for Phase 9.3: Executive Insight Generator."""

# Versioning
INSIGHT_PROMPT_VERSION: str = "1.0"
INSIGHT_SCHEMA_VERSION: str = "1.0"

# Insight Section Types
INSIGHT_TYPE_RISKS: str = "TOP_RISKS"
INSIGHT_TYPE_OPPORTUNITIES: str = "TOP_OPPORTUNITIES"
INSIGHT_TYPE_ACTIONS: str = "PRIORITY_ACTIONS"
INSIGHT_TYPE_THEMES: str = "STRATEGIC_THEMES"
INSIGHT_TYPE_ALERTS: str = "EXECUTIVE_ALERTS"
INSIGHT_TYPE_BOARD_COMMENTARY: str = "BOARD_COMMENTARY"
INSIGHT_TYPE_FULL_PACKAGE: str = "FULL_PACKAGE"

# Word Count Boundaries
BOARD_COMMENTARY_MIN_WORDS: int = 100
BOARD_COMMENTARY_MAX_WORDS: int = 250

RISK_DESC_MIN_WORDS: int = 20
RISK_DESC_MAX_WORDS: int = 100

OPPORTUNITY_DESC_MIN_WORDS: int = 20
OPPORTUNITY_DESC_MAX_WORDS: int = 100

ACTION_RATIONALE_MIN_WORDS: int = 15
ACTION_RATIONALE_MAX_WORDS: int = 80

# Anti-Hallucination Forbidden Keywords / Speculative Triggers
HALLUCINATION_TRIGGERS: list[str] = [
    "i believe",
    "i think",
    "probably",
    "maybe",
    "likely because",
    "outside the dataset",
    "assume",
    "in my opinion",
    "i suspect",
    "i guess",
    "cannot be verified",
    "unconfirmed by data",
]
