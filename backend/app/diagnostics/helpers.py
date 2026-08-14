"""Lightweight data loading, column projection, time-series calculation, and finding factory utilities."""

import os
from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd

from app.core.constants import FindingSeverity, FindingType
from app.core.logging import logger
from app.models.dataset import Dataset
from app.models.dataset_metric import DatasetMetric
from app.models.diagnostic_finding import DiagnosticFinding


def extract_metrics_dict(metrics: List[DatasetMetric]) -> Dict[str, Any]:
    """
    Extracts a key-value mapping from pre-calculated DatasetMetric instances.
    
    Args:
        metrics: List of DatasetMetric records.
        
    Returns:
        Dictionary mapping metric_key -> metric_value.
    """
    return {m.metric_key: m.metric_value for m in metrics}


def load_lightweight_columns(
    dataset: Dataset,
    required_standard_fields: List[str],
) -> Optional[pd.DataFrame]:
    """
    Memory-efficient CSV loader using column projection (`usecols`).
    
    Inspects dataset column mappings to find the original physical CSV column names
    corresponding to the required canonical business fields, loads only those columns,
    and returns a normalized DataFrame.
    
    Args:
        dataset: The Dataset ORM instance.
        required_standard_fields: List of canonical standard field names needed (e.g. ['order_date', 'revenue']).
        
    Returns:
        DataFrame with standardized column names, or None if the file is missing or required columns are unmapped.
    """
    if not dataset or not dataset.file_path or not os.path.exists(dataset.file_path):
        return None

    try:
        # Build mapping: original_column_name -> standard_field
        col_mappings: Dict[str, str] = {}
        if hasattr(dataset, "columns") and dataset.columns:
            for col in dataset.columns:
                if col.mapped_field in required_standard_fields:
                    col_mappings[col.original_name] = col.mapped_field

        # If not all required fields were found in dataset.columns, check if raw CSV columns match directly
        needed_fields = set(required_standard_fields)
        mapped_fields_found = set(col_mappings.values())

        if mapped_fields_found != needed_fields:
            # Fallback: Read sample header from CSV to check for direct column name matches
            header_df = pd.read_csv(dataset.file_path, nrows=0)
            for col_name in header_df.columns:
                norm_name = col_name.strip().lower().replace(" ", "_")
                if norm_name in needed_fields and col_name not in col_mappings:
                    col_mappings[col_name] = norm_name

        # Verify that we found at least one required field
        if not col_mappings:
            return None

        # Load only mapped columns via usecols projection
        df = pd.read_csv(dataset.file_path, usecols=list(col_mappings.keys()))
        # Rename physical columns to standard canonical names
        df = df.rename(columns=col_mappings)
        return df

    except Exception as e:
        logger.debug(f"Lightweight column loading skipped for dataset {dataset.id}: {e}")
        return None


def compute_time_series_aggregates(
    df: pd.DataFrame,
    date_col: str = "order_date",
    value_col: str = "revenue",
    freq: str = "ME",
) -> Optional[pd.DataFrame]:
    """
    Aggregates tabular time-series into periodic buckets and calculates percentage changes and trend statistics.
    
    Args:
        df: DataFrame containing date and value columns.
        date_col: Name of the timestamp/date column.
        value_col: Name of the numerical value column to aggregate.
        freq: Pandas offset alias frequency (e.g. 'ME' for month-end, 'W' for weekly, 'D' for daily).
        
    Returns:
        Aggregated DataFrame indexed by period with columns ['total', 'pct_change', 'rolling_mean', 'cv'] or None.
    """
    if df is None or df.empty or date_col not in df.columns or value_col not in df.columns:
        return None

    try:
        working = df[[date_col, value_col]].dropna().copy()
        working[date_col] = pd.to_datetime(working[date_col], errors="coerce")
        working[value_col] = pd.to_numeric(working[value_col], errors="coerce")
        working = working.dropna()

        if len(working) < 2:
            return None

        # Check time span: If data spans multiple calendar months, bucket monthly (ME)
        min_dt = working[date_col].min()
        max_dt = working[date_col].max()
        months_span = (max_dt.year - min_dt.year) * 12 + (max_dt.month - min_dt.month)
        timespan_days = (max_dt - min_dt).days

        if months_span >= 1:
            effective_freq = "M"
        elif timespan_days >= 14:
            effective_freq = "W"
        else:
            effective_freq = "D"

        # Group by period
        try:
            grouped = (
                working.set_index(date_col)
                .resample(effective_freq)[value_col]
                .sum()
                .reset_index()
            )
        except ValueError:
            effective_freq = "ME" if effective_freq == "M" else effective_freq
            grouped = (
                working.set_index(date_col)
                .resample(effective_freq)[value_col]
                .sum()
                .reset_index()
            )
        grouped.columns = ["period", "total"]

        # Drop empty trailing/leading zero buckets if no activity
        grouped = grouped[grouped["total"] > 0].copy()
        if len(grouped) < 2:
            return None

        # Period-over-period percentage change
        grouped["pct_change"] = grouped["total"].pct_change()
        grouped["rolling_mean"] = grouped["total"].rolling(window=3, min_periods=1).mean()

        mean_val = grouped["total"].mean()
        std_val = grouped["total"].std()
        grouped["cv"] = (std_val / mean_val) if mean_val > 0 and not np.isnan(std_val) else 0.0

        return grouped

    except Exception as e:
        logger.debug(f"Time-series aggregation failed: {e}")
        return None


def create_diagnostic_finding(
    dataset: Dataset,
    finding_type: FindingType,
    severity: FindingSeverity,
    title: str,
    description: str,
    business_impact: str,
    metric_key: Optional[str],
    confidence_score: float,
    supporting_data: Dict[str, Any],
) -> DiagnosticFinding:
    """
    Standard entity factory instantiating a validated DiagnosticFinding ORM instance.
    """
    return DiagnosticFinding(
        dataset_id=dataset.id,
        finding_type=finding_type,
        severity=severity,
        title=title,
        description=description,
        business_impact=business_impact,
        metric_key=metric_key,
        confidence_score=max(0.0, min(1.0, confidence_score)),
        supporting_data=supporting_data,
    )
