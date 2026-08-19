"""Unit tests for Phase 6.5 Enterprise Strategy Execution, Value Realization & Executive Accountability Platform."""

import uuid
import pytest
from app.strategy_execution.services.strategy_execution_engine import StrategyExecutionEngine
from app.strategy_execution.services.dependency_intelligence_engine import DependencyIntelligenceEngine
from app.strategy_execution.services.benefits_realization_engine import BenefitsRealizationEngine
from app.strategy_execution.services.forecast_calibration_engine import ForecastCalibrationEngine
from app.strategy_execution.services.outcome_attribution_engine import OutcomeAttributionEngine
from app.strategy_execution.services.executive_accountability_engine import ExecutiveAccountabilityEngine
from app.strategy_execution.services.executive_performance_engine import ExecutivePerformanceEngine
from app.strategy_execution.services.strategy_review_engine import StrategyReviewEngine


def test_initiative_lifecycle_and_versioning():
    """Test initiative portfolio aggregation and sample retrieval."""
    portfolio_id = uuid.uuid4()
    summary = StrategyExecutionEngine.get_portfolio_initiatives_summary(portfolio_id)

    assert summary["total_initiatives"] == 42
    assert summary["active_initiatives"] == 28
    assert summary["completed_initiatives"] == 10
    assert summary["at_risk_initiatives"] == 4
    assert summary["aggregate_realized_arr"] == 2500000.0

    inits = StrategyExecutionEngine.get_sample_initiatives(portfolio_id)
    assert len(inits) == 3
    assert inits[0].initiative_code == "INIT-2026-001"
    assert inits[0].status == "IN_PROGRESS"


def test_dependency_graph_and_critical_path():
    """Test dependency DAG construction and critical path analysis."""
    portfolio_id = uuid.uuid4()
    cp = DependencyIntelligenceEngine.get_critical_path(portfolio_id)

    assert len(cp.critical_path_initiative_ids) == 3
    assert cp.total_duration_days == 135
    assert cp.blockers_count == 1
    assert len(cp.dag_nodes) == 3
    assert len(cp.dag_edges) == 2


def test_benefits_realization_portfolio_and_initiative():
    """Test portfolio and initiative value realization scores."""
    portfolio_id = uuid.uuid4()
    initiative_id = uuid.uuid4()

    port_val = BenefitsRealizationEngine.get_portfolio_value_realization(portfolio_id)
    assert port_val.forecast_arr == 2800000.0
    assert port_val.actual_arr == 2500000.0
    assert port_val.realization_score == 89.3

    init_val = BenefitsRealizationEngine.get_initiative_realization_report(initiative_id)
    assert init_val.forecast_arr == 124000.0
    assert init_val.actual_arr == 118000.0
    assert init_val.realization_score == 95.2


def test_automatic_forecast_calibration_engine():
    """Test forecast calibration metrics and error analysis."""
    portfolio_id = uuid.uuid4()
    initiative_id = uuid.uuid4()

    rec = ForecastCalibrationEngine.get_forecast_accuracy(initiative_id)
    assert rec.forecast_value == 124000.0
    assert rec.actual_value == 118000.0
    assert rec.accuracy_pct == 95.2

    calib = ForecastCalibrationEngine.get_portfolio_calibration_metrics(portfolio_id)
    assert calib["mean_accuracy_pct"] == 95.2
    assert calib["mape"] == 0.048
    assert calib["calibration_status"] == "CALIBRATED_STABLE"


def test_outcome_attribution_and_evidence():
    """Test explainable outcome attribution chain."""
    initiative_id = uuid.uuid4()
    attr = OutcomeAttributionEngine.get_initiative_attribution_chain(initiative_id)

    assert len(attr["attribution_chain"]) == 5
    assert attr["attribution_chain"][0]["stage"] == "INITIATIVE"
    assert attr["attribution_chain"][1]["stage"] == "RECOMMENDATION"
    assert attr["attribution_chain"][2]["stage"] == "ROOT_CAUSE"
    assert attr["attribution_chain"][3]["stage"] == "KPI_MOVEMENT"
    assert attr["attribution_chain"][4]["stage"] == "ARR_OUTCOME"
    assert len(attr["evidence_citations"]) == 3


def test_executive_accountability_and_scores():
    """Test executive decision ledger and composite accountability score formula."""
    portfolio_id = uuid.uuid4()
    ledger = ExecutiveAccountabilityEngine.get_executive_decision_ledger(portfolio_id)
    assert len(ledger) == 3
    assert ledger[0].approver_role == "COO"

    score = ExecutiveAccountabilityEngine.calculate_accountability_score(
        forecast_accuracy=94.8,
        value_realization=95.2,
        success_rate=87.0,
        risk_compliance=95.0,
    )
    assert score >= 90.0


def test_executive_performance_and_reviews():
    """Test leadership scorecards and strategy review cycles."""
    portfolio_id = uuid.uuid4()

    profiles = ExecutivePerformanceEngine.get_executive_performance_profiles(portfolio_id)
    assert len(profiles) == 3
    assert profiles[0].role == "CFO"
    assert profiles[0].accountability_score >= 90.0

    reviews = StrategyReviewEngine.get_review_cycles(portfolio_id)
    assert len(reviews) == 2
    assert "Q4 Enterprise Strategy Review" in reviews[0].review_name
    assert len(reviews[0].lessons_learned) >= 2
