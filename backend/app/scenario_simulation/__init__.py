"""DecisionOS Phase 6.3 Scenario Simulation Engine Package."""

from app.scenario_simulation.constants import (
    ALLOWED_ADJUSTMENT_TYPES,
    DEFAULT_SCENARIO_LIMIT,
    DEFAULT_SCENARIO_LIMITATIONS,
    DEFAULT_SCENARIO_VERSION,
    METRIC_BOUNDARIES,
    SUPPORTED_SIMULATION_METRICS,
)
from app.scenario_simulation.engines import (
    HealthProjectionEngine,
    MetricBoundaryError,
    MetricProjectionEngine,
    ScenarioComparisonEngine,
    ScenarioRule,
    ScenarioRuleRegistry,
)
from app.scenario_simulation.repositories import ScenarioRepository
from app.scenario_simulation.schemas import (
    ScenarioAssumption,
    ScenarioComparisonItem,
    ScenarioComparisonResponse,
    ScenarioCreate,
    ScenarioHealthProjection,
    ScenarioHistoryResponse,
    ScenarioMetricProjection,
    ScenarioResponse,
)
from app.scenario_simulation.services import ScenarioSimulationService
from app.scenario_simulation.validators import (
    ScenarioValidationError,
    ScenarioValidator,
)

__all__ = [
    "ScenarioAssumption",
    "ScenarioCreate",
    "ScenarioMetricProjection",
    "ScenarioHealthProjection",
    "ScenarioResponse",
    "ScenarioHistoryResponse",
    "ScenarioComparisonItem",
    "ScenarioComparisonResponse",
    "ScenarioValidator",
    "ScenarioValidationError",
    "MetricProjectionEngine",
    "MetricBoundaryError",
    "ScenarioRuleRegistry",
    "ScenarioRule",
    "HealthProjectionEngine",
    "ScenarioComparisonEngine",
    "ScenarioRepository",
    "ScenarioSimulationService",
    "SUPPORTED_SIMULATION_METRICS",
    "ALLOWED_ADJUSTMENT_TYPES",
    "METRIC_BOUNDARIES",
    "DEFAULT_SCENARIO_VERSION",
    "DEFAULT_SCENARIO_LIMIT",
    "DEFAULT_SCENARIO_LIMITATIONS",
]
