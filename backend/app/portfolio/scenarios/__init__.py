"""Scenarios package for Phase 11.4: Executive Scenario Modeling & Strategic Planning Intelligence."""

from app.portfolio.scenarios.constants import (
    IMPACT_CRITICAL_HEALTH_DELTA,
    IMPACT_CRITICAL_RISK_DELTA_PCT,
    IMPACT_HIGH_HEALTH_DELTA,
    IMPACT_HIGH_RISK_DELTA_PCT,
    IMPACT_MODERATE_HEALTH_DELTA,
    IMPACT_MODERATE_RISK_DELTA_PCT,
    SCENARIO_ENGINE_VERSION,
    SCENARIO_SCHEMA_VERSION,
    ScenarioImpactLevel,
    ScenarioResultStatus,
    ScenarioType,
)

__all__ = [
    "SCENARIO_ENGINE_VERSION",
    "SCENARIO_SCHEMA_VERSION",
    "ScenarioType",
    "ScenarioImpactLevel",
    "ScenarioResultStatus",
    "IMPACT_CRITICAL_HEALTH_DELTA",
    "IMPACT_HIGH_HEALTH_DELTA",
    "IMPACT_MODERATE_HEALTH_DELTA",
    "IMPACT_CRITICAL_RISK_DELTA_PCT",
    "IMPACT_HIGH_RISK_DELTA_PCT",
    "IMPACT_MODERATE_RISK_DELTA_PCT",
]
