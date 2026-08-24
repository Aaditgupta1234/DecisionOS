"""Portfolio State Service managing explicit lifecycle states and activation checklist criteria."""

from enum import Enum
from typing import Any, Dict, Optional
from app.portfolio.constants.portfolio_constants import PortfolioState, MIN_BENCHMARK_WORKSPACES


class PortfolioStateService:
    """
    Centralizes lifecycle state transitions and activation progress for the Portfolio & Capital Allocation Studio.
    
    Lifecycle States:
        - INSUFFICIENT_DATA: workspace_count == 0
        - SINGLE_WORKSPACE: workspace_count == 1
        - AVAILABLE: workspace_count >= 2
    """

    @staticmethod
    def compute_portfolio_state(workspace_count: int) -> PortfolioState:
        """Determines deterministic PortfolioState enum from active workspace count."""
        if workspace_count <= 0:
            return PortfolioState.INSUFFICIENT_DATA
        elif workspace_count == 1:
            return PortfolioState.SINGLE_WORKSPACE
        else:
            return PortfolioState.AVAILABLE

    @staticmethod
    def get_benchmark_readiness(workspace_count: int) -> Dict[str, Any]:
        """Calculates benchmark readiness status and required workspaces."""
        is_available = workspace_count >= MIN_BENCHMARK_WORKSPACES
        return {
            "current_workspaces": workspace_count,
            "required_workspaces": MIN_BENCHMARK_WORKSPACES,
            "status": "AVAILABLE" if is_available else "PENDING",
            "benchmark_available": is_available,
        }

    @staticmethod
    def evaluate_activation_checklist(
        workspace_count: int,
        has_dataset: bool = True,
        has_snapshot: bool = False,
        has_kpi_analysis: bool = False,
        has_diagnostics: bool = False,
    ) -> Dict[str, Any]:
        """
        Dynamically evaluates activation progress steps without hardcoded percentages.
        """
        items = [
            {
                "id": "dataset_available",
                "label": "Dataset Available",
                "completed": bool(has_dataset),
            },
            {
                "id": "create_additional_workspace",
                "label": "Create Additional Workspace",
                "completed": workspace_count >= 2,
            },
            {
                "id": "generate_snapshot",
                "label": "Generate Dashboard Snapshot",
                "completed": bool(has_snapshot or workspace_count >= 1),
            },
            {
                "id": "run_kpi_analysis",
                "label": "Run KPI Analysis",
                "completed": bool(has_kpi_analysis or workspace_count >= 1),
            },
            {
                "id": "run_diagnostics",
                "label": "Run Diagnostics & Recommendations",
                "completed": bool(has_diagnostics or workspace_count >= 1),
            },
            {
                "id": "benchmarking_available",
                "label": "Portfolio Benchmarking Available",
                "completed": workspace_count >= MIN_BENCHMARK_WORKSPACES,
            },
        ]
        completed_count = sum(1 for item in items if item["completed"])
        total_count = len(items)
        progress_ratio = round(completed_count / total_count, 2)

        return {
            "items": items,
            "completed_count": completed_count,
            "total_count": total_count,
            "progress_ratio": progress_ratio,
            "is_fully_activated": workspace_count >= MIN_BENCHMARK_WORKSPACES,
        }
