"""SQLAlchemy Forecast Model for Phase 6.4 Forecasting Engine."""

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Dict, List, Optional
from sqlalchemy import (
    DateTime,
    Enum as SQLEnum,
    Float,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import (
    ForecastFrequency,
    ForecastHorizon,
    ForecastStatus,
    ForecastTrend,
)
from app.database.base import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.dataset import Dataset


class Forecast(TimestampMixin, Base):
    """
    Persisted deterministic time-series forecast artifact.
    Stores historical observation counts, step projections, prediction intervals,
    model evaluation metrics (MAE/RMSE), trend classifications, and limitations.
    """

    __tablename__ = "forecasts"

    __table_args__ = (
        Index(
            "ix_forecasts_dataset_created",
            "dataset_id",
            "created_at",
        ),
        Index(
            "ix_forecasts_dataset_metric",
            "dataset_id",
            "metric_key",
        ),
        Index(
            "ix_forecasts_dataset_metric_created",
            "dataset_id",
            "metric_key",
            "created_at",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    dataset_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("datasets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    forecast_version: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="1.0",
    )

    metric_key: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        index=True,
    )

    horizon: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )

    frequency: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )

    model_name: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        default="NAIVE",
    )

    model_version: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="1.0",
    )

    confidence_level: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.80,
    )

    status: Mapped[ForecastStatus] = mapped_column(
        SQLEnum(ForecastStatus, name="forecast_status"),
        nullable=False,
        default=ForecastStatus.COMPLETED,
        index=True,
    )

    historical_observation_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    forecast_points: Mapped[List[Dict[str, Any]]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=False,
        default=list,
    )

    model_metrics: Mapped[Dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=False,
        default=dict,
    )

    trend: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="STABLE",
    )

    limitations: Mapped[List[str]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=False,
        default=list,
    )

    baseline_snapshot: Mapped[Dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=False,
        default=dict,
    )

    metadata_info: Mapped[Dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=False,
        default=dict,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    dataset: Mapped["Dataset"] = relationship(
        "Dataset",
        back_populates="forecasts",
    )

    def __repr__(self) -> str:
        return (
            f"<Forecast id={self.id} dataset_id={self.dataset_id} "
            f"metric={self.metric_key} horizon={self.horizon} model={self.model_name} version={self.forecast_version}>"
        )
