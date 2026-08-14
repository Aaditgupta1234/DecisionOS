"""RecommendationTemplate data model defining modular business action blueprints."""

from dataclasses import dataclass, field
from typing import List, Optional

from app.core.constants import ExpectedTimeToValue, RecommendationType


@dataclass(frozen=True)
class RecommendationTemplate:
    """
    Modular business action blueprint defining executable steps, success metrics,
    time-to-value, and default impact/effort benchmarks.
    
    Attributes:
        title: Concise action headline (e.g. "Launch Retention Campaign").
        description: Strategic summary of the proposed business initiative.
        actions: Concrete ordered list of execution steps.
        success_metrics: Target KPIs to monitor (e.g. ["Customer Retention Rate", "Repeat Purchase Rate"]).
        expected_time_to_value: Anticipated timeframe to realize returns (IMMEDIATE, SHORT_TERM, etc.).
        default_impact: Baseline impact score [0.0 - 1.0].
        default_effort: Baseline execution effort [0.0 - 1.0].
        recommendation_type: Optional override for recommendation classification.
        target_metric_name: Primary KPI for outcome measurement (e.g. "Customer Retention Rate").
        target_improvement_ratio: Expected fractional improvement over baseline (e.g. 0.15 for +15%).
        measurement_period: Duration for measuring outcome returns (e.g. "90 days").
    """

    title: str
    description: str
    actions: List[str]
    success_metrics: List[str]
    expected_time_to_value: ExpectedTimeToValue
    default_impact: float
    default_effort: float
    recommendation_type: Optional[RecommendationType] = None
    target_metric_name: Optional[str] = None
    target_improvement_ratio: float = 0.10
    measurement_period: str = "90 days"
