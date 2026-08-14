"""KPI Engine orchestrating dataset metrics calculation, persistence, idempotency, and summary reporting."""

from datetime import datetime, timezone
from typing import Dict, List
from uuid import UUID
from fastapi import HTTPException, status
import pandas as pd
from sqlalchemy.orm import Session

from app.core.constants import DatasetStatus, MetricCategory, MetricsGenerationStatus, UserRole
from app.core.logging import logger
from app.models.dataset import Dataset
from app.models.dataset_metric import DatasetMetric
from app.models.metric_definition import MetricDefinition
from app.models.user import User
from app.schemas.metric import (
    MetricGenerationResponse,
    MetricResponse,
    MetricSummaryResponse,
)
from app.services.dataset_service import get_dataset_by_id
from app.services.metric_calculator import CalculatedMetric, KPICalculator


def run_kpi_engine(
    db: Session,
    dataset_id: UUID,
    current_user: User,
) -> MetricGenerationResponse:
    """Orchestrates KPI calculation, old metric replacement, and status updates for a dataset."""
    # 1. Fetch dataset and verify readiness
    dataset = get_dataset_by_id(db=db, dataset_id=dataset_id, current_user=current_user)

    if dataset.status != DatasetStatus.READY:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Dataset must be in READY status before KPI generation (current status: {dataset.status.value}).",
        )

    # 2. Load dataset CSV from storage
    try:
        df = pd.read_csv(dataset.file_path)
    except Exception as e:
        logger.error(f"Failed to read CSV for dataset {dataset_id}: {e}")
        dataset.metrics_generation_status = MetricsGenerationStatus.FAILED
        dataset.metrics_generation_error = f"Failed to load dataset file: {str(e)}"
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error reading dataset file: {str(e)}",
        )

    # 3. Build mapped fields lookup
    mapped_fields: Dict[str, str] = {
        col.original_name: col.mapped_field
        for col in dataset.columns
        if col.mapped_field
    }

    # 4. Calculate metrics
    try:
        calculator = KPICalculator(df=df, mapped_fields=mapped_fields)
        calculated_metrics, skipped_categories = calculator.calculate_all()
    except Exception as e:
        logger.error(f"KPI calculation failed for dataset {dataset_id}: {e}")
        dataset.metrics_generation_status = MetricsGenerationStatus.FAILED
        dataset.metrics_generation_error = f"Calculation error: {str(e)}"
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"KPI calculation error: {str(e)}",
        )

    # 5. Idempotent Replacement: Remove existing metrics for this dataset
    db.query(DatasetMetric).filter(DatasetMetric.dataset_id == dataset.id).delete()

    # 6. Resolve MetricDefinitions and persist new DatasetMetric records
    now = datetime.now(timezone.utc)
    new_metrics: List[DatasetMetric] = []

    # Cache existing definitions
    existing_definitions = {
        d.metric_key: d
        for d in db.query(MetricDefinition).all()
    }

    for cm in calculated_metrics:
        definition = existing_definitions.get(cm.metric_key)
        if not definition:
            # Auto-create definition if missing to guarantee robustness
            definition = MetricDefinition(
                name=cm.metric_name,
                metric_key=cm.metric_key,
                metric_category=cm.metric_category,
                required_field=cm.metric_key,
                is_active=True,
            )
            db.add(definition)
            db.flush()
            existing_definitions[cm.metric_key] = definition

        metric_record = DatasetMetric(
            dataset_id=dataset.id,
            metric_definition_id=definition.id,
            generated_by=current_user.id,
            metric_key=cm.metric_key,
            metric_name=cm.metric_name,
            metric_category=cm.metric_category,
            metric_value=cm.metric_value,
            calculated_at=now,
        )
        db.add(metric_record)
        new_metrics.append(metric_record)

    # 7. Update Dataset KPI Tracking state
    dataset.metrics_generation_status = MetricsGenerationStatus.GENERATED
    dataset.metrics_generated_at = now
    dataset.metrics_generation_error = None

    db.commit()

    # Refresh newly created records
    for m in new_metrics:
        db.refresh(m)

    logger.info(f"Successfully generated {len(new_metrics)} KPIs for dataset '{dataset.name}' ({dataset.id})")
    return MetricGenerationResponse(
        dataset_id=dataset.id,
        metrics_generated=len(new_metrics),
        metrics=[MetricResponse.model_validate(m) for m in new_metrics],
        skipped_categories=skipped_categories,
    )


def get_dataset_metrics(
    db: Session,
    dataset_id: UUID,
    current_user: User,
) -> List[DatasetMetric]:
    """Retrieves all computed metrics for a dataset with role-based access scoping."""
    get_dataset_by_id(db=db, dataset_id=dataset_id, current_user=current_user)
    return db.query(DatasetMetric).filter(
        DatasetMetric.dataset_id == dataset_id
    ).order_by(DatasetMetric.metric_category, DatasetMetric.metric_key).all()


def get_dataset_metrics_summary(
    db: Session,
    dataset_id: UUID,
    current_user: User,
) -> MetricSummaryResponse:
    """Returns calculated dataset KPIs grouped by category."""
    metrics = get_dataset_metrics(db=db, dataset_id=dataset_id, current_user=current_user)

    summary: Dict[str, Dict[str, any]] = {
        "revenue": {},
        "orders": {},
        "customers": {},
        "reviews": {},
        "delivery": {},
        "quality": {},
    }

    for m in metrics:
        cat_key = m.metric_category.value if hasattr(m.metric_category, "value") else str(m.metric_category)
        if cat_key in summary:
            summary[cat_key][m.metric_key] = m.metric_value

    return MetricSummaryResponse(
        dataset_id=dataset_id,
        revenue=summary["revenue"],
        orders=summary["orders"],
        customers=summary["customers"],
        reviews=summary["reviews"],
        delivery=summary["delivery"],
        quality=summary["quality"],
    )
