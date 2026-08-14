"""ScenarioSimulationService orchestrating validation, direct projections, explicit propagation, and persistence."""

import logging
from typing import Any, Dict, List, Optional, Set, Union
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.core.constants import ScenarioStatus
from app.models.dataset import Dataset
from app.models.scenario import Scenario
from app.scenario_simulation.constants import (
    DEFAULT_SCENARIO_LIMITATIONS,
    DEFAULT_SCENARIO_VERSION,
)
from app.scenario_simulation.engines.health_projection_engine import HealthProjectionEngine
from app.scenario_simulation.engines.metric_projection_engine import (
    MetricBoundaryError,
    MetricProjectionEngine,
)
from app.scenario_simulation.engines.scenario_comparison_engine import ScenarioComparisonEngine
from app.scenario_simulation.engines.scenario_rule_registry import ScenarioRuleRegistry
from app.scenario_simulation.repositories.scenario_repository import ScenarioRepository
from app.scenario_simulation.schemas.scenario_schema import (
    ScenarioAssumption,
    ScenarioComparisonResponse,
    ScenarioCreate,
    ScenarioHealthProjection,
    ScenarioHistoryResponse,
    ScenarioMetricProjection,
    ScenarioResponse,
)
from app.scenario_simulation.validators.scenario_validator import (
    ScenarioValidationError,
    ScenarioValidator,
)
from app.services.intelligence_service import IntelligenceService

logger = logging.getLogger(__name__)


