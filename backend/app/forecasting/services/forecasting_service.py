"""ForecastingService orchestrating time-series extraction, validation, forecasting, and persistence."""

import logging
import os
from typing import Any, Dict, List, Optional, Set, Union
from uuid import UUID
from fastapi import HTTPException, status
import pandas as pd
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.core.constants import ForecastStatus
from app.models.dataset import Dataset
from app.models.dataset_metric import DatasetMetric
from app.models.forecast import Forecast
from app.forecasting.constants import DEFAULT_FORECAST_VERSION
from app.forecasting.engines.forecast_engine import ForecastEngine
from app.forecasting.preparation.time_series_preparer import (
    InsufficientObservationsError,
    TimeSeriesPreparationError,
    TimeSeriesPreparer,
)
from app.forecasting.repositories.forecast_repository import ForecastRepository
from app.forecasting.schemas.forecast_schema import (
    ForecastComparisonItem,
    ForecastComparisonResponse,
    ForecastHistoryResponse,
    ForecastPoint,
    ForecastRequest,
    ForecastResponse,
    ModelMetrics,
)
from app.forecasting.validators.forecast_validator import (
    ForecastValidationError,
    ForecastValidator,
)

logger = logging.getLogger(__name__)


class ForecastingService:
    """
    Service layer executing deterministic time-series forecasting,
    enforcing dataset isolation, and preserving immutability of production intelligence.
    """

    def __init__(self, db: Union[AsyncSession, Session]):
        self.db = db
        self.repo = ForecastRepository(db)

    def _is_async(self) -> bool:
        return isinstance(self.db, AsyncSession)

    async def _validate_dataset_exists(self, dataset_id: UUID) -> Dataset:
        """Ensures the dataset exists and is active."""
        stmt = select(Dataset).where(Dataset.id == dataset_id, Dataset.is_deleted == False)
        if self._is_async():
            res = await self.db.execute(stmt)
        else:
            res = self.db.execute(stmt)
        dataset = res.scalar_one_or_none()
        if not dataset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Dataset '{dataset_id}' not found",
            )
        return dataset

    def _map_to_response(self, forecast: Forecast) -> ForecastResponse:
        """Maps ORM model to Pydantic ForecastResponse."""
        points = [ForecastPoint(**p) for p in forecast.forecast_points]
        metrics = ModelMetrics(**forecast.model_metrics)

        return ForecastResponse(
            id=forecast.id,
            dataset_id=forecast.dataset_id,
            forecast_version=forecast.forecast_version,
            metric_key=forecast.metric_key,
            horizon=forecast.horizon,
            frequency=forecast.frequency,
            model_name=forecast.model_name,
            model_version=forecast.model_version,
            confidence_level=forecast.confidence_level,
            status=forecast.status,
            historical_observation_count=forecast.historical_observation_count,
            forecast_points=points,
            model_metrics=metrics,
            trend=forecast.trend,
            limitations=forecast.limitations,
            baseline_snapshot=forecast.baseline_snapshot,
            metadata_info=forecast.metadata_info,
            created_at=forecast.created_at,
            updated_at=forecast.updated_at,
        )

    # -----------------------------------------------------------------------
    # Forecast Generation Pipeline
    # -----------------------------------------------------------------------

    async def generate_forecast(
        self,
        dataset_id: UUID,
        request: ForecastRequest,
    ) -> ForecastResponse:
        """
        Executes deterministic time-series forecasting:
        1. Validates dataset existence.
        2. Retrieves dataset metric keys and validates request.
        3. Loads dataset DataFrame from storage.
        4. Extracts and prepares time series with metric-aware aggregation.
        5. Fits candidate models, backtests without data leakage, and predicts forward.
        6. Enforces physical boundaries and statistical prediction intervals.
        7. Persists Forecast artifact without mutating production intelligence.
        """
        # 1. Validate Dataset
        dataset = await self._validate_dataset_exists(dataset_id)

        # 2. Get available dataset metric keys
        stmt = select(DatasetMetric.metric_key).where(DatasetMetric.dataset_id == dataset_id)
        if self._is_async():
            metric_res = await self.db.execute(stmt)
        else:
            metric_res = self.db.execute(stmt)
        dataset_metric_keys: Set[str] = set(metric_res.scalars().all())

        # Fallback: if metrics table not populated, allow supported metrics if columns exist
        if not dataset_metric_keys:
            dataset_metric_keys = {request.metric_key}

        # Validate request parameters
        try:
            ForecastValidator.validate_request(request, dataset_metric_keys)
        except ForecastValidationError as v_err:
            logger.warning(f"Forecast request rejected: {v_err}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(v_err),
            )

        # 3. Load DataFrame from storage
        if not dataset.file_path or not os.path.exists(dataset.file_path):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Dataset CSV file not found on disk at '{dataset.file_path}'. Cannot extract time series.",
            )

        try:
            df = pd.read_csv(dataset.file_path)
        except Exception as e:
            logger.error(f"Error reading dataset CSV for forecast: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to load dataset file: {str(e)}",
            )

        # 4. Prepare Time Series
        mapped_fields: Dict[str, str] = {
            col.original_name: col.mapped_field
            for col in (dataset.columns or [])
            if col.mapped_field
        }

        try:
            time_series = TimeSeriesPreparer.prepare_from_dataframe(
                df=df,
                mapped_fields=mapped_fields,
                metric_key=request.metric_key,
            )
        except InsufficientObservationsError as io_err:
            logger.warning(f"Insufficient observations for forecast: {io_err}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(io_err),
            )
        except TimeSeriesPreparationError as tp_err:
            logger.warning(f"Time series preparation error: {tp_err}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(tp_err),
            )

        # 5. Execute Numerical Forecasting
        forecast_result = ForecastEngine.generate_forecast(
            time_series=time_series,
            horizon=request.horizon,
            confidence_level=request.confidence_level,
            model_name_override=request.model_name,
        )

        # 6. Validate Generated Points
        forecast_points_dto = [ForecastPoint(**p) for p in forecast_result["forecast_points"]]
        ForecastValidator.validate_forecast_points(forecast_points_dto)

        # 7. Determine Versioning
        latest = await self.repo.get_latest_by_metric(dataset_id, request.metric_key)
        if latest:
            try:
                major_num = int(float(latest.forecast_version))
                next_version = f"{major_num + 1}.0"
            except ValueError:
                next_version = "2.0"
        else:
            next_version = DEFAULT_FORECAST_VERSION

        # 8. Construct Snapshot & Telemetry
        baseline_snapshot = {
            "historical_mean": round(float(pd.Series(time_series.values).mean()), 4),
            "historical_std": round(float(pd.Series(time_series.values).std()), 4),
            "last_observed_value": time_series.values[-1],
            "first_period": time_series.periods[0],
            "last_period": time_series.periods[-1],
            "volatility_cv": time_series.volatility_cv,
            "has_structural_break": time_series.has_structural_break,
        }

        metadata_info = {
            "candidate_evaluations": forecast_result.get("candidate_evaluations", {}),
            "selected_model": forecast_result["model_name"],
            "horizon_steps": len(forecast_points_dto),
        }

        # 9. Instantiate & Persist
        forecast = Forecast(
            dataset_id=dataset_id,
            forecast_version=next_version,
            metric_key=request.metric_key,
            horizon=request.horizon.value if hasattr(request.horizon, "value") else str(request.horizon),
            frequency=time_series.frequency.value if hasattr(time_series.frequency, "value") else str(time_series.frequency),
            model_name=forecast_result["model_name"],
            model_version=forecast_result["model_version"],
            confidence_level=request.confidence_level,
            status=ForecastStatus.COMPLETED,
            historical_observation_count=time_series.observation_count,
            forecast_points=forecast_result["forecast_points"],
            model_metrics=forecast_result["model_metrics"],
            trend=forecast_result["trend"],
            limitations=forecast_result["limitations"],
            baseline_snapshot=baseline_snapshot,
            metadata_info=metadata_info,
        )

        persisted = await self.repo.create(forecast)

        if self._is_async():
            await self.db.commit()
        else:
            self.db.commit()

        return self._map_to_response(persisted)

    # -----------------------------------------------------------------------
    # Retrieval, History & Comparison
    # -----------------------------------------------------------------------

    async def get_forecast(self, forecast_id: UUID) -> ForecastResponse:
        """Retrieves a specific forecast by ID."""
        forecast = await self.repo.get_by_id(forecast_id)
        if not forecast:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Forecast '{forecast_id}' not found",
            )
        return self._map_to_response(forecast)

    async def list_forecasts(
        self,
        dataset_id: UUID,
        metric_key: Optional[str] = None,
        limit: int = 10,
        offset: int = 0,
    ) -> ForecastHistoryResponse:
        """Lists historical forecasts for a dataset."""
        await self._validate_dataset_exists(dataset_id)
        total_count = await self.repo.count_by_dataset(dataset_id, metric_key=metric_key)
        forecasts = await self.repo.list_history_by_dataset(
            dataset_id=dataset_id,
            metric_key=metric_key,
            limit=limit,
            offset=offset,
        )
        return ForecastHistoryResponse(
            total_count=total_count,
            forecasts=[self._map_to_response(f) for f in forecasts],
        )

    async def compare_forecasts(
        self,
        dataset_id: UUID,
        forecast_ids: Optional[List[UUID]] = None,
        metric_key: Optional[str] = None,
    ) -> ForecastComparisonResponse:
        """
        Synthesizes a side-by-side comparison matrix across multiple forecast runs.
        Enforces strict dataset isolation: all forecast IDs must belong to the requested dataset.
        """
        await self._validate_dataset_exists(dataset_id)

        if forecast_ids and len(forecast_ids) > 0:
            forecasts = await self.repo.get_by_ids(dataset_id=dataset_id, forecast_ids=forecast_ids)
            if len(forecasts) != len(forecast_ids):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="One or more specified forecast IDs do not exist or do not belong to the requested dataset.",
                )
        else:
            forecasts = await self.repo.list_history_by_dataset(
                dataset_id=dataset_id,
                metric_key=metric_key,
                limit=5,
                offset=0,
            )

        if not forecasts or len(forecasts) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No forecasts available for comparison on this dataset.",
            )

        # Build comparison items and delta matrix
        target_metric = forecasts[0].metric_key
        comparison_items = []
        matrix_periods: Dict[str, Dict[str, Any]] = {}

        for f in forecasts:
            item = ForecastComparisonItem(
                forecast_id=f.id,
                forecast_version=f.forecast_version,
                model_name=f.model_name,
                horizon=f.horizon,
                frequency=f.frequency,
                model_metrics=ModelMetrics(**f.model_metrics),
                trend=f.trend,
                forecast_points=[ForecastPoint(**p) for p in f.forecast_points],
            )
            comparison_items.append(item)

            for p in f.forecast_points:
                period_key = p["period"]
                if period_key not in matrix_periods:
                    matrix_periods[period_key] = {}
                matrix_periods[period_key][str(f.id)] = {
                    "version": f.forecast_version,
                    "model": f.model_name,
                    "predicted": p["predicted_value"],
                    "lower": p.get("lower_bound"),
                    "upper": p.get("upper_bound"),
                }

        return ForecastComparisonResponse(
            dataset_id=dataset_id,
            metric_key=target_metric,
            forecasts=comparison_items,
            comparison_matrix={
                "periods": matrix_periods,
                "summary": {
                    str(f.id): {
                        "version": f.forecast_version,
                        "model": f.model_name,
                        "rmse": f.model_metrics.get("rmse"),
                        "trend": f.trend,
                    }
                    for f in forecasts
                },
            },
        )

    async def delete_forecast(self, forecast_id: UUID) -> bool:
        """Deletes a specific forecast simulation."""
        deleted = await self.repo.delete_by_id(forecast_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Forecast '{forecast_id}' not found",
            )
        if self._is_async():
            await self.db.commit()
        else:
            self.db.commit()
        return True
