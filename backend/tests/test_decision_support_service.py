"""Integration tests for Phase 12.9 DecisionSupportService."""

import uuid
import pytest
from app.execution.models.initiative import StrategicInitiative
from app.execution.models.program import StrategicProgram
from app.execution.models.snapshot import StrategicPortfolioSnapshot
from app.execution.services.decision_support_service import DecisionSupportService


@pytest.mark.anyio
async def test_decision_support_service_end_to_end(db_session):
    """Tests service layer end-to-end multi-domain aggregation, decision generation, and balance intelligence."""
    org_id = uuid.uuid4()
    service = DecisionSupportService(db_session)

    # 1. Create a program and initiative in DB
    prog = StrategicProgram(
        id=uuid.uuid4(),
        organization_id=org_id,
        title="Enterprise Modernization",
        description="Modernization Roadmap",
    )
    db_session.add(prog)
    db_session.commit()

    init = StrategicInitiative(
        id=uuid.uuid4(),
        organization_id=org_id,
        program_id=prog.id,
        title="Core Platform Migration",
        description="Migrate legacy core",
        objective="Improve uptime to 99.99%",
        budget_allocated=400000.0,
        budget_spent=200000.0,
        execution_health_score=85.0,
    )
    db_session.add(init)
    db_session.commit()

    # 2. Get Executive Decision Support
    res = await service.get_executive_decision_support(org_id)
    assert res.organization_id == org_id
    assert len(res.executive_actions) >= 1
    assert len(res.investment_priorities) >= 1
    assert res.portfolio_balance_metrics is not None
    assert res.decision_readiness_score > 0.0
    assert res.portfolio_actionability_score > 0.0
    assert res.decision_engine_version == "1.0"
    assert res.investment_engine_version == "1.0"
    assert res.balance_engine_version == "1.0"
    assert res.intervention_engine_version == "1.0"

    # 3. Get Executive Actions
    actions = await service.get_executive_actions(org_id)
    assert len(actions) >= 1
    assert actions[0].decision_driver_coverage_pct == 100.0
    assert len(actions[0].decision_drivers) == 6

    # 4. Get Investment Priorities
    investments = await service.get_investment_priorities(org_id)
    assert len(investments) >= 1
    assert investments[0].expected_value_score > 0.0

    # 5. Get Portfolio Balance
    balance = await service.get_portfolio_balance(org_id)
    assert balance.portfolio_balance_score > 0.0

    # 6. Get Intervention Queue
    queue = await service.get_intervention_queue(org_id)
    assert queue.organization_id == org_id
    assert queue.total_interventions >= 0
