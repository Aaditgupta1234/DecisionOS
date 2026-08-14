"""Constants and supported metric definitions for Phase 6.3 Scenario Simulation Engine."""

from typing import Dict, Set
from app.core.constants import MetricCategory, ScenarioAdjustmentType

DEFAULT_SCENARIO_VERSION = "1.0"
DEFAULT_SIMULATION_RULE_VERSION = "1.0"

# Pagination defaults
DEFAULT_SCENARIO_LIMIT = 10
MAX_SCENARIO_LIMIT = 100

# Metric Boundary Constraints (min, max, allow_floats, unit)
# None represents unbounded
METRIC_BOUNDARIES: Dict[str, Dict[str, any]] = {
    "total_revenue": {"min": 0.0, "max": None, "allow_float": True, "category": MetricCategory.REVENUE},
    "average_revenue": {"min": 0.0, "max": None, "allow_float": True, "category": MetricCategory.REVENUE},
    "maximum_revenue": {"min": 0.0, "max": None, "allow_float": True, "category": MetricCategory.REVENUE},
    "minimum_revenue": {"min": 0.0, "max": None, "allow_float": True, "category": MetricCategory.REVENUE},
    "revenue_per_customer": {"min": 0.0, "max": None, "allow_float": True, "category": MetricCategory.REVENUE},
    "total_orders": {"min": 0, "max": None, "allow_float": False, "category": MetricCategory.ORDERS},
    "completed_orders": {"min": 0, "max": None, "allow_float": False, "category": MetricCategory.ORDERS},
    "cancelled_orders": {"min": 0, "max": None, "allow_float": False, "category": MetricCategory.ORDERS},
    "completion_rate": {"min": 0.0, "max": 100.0, "allow_float": True, "category": MetricCategory.ORDERS},
    "unique_customers": {"min": 0, "max": None, "allow_float": False, "category": MetricCategory.CUSTOMERS},
    "customer_churn_rate": {"min": 0.0, "max": 100.0, "allow_float": True, "category": MetricCategory.CUSTOMERS},
    "customer_retention_rate": {"min": 0.0, "max": 100.0, "allow_float": True, "category": MetricCategory.CUSTOMERS},
    "average_review_score": {"min": 1.0, "max": 5.0, "allow_float": True, "category": MetricCategory.REVIEWS},
    "average_delivery_time": {"min": 0.0, "max": None, "allow_float": True, "category": MetricCategory.DELIVERY},
}

# Allowed adjustment types per metric key
ALLOWED_ADJUSTMENT_TYPES: Dict[str, Set[ScenarioAdjustmentType]] = {
    "total_revenue": {ScenarioAdjustmentType.RELATIVE_PERCENT, ScenarioAdjustmentType.ABSOLUTE_VALUE},
    "average_revenue": {ScenarioAdjustmentType.RELATIVE_PERCENT, ScenarioAdjustmentType.ABSOLUTE_VALUE},
    "maximum_revenue": {ScenarioAdjustmentType.RELATIVE_PERCENT, ScenarioAdjustmentType.ABSOLUTE_VALUE},
    "minimum_revenue": {ScenarioAdjustmentType.RELATIVE_PERCENT, ScenarioAdjustmentType.ABSOLUTE_VALUE},
    "revenue_per_customer": {ScenarioAdjustmentType.RELATIVE_PERCENT, ScenarioAdjustmentType.ABSOLUTE_VALUE},
    "total_orders": {ScenarioAdjustmentType.RELATIVE_PERCENT, ScenarioAdjustmentType.ABSOLUTE_VALUE},
    "completed_orders": {ScenarioAdjustmentType.RELATIVE_PERCENT, ScenarioAdjustmentType.ABSOLUTE_VALUE},
    "cancelled_orders": {ScenarioAdjustmentType.RELATIVE_PERCENT, ScenarioAdjustmentType.ABSOLUTE_VALUE},
    "completion_rate": {ScenarioAdjustmentType.PERCENTAGE_POINTS, ScenarioAdjustmentType.RELATIVE_PERCENT},
    "unique_customers": {ScenarioAdjustmentType.RELATIVE_PERCENT, ScenarioAdjustmentType.ABSOLUTE_VALUE},
    "customer_churn_rate": {ScenarioAdjustmentType.PERCENTAGE_POINTS, ScenarioAdjustmentType.RELATIVE_PERCENT},
    "customer_retention_rate": {ScenarioAdjustmentType.PERCENTAGE_POINTS, ScenarioAdjustmentType.RELATIVE_PERCENT},
    "average_review_score": {ScenarioAdjustmentType.ABSOLUTE_VALUE, ScenarioAdjustmentType.RELATIVE_PERCENT},
    "average_delivery_time": {ScenarioAdjustmentType.RELATIVE_PERCENT, ScenarioAdjustmentType.ABSOLUTE_VALUE},
}

SUPPORTED_SIMULATION_METRICS: Set[str] = set(METRIC_BOUNDARIES.keys())

DEFAULT_SCENARIO_LIMITATIONS = [
    "This is a deterministic what-if simulation, not a predictive forecast.",
    "Projected results are calculated strictly from the explicitly supplied assumptions and registered deterministic propagation rules.",
    "No causal propagation was applied where no explicit deterministic mathematical relationship exists in DecisionOS.",
    "Projected outcomes do not account for unmodelled macroeconomic or external competitive market dynamics.",
]
