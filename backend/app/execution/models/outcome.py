"""SQLAlchemy Models for Phase 12.6: Outcomes & Benefits Realization Engine."""

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional
from sqlalchemy import (
    DateTime,
    Enum as SQLEnum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.execution.constants import (
    BenefitRealizationStatus,
    BenefitTrend,
    BenefitType,
    ConfidenceTrend,
    MeasurementFrequency,
    MeasurementQuality,
    MeasurementRecency,
    MeasurementStability,
    OutcomeConfidenceLevel,
    OutcomeCriticality,
    OutcomeExecutionStatus,
    OutcomeHealth,
    OutcomeMetricType,
    OutcomeStatus,
    OutcomeValueClassification,
    TargetDateStatus,
)
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.execution.models.initiative import StrategicInitiative
    from app.models.organization import Organization


class InitiativeOutcomeMeasurement(TimestampMixin, Base):
    """
    Quantitative outcome measurement entity evaluating final KPI realization versus expected targets,
    stability, data quality, data freshness, schedule adherence, and predictability.
    """

    __tablename__ = "initiative_outcomes"

    __table_args__ = (
        Index("ix_initiative_outcomes_initiative", "initiative_id"),
        Index("ix_initiative_outcomes_org", "organization_id"),
        Index("ix_initiative_outcomes_status", "organization_id", "status"),
        Index("ix_initiative_outcomes_type", "organization_id", "metric_type"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    initiative_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("strategic_initiatives.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    target_metric: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    metric_type: Mapped[OutcomeMetricType] = mapped_column(
        SQLEnum(OutcomeMetricType, name="outcome_metric_type"),
        nullable=False,
        default=OutcomeMetricType.STRATEGIC,
    )

    criticality: Mapped[OutcomeCriticality] = mapped_column(
        SQLEnum(OutcomeCriticality, name="outcome_criticality"),
        nullable=False,
        default=OutcomeCriticality.HIGH,
    )

    baseline_value: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    target_value: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    actual_value: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    measurement_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    target_achievement_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    days_until_target: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )

    target_date_status: Mapped[TargetDateStatus] = mapped_column(
        SQLEnum(TargetDateStatus, name="target_date_status"),
        nullable=False,
        default=TargetDateStatus.ON_TIME,
    )

    realization_delay_days: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )

    measurement_version: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
    )

    measurement_frequency: Mapped[MeasurementFrequency] = mapped_column(
        SQLEnum(MeasurementFrequency, name="measurement_frequency"),
        nullable=False,
        default=MeasurementFrequency.MONTHLY,
    )

    status: Mapped[OutcomeStatus] = mapped_column(
        SQLEnum(OutcomeStatus, name="outcome_status"),
        nullable=False,
        default=OutcomeStatus.IN_PROGRESS,
    )

    achievement_percentage: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    target_variance: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    improvement_amount: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    confidence_level: Mapped[OutcomeConfidenceLevel] = mapped_column(
        SQLEnum(OutcomeConfidenceLevel, name="outcome_confidence_level"),
        nullable=False,
        default=OutcomeConfidenceLevel.HIGH,
    )

    confidence_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=100.0,
    )

    confidence_trend: Mapped[ConfidenceTrend] = mapped_column(
        SQLEnum(ConfidenceTrend, name="confidence_trend"),
        nullable=False,
        default=ConfidenceTrend.STABLE,
    )

    measurement_stability: Mapped[MeasurementStability] = mapped_column(
        SQLEnum(MeasurementStability, name="measurement_stability"),
        nullable=False,
        default=MeasurementStability.HIGH,
    )

    measurement_stability_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=100.0,
    )

    measurement_volatility: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    measurement_quality: Mapped[MeasurementQuality] = mapped_column(
        SQLEnum(MeasurementQuality, name="measurement_quality"),
        nullable=False,
        default=MeasurementQuality.HIGH,
    )

    measurement_reliability_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=100.0,
    )

    outcome_data_reliability_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=100.0,
    )

    measurement_recency: Mapped[MeasurementRecency] = mapped_column(
        SQLEnum(MeasurementRecency, name="measurement_recency"),
        nullable=False,
        default=MeasurementRecency.CURRENT,
    )

    measurement_completeness_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=100.0,
    )

    outcome_predictability_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=100.0,
    )

    outcome_health: Mapped[OutcomeHealth] = mapped_column(
        SQLEnum(OutcomeHealth, name="outcome_health"),
        nullable=False,
        default=OutcomeHealth.HEALTHY,
    )

    execution_status: Mapped[OutcomeExecutionStatus] = mapped_column(
        SQLEnum(OutcomeExecutionStatus, name="outcome_execution_status"),
        nullable=False,
        default=OutcomeExecutionStatus.ON_TRACK,
    )

    owner_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )

    owner_name: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    verdict_summary: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="",
    )

    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )

    updated_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )

    # Backwards compatibility properties
    @property
    def metric_name(self) -> str:
        return self.target_metric

    @metric_name.setter
    def metric_name(self, value: str) -> None:
        self.target_metric = value

    @property
    def target_achievement_percentage(self) -> float:
        return self.achievement_percentage

    @target_achievement_percentage.setter
    def target_achievement_percentage(self, value: float) -> None:
        self.achievement_percentage = value

    @property
    def outcome_confidence(self) -> OutcomeConfidenceLevel:
        return self.confidence_level

    @outcome_confidence.setter
    def outcome_confidence(self, value: OutcomeConfidenceLevel) -> None:
        self.confidence_level = value

    @property
    def measured_at(self) -> datetime:
        return self.measurement_date

    @measured_at.setter
    def measured_at(self, value: datetime) -> None:
        self.measurement_date = value

    # Relational Navigation
    initiative: Mapped["StrategicInitiative"] = relationship(
        "StrategicInitiative",
        back_populates="outcomes",
    )

    organization: Mapped["Organization"] = relationship(
        "Organization",
        foreign_keys=[organization_id],
    )

    def __repr__(self) -> str:
        return (
            f"<InitiativeOutcomeMeasurement id={self.id} metric='{self.target_metric}' "
            f"achievement={self.achievement_percentage:.1f}% status={self.status.value}>"
        )


