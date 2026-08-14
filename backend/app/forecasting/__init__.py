"""DecisionOS Phase 6.4 Forecasting Engine Package."""

from app.forecasting.constants import (
    DEFAULT_CONFIDENCE_LEVEL,
    DEFAULT_FORECAST_LIMITATIONS,
    DEFAULT_FORECAST_VERSION,
    HORIZON_STEPS_MAP,
    METRIC_AGGREGATION_MAP,
    METRIC_PHYSICAL_BOUNDS,
    MIN_OBSERVATIONS_MAP,
    SUPPORTED_FORECAST_METRICS,
    get_forecast_steps,
)
from app.forecasting.engines import (
    ForecastEngine,
    ForecastEvaluationEngine,
)
from app.forecasting.models import (
    BaseForecastModel,
    MovingAverageForecastModel,
    NaiveForecastModel,
)
from app.forecasting.preparation import (
    InsufficientObservationsError,
    PreparedTimeSeries,
    TimeSeriesPreparationError,
    TimeSeriesPreparer,
)
from app.forecasting.repositories import ForecastRepository
from app.forecasting.schemas import (
    ForecastComparisonItem,
    ForecastComparisonResponse,
    ForecastHistoryResponse,
    ForecastPoint,
    ForecastRequest,
    ForecastResponse,
    ModelMetrics,
)
from app.forecasting.services import ForecastingService
from app.forecasting.validators import (
    ForecastValidationError,
    ForecastValidator,
)

__all__ = [
    "ForecastRequest",
    "ForecastPoint",
    "ModelMetrics",
    "ForecastResponse",
    "ForecastHistoryResponse",
    "ForecastComparisonItem",
    "ForecastComparisonResponse",
    "TimeSeriesPreparer",
    "PreparedTimeSeries",
    "TimeSeriesPreparationError",
    "InsufficientObservationsError",
    "BaseForecastModel",
    "NaiveForecastModel",
    "MovingAverageForecastModel",
    "ForecastEvaluationEngine",
    "ForecastEngine",
    "ForecastValidator",
    "ForecastValidationError",
    "ForecastRepository",
    "ForecastingService",
    "get_forecast_steps",
    "DEFAULT_FORECAST_VERSION",
    "DEFAULT_CONFIDENCE_LEVEL",
    "MIN_OBSERVATIONS_MAP",
    "HORIZON_STEPS_MAP",
    "METRIC_AGGREGATION_MAP",
    "METRIC_PHYSICAL_BOUNDS",
    "SUPPORTED_FORECAST_METRICS",
    "DEFAULT_FORECAST_LIMITATIONS",
]
