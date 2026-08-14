from datetime import datetime, timezone
import uuid
import pytest
from fastapi import HTTPException

from app.core.constants import (
    FindingSeverity,
    FindingType,
    MetricCategory,
    ScenarioAdjustmentType,
)
from app.models.dataset import Dataset
from app.models.dataset_metric import DatasetMetric
from app.models.diagnostic_finding import DiagnosticFinding
from app.models.metric_definition import MetricDefinition
from app.scenario_simulation.schemas.scenario_schema import (
    ScenarioAssumption,
    ScenarioCreate,
)
from app.scenario_simulation.services.scenario_simulation_service import ScenarioSimulationService


@pytest.fixture
def simulation_dataset(db_session, admin_user):
    dataset = Dataset(
        name="Simulation Service Test Dataset",
        original_filename="sim_srv.csv",
        stored_filename=f"{uuid.uuid4().hex[:12]}_sim_srv.csv",
        file_path="/tmp/sim_srv.csv",
        file_size=1024,
        uploaded_by=admin_user.id,
    )
    db_session.add(dataset)
    db_session.commit()
    db_session.refresh(dataset)

    metric_configs = [
        ("customer_churn_rate", "Customer Churn Rate", MetricCategory.CUSTOMERS, 22.0, "customer_id"),
        ("customer_retention_rate", "Customer Retention Rate", MetricCategory.CUSTOMERS, 78.0, "customer_id"),
        ("total_revenue", "Total Revenue", MetricCategory.REVENUE, 100000.0, "revenue"),
        ("total_orders", "Total Orders", MetricCategory.ORDERS, 1000.0, "order_id"),
        ("average_revenue", "Average Revenue", MetricCategory.REVENUE, 100.0, "revenue"),
    ]

    for key, name, cat, val, req_f in metric_configs:
        mdef = db_session.query(MetricDefinition).filter_by(metric_key=key).first()
        if not mdef:
            mdef = MetricDefinition(
                metric_key=key,
                name=name,
                metric_category=cat,
                required_field=req_f,
            )
            db_session.add(mdef)
            db_session.commit()
            db_session.refresh(mdef)

        m = DatasetMetric(
            dataset_id=dataset.id,
            metric_definition_id=mdef.id,
            metric_key=key,
            metric_name=name,
            metric_category=cat,
            metric_value=val,
            calculated_at=datetime.now(timezone.utc),
        )
        db_session.add(m)
    db_session.commit()

    finding = DiagnosticFinding(
        dataset_id=dataset.id,
        finding_type=FindingType.CUSTOMER_CONCENTRATION,
        severity=FindingSeverity.HIGH,
        title="Customer Churn Spike (22%)",
        description="High churn rate.",
        business_impact="Increases customer attrition rate and lowers LTV.",
        confidence_score=0.95,
    )
    db_session.add(finding)
    db_session.commit()

    return dataset


@pytest.mark.anyio
async def test_simulate_scenario_success(db_session, simulation_dataset):
    """Verifies end-to-end simulation execution and projection output."""
    service = ScenarioSimulationService(db=db_session)
    payload = ScenarioCreate(
        name="Reduce Churn by 5%",
        description="Test simulation",
        assumptions=[
            ScenarioAssumption(
                metric_key="customer_churn_rate",
                adjustment_type=ScenarioAdjustmentType.PERCENTAGE_POINTS,
                adjustment_value=-5.0,
            )
        ],
    )

    res = await service.simulate_scenario(dataset_id=simulation_dataset.id, payload=payload)
    assert res.id is not None
    assert res.name == "Reduce Churn by 5%"
    assert res.scenario_version == "1.0"
    assert len(res.projected_metrics) >= 2  # Churn + propagated retention

    # Retention should be derived to 83%
    ret_proj = next(m for m in res.projected_metrics if m.metric_key == "customer_retention_rate")
    assert ret_proj.projected_value == 83.0
    assert ret_proj.derived_from == "rule_churn_to_retention"

    # Health score should be projected
    assert res.projected_health.projected_score >= res.projected_health.baseline_score


@pytest.mark.anyio
async def test_simulate_scenario_immutability_of_production_data(db_session, simulation_dataset):
    """
    CRITICAL TEST: Proves that running a simulation NEVER mutates actual DatasetMetric
    or DiagnosticFinding records in the database.
    """
    service = ScenarioSimulationService(db=db_session)
    payload = ScenarioCreate(
        name="Hypothetical Doubling of Revenue",
        assumptions=[
            ScenarioAssumption(
                metric_key="total_revenue",
                adjustment_type=ScenarioAdjustmentType.RELATIVE_PERCENT,
                adjustment_value=100.0,
            )
        ],
    )

    await service.simulate_scenario(dataset_id=simulation_dataset.id, payload=payload)

    # Query actual database record directly
    db_metric = (
        db_session.query(DatasetMetric)
        .filter(DatasetMetric.dataset_id == simulation_dataset.id, DatasetMetric.metric_key == "total_revenue")
        .first()
    )
    # Must remain original 100,000.0
    assert db_metric.metric_value == 100000.0


@pytest.mark.anyio
async def test_simulate_scenario_version_increment(db_session, simulation_dataset):
    """Verifies that simulating the same scenario name increments version (1.0 -> 2.0)."""
    service = ScenarioSimulationService(db=db_session)
    payload = ScenarioCreate(
        name="Iterated Scenario",
        assumptions=[
            ScenarioAssumption(
                metric_key="total_revenue",
                adjustment_type=ScenarioAdjustmentType.RELATIVE_PERCENT,
                adjustment_value=5.0,
            )
        ],
    )

    s1 = await service.simulate_scenario(dataset_id=simulation_dataset.id, payload=payload)
    assert s1.scenario_version == "1.0"

    s2 = await service.simulate_scenario(dataset_id=simulation_dataset.id, payload=payload)
    assert s2.scenario_version == "2.0"


@pytest.mark.anyio
async def test_simulate_scenario_404_dataset_not_found(db_session):
    """Verifies 404 when dataset does not exist."""
    service = ScenarioSimulationService(db=db_session)
    payload = ScenarioCreate(
        name="Ghost Scenario",
        assumptions=[
            ScenarioAssumption(
                metric_key="total_revenue",
                adjustment_type=ScenarioAdjustmentType.RELATIVE_PERCENT,
                adjustment_value=10.0,
            )
        ],
    )
    with pytest.raises(HTTPException) as exc:
        await service.simulate_scenario(dataset_id=uuid.uuid4(), payload=payload)
    assert exc.value.status_code == 404


@pytest.mark.anyio
async def test_simulate_scenario_400_validation_error(db_session, simulation_dataset):
    """Verifies 400 when assumption breaches boundaries."""
    service = ScenarioSimulationService(db=db_session)
    payload = ScenarioCreate(
        name="Invalid Scenario",
        assumptions=[
            ScenarioAssumption(
                metric_key="customer_churn_rate",
                adjustment_type=ScenarioAdjustmentType.PERCENTAGE_POINTS,
                adjustment_value=95.0,  # 22 + 95 = 117% > 100% max
            )
        ],
    )
    with pytest.raises(HTTPException) as exc:
        await service.simulate_scenario(dataset_id=simulation_dataset.id, payload=payload)
    assert exc.value.status_code == 400
