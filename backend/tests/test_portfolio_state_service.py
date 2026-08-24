"""Tests for PortfolioStateService and explicit portfolio lifecycle states."""

import pytest
from app.portfolio.constants.portfolio_constants import PortfolioState, MIN_BENCHMARK_WORKSPACES
from app.portfolio.services.portfolio_state_service import PortfolioStateService


def test_portfolio_state_lifecycle_transitions():
    """Verify deterministic PortfolioState transitions across workspace counts."""
    # State A: 0 workspaces -> INSUFFICIENT_DATA
    assert PortfolioStateService.compute_portfolio_state(0) == PortfolioState.INSUFFICIENT_DATA
    assert PortfolioStateService.compute_portfolio_state(-1) == PortfolioState.INSUFFICIENT_DATA

    # State B: 1 workspace -> SINGLE_WORKSPACE
    assert PortfolioStateService.compute_portfolio_state(1) == PortfolioState.SINGLE_WORKSPACE

    # State C: 2+ workspaces -> AVAILABLE
    assert PortfolioStateService.compute_portfolio_state(2) == PortfolioState.AVAILABLE
    assert PortfolioStateService.compute_portfolio_state(5) == PortfolioState.AVAILABLE
    assert PortfolioStateService.compute_portfolio_state(50) == PortfolioState.AVAILABLE


def test_benchmark_readiness_indicator():
    """Verify benchmark readiness transitions at threshold MIN_BENCHMARK_WORKSPACES (2)."""
    readiness_0 = PortfolioStateService.get_benchmark_readiness(0)
    assert readiness_0["current_workspaces"] == 0
    assert readiness_0["required_workspaces"] == MIN_BENCHMARK_WORKSPACES
    assert readiness_0["status"] == "PENDING"
    assert readiness_0["benchmark_available"] is False

    readiness_1 = PortfolioStateService.get_benchmark_readiness(1)
    assert readiness_1["current_workspaces"] == 1
    assert readiness_1["status"] == "PENDING"
    assert readiness_1["benchmark_available"] is False

    readiness_2 = PortfolioStateService.get_benchmark_readiness(2)
    assert readiness_2["current_workspaces"] == 2
    assert readiness_2["status"] == "AVAILABLE"
    assert readiness_2["benchmark_available"] is True


def test_activation_checklist_dynamic_progress():
    """Verify dynamic evaluation of activation checklist without hardcoded progress percentages."""
    # 0 workspaces
    checklist_0 = PortfolioStateService.evaluate_activation_checklist(
        workspace_count=0,
        has_dataset=True,
        has_snapshot=False,
    )
    assert checklist_0["is_fully_activated"] is False
    assert checklist_0["completed_count"] == 1  # Only dataset available
    assert checklist_0["total_count"] == 6
    assert checklist_0["progress_ratio"] == 0.17

    # 1 workspace
    checklist_1 = PortfolioStateService.evaluate_activation_checklist(
        workspace_count=1,
        has_dataset=True,
        has_snapshot=True,
        has_kpi_analysis=True,
        has_diagnostics=True,
    )
    assert checklist_1["is_fully_activated"] is False
    assert checklist_1["completed_count"] == 4  # Dataset, Snapshot, KPI, Diagnostics
    assert checklist_1["progress_ratio"] == 0.67

    # 2 workspaces (Fully activated)
    checklist_2 = PortfolioStateService.evaluate_activation_checklist(
        workspace_count=2,
        has_dataset=True,
        has_snapshot=True,
        has_kpi_analysis=True,
        has_diagnostics=True,
    )
    assert checklist_2["is_fully_activated"] is True
    assert checklist_2["completed_count"] == 6
    assert checklist_2["progress_ratio"] == 1.00
