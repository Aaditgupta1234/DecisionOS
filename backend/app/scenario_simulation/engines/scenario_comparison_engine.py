"""ScenarioComparisonEngine generating deterministic side-by-side delta matrices across scenarios."""

from typing import Any, Dict, List
from uuid import UUID
from app.models.scenario import Scenario
from app.scenario_simulation.schemas.scenario_schema import (
    ScenarioAssumption,
    ScenarioComparisonItem,
    ScenarioComparisonResponse,
    ScenarioHealthProjection,
    ScenarioMetricProjection,
)


class ScenarioComparisonEngine:
    """
    Deterministic comparative analytics engine comparing multiple scenarios against baseline.
    """

    @classmethod
    def compare(
        cls,
        dataset_id: UUID,
        baseline_snapshot: Dict[str, Any],
        scenarios: List[Scenario],
    ) -> ScenarioComparisonResponse:
        """
        Synthesizes a structured side-by-side comparison across all provided scenarios.
        """
        baseline_health = baseline_snapshot.get("health", {})
        comparison_items: List[ScenarioComparisonItem] = []
        matrix_metrics: Dict[str, Dict[str, Any]] = {}

        # Collect all metric keys across baseline and scenarios
        base_metrics_dict = baseline_snapshot.get("metrics", {})

        for sc in scenarios:
            # Assumptions
            assumptions_list = [
                ScenarioAssumption(
                    metric_key=a["metric_key"],
                    adjustment_type=a["adjustment_type"],
                    adjustment_value=a["adjustment_value"],
                )
                for a in sc.assumptions
            ]

            # Health projection
            h_data = sc.projected_health
            health_proj = ScenarioHealthProjection(
                baseline_score=h_data.get("baseline_score", 0),
                projected_score=h_data.get("projected_score", 0),
                score_delta=h_data.get("score_delta", 0),
                baseline_status=h_data.get("baseline_status", "WATCH_LIST"),
                projected_status=h_data.get("projected_status", "WATCH_LIST"),
                status_changed=h_data.get("status_changed", False),
            )

            # Metric projections
            proj_metrics_list = [
                ScenarioMetricProjection(**m)
                for m in sc.projected_metrics
            ]

            comparison_items.append(
                ScenarioComparisonItem(
                    scenario_id=sc.id,
                    name=sc.name,
                    assumptions=assumptions_list,
                    health=health_proj,
                    metric_projections=proj_metrics_list,
                )
            )

            # Populate matrix
            for m in sc.projected_metrics:
                k = m["metric_key"]
                if k not in matrix_metrics:
                    matrix_metrics[k] = {
                        "baseline": m["baseline_value"],
                        "scenarios": {},
                    }
                matrix_metrics[k]["scenarios"][str(sc.id)] = {
                    "scenario_name": sc.name,
                    "projected_value": m["projected_value"],
                    "absolute_delta": m["absolute_delta"],
                    "percentage_delta": m["percentage_delta"],
                }

        comparison_matrix = {
            "metrics": matrix_metrics,
            "health_summary": {
                "baseline_score": baseline_health.get("score", 100),
                "baseline_status": baseline_health.get("status", "EXCELLENT"),
                "scenarios": {
                    str(sc.id): {
                        "name": sc.name,
                        "projected_score": sc.projected_health.get("projected_score"),
                        "score_delta": sc.projected_health.get("score_delta"),
                        "projected_status": sc.projected_health.get("projected_status"),
                    }
                    for sc in scenarios
                },
            },
        }

        return ScenarioComparisonResponse(
            dataset_id=dataset_id,
            baseline_health=baseline_health,
            scenarios=comparison_items,
            comparison_matrix=comparison_matrix,
        )
