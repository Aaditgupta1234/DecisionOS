"""Unit tests for Phase 5.2A Enterprise Portfolio Intelligence."""

import uuid
import pytest
from app.portfolio.services.portfolio_health_engine import PortfolioHealthEngine
from app.portfolio.services.benchmarking_engine import CrossDatasetBenchmarkingEngine
from app.portfolio.services.department_scorecard_engine import DepartmentScorecardEngine
from app.portfolio.services.portfolio_summary_engine import PortfolioSummaryEngine


def test_portfolio_health_engine():
    """Test deterministic calculation of portfolio health and confidence."""
    portfolio_id = uuid.uuid4()
    bu_data = [
        {"id": uuid.uuid4(), "name": "E-Commerce", "health_score": 85.0, "weight": 0.6, "dataset_count": 2},
        {"id": uuid.uuid4(), "name": "Logistics", "health_score": 65.0, "weight": 0.4, "dataset_count": 1},
    ]

    res = PortfolioHealthEngine.calculate_health(portfolio_id, bu_data, data_quality_score=0.98)
    assert res.portfolio_id == portfolio_id
    assert res.overall_health_score == 77.0  # (85*0.6 + 65*0.4) = 51 + 26 = 77.0
    assert res.health_tier == "HEALTHY"
    assert res.confidence_score > 0.85
    assert len(res.sha256_hash) == 64


def test_cross_dataset_benchmarking_engine():
    """Test deterministic comparative gap analysis."""
    portfolio_id = uuid.uuid4()
    b_id = uuid.uuid4()
    t_id = uuid.uuid4()

    res = CrossDatasetBenchmarkingEngine.generate_benchmarks(
        portfolio_id,
        b_id,
        t_id,
        baseline_metrics={"Customer Retention Rate": 90.0, "Average Order Value (AOV)": 200.0},
        target_metrics={"Customer Retention Rate": 85.0, "Average Order Value (AOV)": 210.0},
    )

    assert res.portfolio_id == portfolio_id
    assert len(res.benchmarks) == 2
    retention_bm = next(b for b in res.benchmarks if b.metric_name == "Customer Retention Rate")
    assert retention_bm.baseline_value == 90.0
    assert retention_bm.target_value == 85.0
    assert retention_bm.gap_percentage == -5.6
    assert retention_bm.top_performer_dataset == "Baseline Dataset"


def test_department_scorecard_engine():
    """Test generation of functional department scorecards."""
    portfolio_id = uuid.uuid4()
    res = DepartmentScorecardEngine.generate_scorecards(portfolio_id)

    assert res.portfolio_id == portfolio_id
    assert len(res.scorecards) == 5
    dept_names = [d.department_name for d in res.scorecards]
    assert "Marketing & Growth" in dept_names
    assert "Logistics & Operations" in dept_names
    assert "Customer Success" in dept_names


def test_portfolio_summary_engine():
    """Test synthesis of Executive Portfolio Intelligence brief."""
    portfolio_id = uuid.uuid4()
    res = PortfolioSummaryEngine.generate_summary(portfolio_id)

    assert res.portfolio_id == portfolio_id
    assert res.overall_health == 74.0
    assert "Marketing" in res.strongest_unit
    assert "Logistics" in res.weakest_unit
    assert res.projected_arr_recovery == 480000.0
    assert len(res.board_directives) >= 3
    assert len(res.sha256_hash) == 64