class ScenarioSimulationService:
    """
    Service layer executing deterministic what-if scenario simulations,
    enforcing dataset isolation, and preserving immutability of production intelligence.
    """

    def __init__(self, db: Union[AsyncSession, Session]):
        self.db = db
        self.repo = ScenarioRepository(db)
        self.intel_service = IntelligenceService(db)
        self.rule_registry = ScenarioRuleRegistry()

    def _is_async(self) -> bool:
        return isinstance(self.db, AsyncSession)

    async def _validate_dataset_exists(self, dataset_id: UUID) -> Dataset:
        """Ensures the dataset exists and is active."""
        stmt = select(Dataset).where(Dataset.id == dataset_id, Dataset.is_deleted == False)
        if self._is_async():
            res = await self.db.execute(stmt)
        else:
            res = self.db.execute(stmt)
        dataset = res.scalar_one_or_none()
        if not dataset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Dataset '{dataset_id}' not found",
            )
        return dataset

    def _map_to_response(self, scenario: Scenario) -> ScenarioResponse:
        """Maps ORM model to Pydantic ScenarioResponse."""
        h_data = scenario.projected_health
        health_proj = ScenarioHealthProjection(
            baseline_score=h_data.get("baseline_score", 0),
            projected_score=h_data.get("projected_score", 0),
            score_delta=h_data.get("score_delta", 0),
            baseline_status=h_data.get("baseline_status", "WATCH_LIST"),
            projected_status=h_data.get("projected_status", "WATCH_LIST"),
            status_changed=h_data.get("status_changed", False),
        )

        assumptions_list = [
            ScenarioAssumption(
                metric_key=a["metric_key"],
                adjustment_type=a["adjustment_type"],
                adjustment_value=a["adjustment_value"],
            )
            for a in scenario.assumptions
        ]

        proj_metrics_list = [
            ScenarioMetricProjection(**m)
            for m in scenario.projected_metrics
        ]

        return ScenarioResponse(
            id=scenario.id,
            dataset_id=scenario.dataset_id,
            scenario_version=scenario.scenario_version,
            name=scenario.name,
            description=scenario.description,
            status=scenario.status,
            assumptions=assumptions_list,
            baseline_snapshot=scenario.baseline_snapshot,
            projected_metrics=proj_metrics_list,
            projected_findings=scenario.projected_findings,
            projected_risks=scenario.projected_risks,
            projected_opportunities=scenario.projected_opportunities,
            projected_health=health_proj,
            limitations=scenario.limitations,
            metadata_info=scenario.metadata_info,
            created_at=scenario.created_at,
            updated_at=scenario.updated_at,
        )

    # -----------------------------------------------------------------------
    # Simulation Execution
    # -----------------------------------------------------------------------

    async def simulate_scenario(
        self,
        dataset_id: UUID,
        payload: ScenarioCreate,
    ) -> ScenarioResponse:
        """
        Executes a deterministic what-if scenario simulation:
        1. Validates dataset & baseline intelligence.
        2. Strictly validates assumptions & boundaries.
        3. Projects direct assumption metrics.
        4. Applies priority-ordered propagation rules.
        5. Re-evaluates diagnostic findings & recalculates health score (without unearned recovery bonuses).
        6. Persists the simulation record without mutating production data.
        """
        # 1. Validate Dataset
        await self._validate_dataset_exists(dataset_id)

        # 2. Load Deterministic Intelligence Report
        report = await self.intel_service.get_intelligence_report(dataset_id)

        # Extract baseline metrics lookup
        baseline_metrics: Dict[str, float] = {}
        metric_metadata: Dict[str, Dict[str, Any]] = {}
        for m in (report.metrics or []):
            k = m.get("metric_key") or m.get("name")
            val = float(m.get("current_value") if m.get("current_value") is not None else m.get("value", 0.0))
            if k:
                baseline_metrics[k] = val
                metric_metadata[k] = {
                    "name": m.get("name") or k,
                    "category": m.get("category", "general"),
                }

        # 3. Strict Deterministic Validation
        try:
            ScenarioValidator.validate_assumptions(
                assumptions=payload.assumptions,
                dataset_metrics=baseline_metrics,
            )
        except ScenarioValidationError as s_err:
            logger.warning(f"Scenario validation rejected: {s_err}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(s_err),
            )

        # 4. Baseline Snapshot
        exec_summary = report.executive_summary
        baseline_score = exec_summary.business_health_score
        baseline_status = exec_summary.business_health_status

        baseline_snapshot = {
            "metrics": dict(baseline_metrics),
            "health": {
                "score": baseline_score,
                "status": baseline_status.value if hasattr(baseline_status, "value") else str(baseline_status),
            },
            "findings_count": len(report.findings or []),
            "root_causes_count": len(report.root_causes or []),
        }

        # 5. Direct Metric Projections
        working_metrics = dict(baseline_metrics)
        directly_assumed_keys: Set[str] = set()

        for assumption in payload.assumptions:
            k = assumption.metric_key
            b_val = baseline_metrics[k]
            try:
                p_val = MetricProjectionEngine.project_value(
                    baseline_value=b_val,
                    adjustment_type=assumption.adjustment_type,
                    adjustment_value=assumption.adjustment_value,
                    metric_key=k,
                )
            except MetricBoundaryError as mb_err:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=str(mb_err),
                )
            working_metrics[k] = p_val
            directly_assumed_keys.add(k)

        # 6. Apply Dependency-Ordered Propagation Rules (Cycle-Protected)
        working_metrics, derived_sources = self.rule_registry.apply_propagation(
            current_metrics=working_metrics,
            directly_assumed_keys=directly_assumed_keys,
        )

        # 7. Build Metric Projection DTOs
        projected_metrics_list = []
        for k, p_val in working_metrics.items():
            b_val = baseline_metrics.get(k, p_val)
            abs_delta = round(p_val - b_val, 4)
            pct_delta = round((abs_delta / b_val * 100.0), 2) if b_val != 0.0 else 0.0
            meta = metric_metadata.get(k, {"name": k, "category": "general"})

            is_direct = k in directly_assumed_keys
            derived_by = derived_sources.get(k)

            # Include if modified or directly assumed
            if is_direct or derived_by or abs_delta != 0.0:
                projected_metrics_list.append({
                    "metric_key": k,
                    "metric_name": meta["name"],
                    "category": meta["category"],
                    "baseline_value": b_val,
                    "projected_value": p_val,
                    "absolute_delta": abs_delta,
                    "percentage_delta": pct_delta,
                    "is_direct_assumption": is_direct,
                    "derived_from": derived_by,
                })

        # 8. Re-evaluate Findings & Compute Isolated Health Score
        health_proj, proj_findings, proj_risks, proj_opportunities = (
            HealthProjectionEngine.project_health_and_diagnostics(
                baseline_health_score=baseline_score,
                baseline_health_status=baseline_status,
                baseline_findings=report.findings or [],
                baseline_root_causes=report.root_causes or [],
                baseline_metrics=baseline_metrics,
                projected_metrics=working_metrics,
            )
        )

        # 9. Determine Scenario Version
        latest = await self.repo.get_latest_by_dataset(dataset_id)
        if latest and latest.name.lower().strip() == payload.name.lower().strip():
            try:
                major_num = int(float(latest.scenario_version))
                next_version = f"{major_num + 1}.0"
            except ValueError:
                next_version = "2.0"
        else:
            next_version = DEFAULT_SCENARIO_VERSION

        # 10. Instantiate & Persist Scenario
        scenario = Scenario(
            dataset_id=dataset_id,
            scenario_version=next_version,
            name=payload.name,
            description=payload.description,
            status=ScenarioStatus.COMPLETED,
            assumptions=[a.model_dump() for a in payload.assumptions],
            baseline_snapshot=baseline_snapshot,
            projected_metrics=projected_metrics_list,
            projected_findings=proj_findings,
            projected_risks=proj_risks,
            projected_opportunities=proj_opportunities,
            projected_health=health_proj.model_dump(),
            limitations=DEFAULT_SCENARIO_LIMITATIONS,
            metadata_info={
                "assumptions_count": len(payload.assumptions),
                "propagated_metrics_count": len(derived_sources),
            },
        )

        persisted = await self.repo.create(scenario)

        if self._is_async():
            await self.db.commit()
        else:
            self.db.commit()

        return self._map_to_response(persisted)

    # -----------------------------------------------------------------------
    # Scenario Management & History
    # -----------------------------------------------------------------------

    async def get_scenario(self, scenario_id: UUID) -> ScenarioResponse:
        """Retrieves a specific scenario simulation by ID."""
        scenario = await self.repo.get_by_id(scenario_id)
        if not scenario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Scenario '{scenario_id}' not found",
            )
        return self._map_to_response(scenario)

    async def list_scenarios(
        self,
        dataset_id: UUID,
        limit: int = 10,
        offset: int = 0,
    ) -> ScenarioHistoryResponse:
        """Lists historical scenario simulations for a dataset."""
        await self._validate_dataset_exists(dataset_id)
        total_count = await self.repo.count_by_dataset(dataset_id)
        scenarios = await self.repo.list_history_by_dataset(
            dataset_id=dataset_id,
            limit=limit,
            offset=offset,
        )
        return ScenarioHistoryResponse(
            total_count=total_count,
            scenarios=[self._map_to_response(s) for s in scenarios],
        )

    async def compare_scenarios(
        self,
        dataset_id: UUID,
        scenario_ids: Optional[List[UUID]] = None,
    ) -> ScenarioComparisonResponse:
        """
        Synthesizes a side-by-side comparison matrix across multiple scenarios.
        Enforces strict dataset isolation: all scenario IDs must belong to the requested dataset.
        """
        await self._validate_dataset_exists(dataset_id)

        # 1. Fetch scenarios
        if scenario_ids and len(scenario_ids) > 0:
            scenarios = await self.repo.get_by_ids(dataset_id=dataset_id, scenario_ids=scenario_ids)
            # Strict dataset validation check:
            if len(scenarios) != len(scenario_ids):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="One or more specified scenario IDs do not exist or do not belong to the requested dataset.",
                )
        else:
            # Default to latest 5 scenarios for dataset
            scenarios = await self.repo.list_history_by_dataset(dataset_id=dataset_id, limit=5, offset=0)

        if not scenarios or len(scenarios) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No scenario simulations available for comparison on this dataset.",
            )

        # 2. Extract baseline snapshot from the first scenario
        baseline_snapshot = scenarios[0].baseline_snapshot

        # 3. Generate deterministic comparison matrix
        return ScenarioComparisonEngine.compare(
            dataset_id=dataset_id,
            baseline_snapshot=baseline_snapshot,
            scenarios=scenarios,
        )

    async def delete_scenario(self, scenario_id: UUID) -> bool:
        """Deletes a specific scenario simulation."""
        deleted = await self.repo.delete_by_id(scenario_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Scenario '{scenario_id}' not found",
            )
        if self._is_async():
            await self.db.commit()
        else:
            self.db.commit()
        return True