# Backward compatibility alias
InitiativeOutcome = InitiativeOutcomeMeasurement


class InitiativeBenefitRealization(TimestampMixin, Base):
    """
    Quantitative strategic benefit entity tracking financial and non-financial value creation,
    ROI, gap analysis, and realization scoring against initiative investment.
    """

    __tablename__ = "initiative_benefit_realizations"

    __table_args__ = (
        Index("ix_initiative_benefits_initiative", "initiative_id"),
        Index("ix_initiative_benefits_org", "organization_id"),
        Index("ix_initiative_benefits_type", "organization_id", "benefit_type"),
        Index("ix_initiative_benefits_status", "organization_id", "realization_status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    initiative_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("strategic_initiatives.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    benefit_type: Mapped[BenefitType] = mapped_column(
        SQLEnum(BenefitType, name="benefit_type"),
        nullable=False,
        default=BenefitType.STRATEGIC_VALUE,
    )

    expected_value: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    realized_value: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    realization_percentage: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    realization_status: Mapped[BenefitRealizationStatus] = mapped_column(
        SQLEnum(BenefitRealizationStatus, name="benefit_realization_status"),
        nullable=False,
        default=BenefitRealizationStatus.MISSED,
    )

    realization_gap: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    benefit_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    value_classification: Mapped[OutcomeValueClassification] = mapped_column(
        SQLEnum(OutcomeValueClassification, name="outcome_value_classification"),
        nullable=False,
        default=OutcomeValueClassification.LOW,
    )

    confidence_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=100.0,
    )

    confidence_level: Mapped[OutcomeConfidenceLevel] = mapped_column(
        SQLEnum(OutcomeConfidenceLevel, name="benefit_confidence_level"),
        nullable=False,
        default=OutcomeConfidenceLevel.HIGH,
    )

    confidence_trend: Mapped[ConfidenceTrend] = mapped_column(
        SQLEnum(ConfidenceTrend, name="benefit_confidence_trend"),
        nullable=False,
        default=ConfidenceTrend.STABLE,
    )

    benefit_trend: Mapped[BenefitTrend] = mapped_column(
        SQLEnum(BenefitTrend, name="benefit_trend"),
        nullable=False,
        default=BenefitTrend.STABLE,
    )

    investment_cost: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    currency: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        default="USD",
    )

    measured_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    notes: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="",
    )

    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )

    updated_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )

    # Relational Navigation
    initiative: Mapped["StrategicInitiative"] = relationship(
        "StrategicInitiative",
        back_populates="benefits",
    )

    organization: Mapped["Organization"] = relationship(
        "Organization",
        foreign_keys=[organization_id],
    )

    def __repr__(self) -> str:
        return (
            f"<InitiativeBenefitRealization id={self.id} type={self.benefit_type.value} "
            f"realized={self.realized_value}/{self.expected_value} status={self.realization_status.value}>"
        )
