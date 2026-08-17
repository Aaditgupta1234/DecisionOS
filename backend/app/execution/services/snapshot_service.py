import json
import time
import uuid
from datetime import date, datetime, timezone
from typing import Any, Dict, List, Optional, Tuple, Union
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.execution.constants import (
    SNAPSHOT_ENGINE_VERSION,
    SNAPSHOT_SCHEMA_VERSION,
    STRATEGIC_SNAPSHOT_METRIC_VERSION,
    SnapshotChangeSeverity,
    SnapshotGenerationStatus,
    SnapshotIntegrityStatus,
    SnapshotQualityLevel,
    SnapshotRetentionCategory,
    SnapshotTriggerSource,
    TrendDirection,
    calculate_change_severity,
    calculate_snapshot_checksum,
    calculate_snapshot_completeness,
    calculate_snapshot_coverage_rate,
    calculate_snapshot_quality_level,
    calculate_trend_direction,
    verify_snapshot_checksum,
)
from app.execution.models.initiative import StrategicInitiative
from app.execution.models.program import StrategicProgram
from app.execution.models.snapshot import (
    InitiativeSnapshot,
    PortfolioSnapshot,
    ProgramSnapshot,
)
from app.execution.repositories.benefit_repository import BenefitRealizationRepository
from app.execution.repositories.dependency_repository import DependencyRepository
from app.execution.repositories.governance_review_repository import GovernanceReviewRepository
from app.execution.repositories.initiative_repository import InitiativeFilterParams, InitiativeRepository
from app.execution.repositories.milestone_repository import MilestoneRepository
from app.execution.repositories.outcome_repository import OutcomeMeasurementRepository
from app.execution.repositories.program_repository import ProgramRepository
from app.execution.repositories.snapshot_repository import SnapshotRepository
from app.execution.schemas.snapshot import (
    CreateInitiativeSnapshotRequest,
    CreatePortfolioSnapshotRequest,
    CreateProgramSnapshotRequest,
    HistoricalAttentionMetrics,
    HistoricalConcentrationMetrics,
    InitiativeReplayResponse,
    InitiativeSnapshotHistoryResponse,
    InitiativeSnapshotResponse,
    MetricDeltaItem,
    PortfolioEvolutionMetrics,
    PortfolioReplayResponse,
    PortfolioSnapshotHistoryResponse,
    PortfolioSnapshotResponse,
    ProgramReplayResponse,
    ProgramSnapshotHistoryResponse,
    ProgramSnapshotResponse,
    SnapshotComparisonResponse,
    TimeseriesAnalyticsMetrics,
)
from app.execution.services.historical_trend_engine import HistoricalTrendEngine
from app.execution.services.portfolio_evolution_engine import PortfolioEvolutionEngine
from app.execution.services.snapshot_replay_engine import SnapshotReplayEngine
from app.execution.services.strategic_analytics_service import StrategicAnalyticsService
from app.execution.services.timeseries_analytics_engine import TimeseriesAnalyticsEngine


class SnapshotService:
    """Multi-tenant orchestration service for snapshot persistence, replay, comparison, and time-series intelligence."""

    def __init__(self, db: Union[AsyncSession, Session]) -> None:
        self.db = db
        self.snapshot_repo = SnapshotRepository(db)
        self.initiative_repo = InitiativeRepository(db)
        self.program_repo = ProgramRepository(db)
        self.milestone_repo = MilestoneRepository(db)
        self.outcome_repo = OutcomeMeasurementRepository(db)
        self.benefit_repo = BenefitRealizationRepository(db)
        self.governance_repo = GovernanceReviewRepository(db)
        self.dependency_repo = DependencyRepository(db)
        self.analytics_service = StrategicAnalyticsService(db)

    # -------------------------------------------------------------------------
    # Portfolio Snapshots
    # -------------------------------------------------------------------------

    async def create_portfolio_snapshot(
        self,
        organization_id: uuid.UUID,
        request: Optional[CreatePortfolioSnapshotRequest] = None,
        user_id: Optional[uuid.UUID] = None,
    ) -> PortfolioSnapshotResponse:
        """Captures an immutable, lossless point-in-time snapshot of the entire portfolio state."""
        start_time = time.perf_counter()
        req = request or CreatePortfolioSnapshotRequest()
        now = datetime.now(timezone.utc)
        today = date.today()

        # 1. Fetch current cross-domain intelligence
        try:
            port_analytics = await self.analytics_service.get_portfolio_analytics(organization_id)
            port_diag = await self.analytics_service.get_portfolio_diagnostics(organization_id)
            port_rankings = await self.analytics_service.get_portfolio_rankings(organization_id, limit=50)
            exec_attention = await self.analytics_service.get_executive_attention_queue(organization_id)
            gen_status = SnapshotGenerationStatus.SUCCESS
        except Exception:
            gen_status = SnapshotGenerationStatus.PARTIAL
            port_analytics = None
            port_diag = None
            port_rankings = None
            exec_attention = None

        # 2. Extract entities for counts and coverage
        filters = InitiativeFilterParams(limit=1000)
        initiatives, total_inits = await self.initiative_repo.list(organization_id, filters)
        programs = await self.program_repo.list_by_organization(organization_id)
        outcomes = await self.outcome_repo.list_outcomes(organization_id=organization_id)
        benefits = await self.benefit_repo.list_benefits(organization_id=organization_id)
        reviews = await self.governance_repo.list_reviews(organization_id=organization_id)

        source_init_count = len(initiatives)
        source_prog_count = len(programs)
        source_outcome_count = len(outcomes)
        source_benefit_count = len(benefits)
        source_risk_count = sum(1 for i in initiatives if getattr(i, "risk_score", 0.0) > 40.0)
        source_milestone_count = 0
        for i in initiatives:
            ms = await self.milestone_repo.list_by_initiative(i.id, organization_id)
            source_milestone_count += len(ms)

        captured_entities = (
            source_init_count
            + source_prog_count
            + source_outcome_count
            + source_benefit_count
            + source_risk_count
            + source_milestone_count
        )
        expected_entities = max(1, captured_entities)
        coverage_rate = calculate_snapshot_coverage_rate(captured_entities, expected_entities)

        # 3. Extract core metrics
        metrics = port_analytics.metrics if port_analytics else None
        h_score = float(metrics.strategic_value_score if metrics else 100.0)
        r_score = float(max(0.0, 100.0 - (metrics.execution_health_component if metrics else 100.0)))
        gov_score = float(metrics.governance_maturity_component if metrics else 100.0)
        out_rate = float(metrics.outcome_achievement_component if metrics else 0.0)
        ben_rate = float(metrics.benefit_realization_component if metrics else 0.0)
        roi_sc = float(metrics.roi_score_component if metrics else 0.0)
        mat_score = float(port_analytics.portfolio_strategic_maturity_score if port_analytics else 0.0)
        val_eff = float(metrics.value_efficiency_score if metrics else 0.0)

        diag_data = port_diag.diagnostics if port_diag else None
        dep_score = float(
            getattr(diag_data.dependency_concentration, "single_point_of_failure_count", 0.0)
            if diag_data and hasattr(diag_data, "dependency_concentration")
            else 0.0
        )
        conc_score = float(
            getattr(diag_data.value_concentration, "top_10_percent_value_share", 0.0)
            if diag_data and hasattr(diag_data, "value_concentration")
            else 0.0
        )
        att_score = float(exec_attention.queue[0].attention_score if exec_attention and exec_attention.queue else 0.0)

        completeness_score = calculate_snapshot_completeness(
            populated_metrics=13 if gen_status == SnapshotGenerationStatus.SUCCESS else 8,
            expected_metrics=13,
        )
        quality_level = calculate_snapshot_quality_level(completeness_score)

        rankings_dump = port_rankings.model_dump(mode="json") if port_rankings else {}
        attention_dump = exec_attention.model_dump(mode="json") if exec_attention else {}
        diagnostics_dump = port_diag.model_dump(mode="json") if port_diag else {}

        deep_payload = {
            "organization_id": str(organization_id),
            "captured_at": now.isoformat(),
            "initiatives": [
                {
                    "id": str(i.id),
                    "title": i.title,
                    "status": i.status.value if hasattr(i.status, "value") else str(i.status),
                    "health_score": float(getattr(i, "execution_health_score", getattr(i, "health_score", 100.0)) or 100.0),
                    "budget_allocated": float(getattr(i, "budget_allocated", 0.0) or 0.0),
                    "budget_spent": float(getattr(i, "budget_spent", 0.0) or 0.0),
                }
                for i in initiatives
            ],
            "programs": [
                {
                    "id": str(p.id),
                    "title": p.title,
                    "status": p.status.value if hasattr(p.status, "value") else str(p.status),
                }
                for p in programs
            ],
            "rankings": rankings_dump,
            "attention_queue": attention_dump,
            "diagnostics": diagnostics_dump,
        }
        deep_payload = json.loads(json.dumps(deep_payload, default=str))

        checksum = calculate_snapshot_checksum(deep_payload)
        elapsed_ms = int((time.perf_counter() - start_time) * 1000)

        # 5. Build and persist model
        snapshot = PortfolioSnapshot(
            id=uuid.uuid4(),
            organization_id=organization_id,
            parent_snapshot_id=req.parent_snapshot_id,
            snapshot_date=today,
            snapshot_timestamp=now,
            is_baseline_snapshot=req.is_baseline_snapshot,
            snapshot_retention_category=req.snapshot_retention_category,
            snapshot_trigger_source=req.trigger_source,
            snapshot_created_by=user_id,
            generation_status=gen_status,
            capture_duration_ms=elapsed_ms,
            portfolio_health_score=h_score,
            portfolio_risk_score=r_score,
            portfolio_governance_score=gov_score,
            portfolio_outcome_attainment_rate=out_rate,
            portfolio_outcomes_achieved_rate=out_rate,
            portfolio_benefit_realization_rate=ben_rate,
            portfolio_roi_score=roi_sc,
            portfolio_roi_percentage=roi_sc,
            portfolio_strategic_maturity_score=mat_score,
            portfolio_value_realization_efficiency=val_eff,
            portfolio_dependency_exposure_score=dep_score,
            portfolio_concentration_risk_score=conc_score,
            portfolio_attention_score=att_score,
            snapshot_completeness_score=completeness_score,
            snapshot_coverage_rate=coverage_rate,
            snapshot_quality_level=quality_level,
            snapshot_checksum=checksum,
            last_integrity_verified_at=now,
            source_initiative_count=source_init_count,
            source_program_count=source_prog_count,
            source_outcome_count=source_outcome_count,
            source_benefit_count=source_benefit_count,
            source_risk_count=source_risk_count,
            source_milestone_count=source_milestone_count,
            snapshot_payload=deep_payload,
            snapshot_version=SNAPSHOT_ENGINE_VERSION,
            snapshot_schema_version=SNAPSHOT_SCHEMA_VERSION,
            metric_version="1.0",
            engine_version=SNAPSHOT_ENGINE_VERSION,
        )

        persisted = await self.snapshot_repo.create_portfolio_snapshot(snapshot)
        return self._to_portfolio_response(persisted, integrity_status=SnapshotIntegrityStatus.VALID)

    async def get_portfolio_snapshot(
        self,
        organization_id: uuid.UUID,
        snapshot_id: uuid.UUID,
    ) -> PortfolioSnapshotResponse:
        """Retrieves a portfolio snapshot by ID with cryptographic verification."""
        snap = await self.snapshot_repo.get_portfolio_snapshot_by_id(snapshot_id, organization_id)
        if not snap:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Portfolio Snapshot '{snapshot_id}' not found in organization scope.",
            )

        integrity = verify_snapshot_checksum(snap.snapshot_payload or {}, snap.snapshot_checksum)
        now = datetime.now(timezone.utc)
        await self.snapshot_repo.update_portfolio_snapshot_integrity(snap, now)
        return self._to_portfolio_response(snap, integrity_status=integrity)

    async def get_latest_portfolio_snapshot(
        self,
        organization_id: uuid.UUID,
    ) -> PortfolioSnapshotResponse:
        """Retrieves the latest portfolio snapshot or auto-generates if none exists."""
        snap = await self.snapshot_repo.get_latest_portfolio_snapshot(organization_id)
        if not snap:
            return await self.create_portfolio_snapshot(organization_id)
        integrity = verify_snapshot_checksum(snap.snapshot_payload or {}, snap.snapshot_checksum)
        return self._to_portfolio_response(snap, integrity_status=integrity)

    async def get_baseline_portfolio_snapshot(
        self,
        organization_id: uuid.UUID,
    ) -> PortfolioSnapshotResponse:
        """Retrieves the designated baseline portfolio snapshot."""
        snap = await self.snapshot_repo.get_baseline_portfolio_snapshot(organization_id)
        if not snap:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No designated baseline portfolio snapshot exists for organization '{organization_id}'.",
            )
        integrity = verify_snapshot_checksum(snap.snapshot_payload or {}, snap.snapshot_checksum)
        return self._to_portfolio_response(snap, integrity_status=integrity)

    async def list_portfolio_snapshots_history(
        self,
        organization_id: uuid.UUID,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        retention_category: Optional[SnapshotRetentionCategory] = None,
        trigger_source: Optional[SnapshotTriggerSource] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> PortfolioSnapshotHistoryResponse:
        """Lists historical snapshots accompanied by rolling time-series and portfolio evolution analytics."""
        snaps, total = await self.snapshot_repo.list_portfolio_snapshots(
            organization_id=organization_id,
            start_date=start_date,
            end_date=end_date,
            retention_category=retention_category,
            trigger_source=trigger_source,
            limit=limit,
            offset=offset,
        )

        # Convert to dicts for analytical engines (oldest first for time-series / evolution)
        snaps_dict = [self._snapshot_to_dict(s) for s in reversed(snaps)]

        timeseries_metrics = None
        evolution_metrics = None
        warnings: List[str] = []

        if snaps_dict:
            ts_res = TimeseriesAnalyticsEngine.calculate_timeseries_analytics(organization_id, snaps_dict)
            timeseries_metrics = TimeseriesAnalyticsMetrics(**ts_res)

            evo_res = PortfolioEvolutionEngine.calculate_portfolio_evolution(organization_id, snaps_dict)
            evolution_metrics = PortfolioEvolutionMetrics(**evo_res)
            warnings.extend(ts_res.get("data_quality_warnings", []))
            warnings.extend(evo_res.get("data_quality_warnings", []))
        else:
            warnings.append("No portfolio snapshots available in requested query range.")

        response_items = [self._to_portfolio_response(s) for s in snaps]
        return PortfolioSnapshotHistoryResponse(
            organization_id=organization_id,
            total_snapshots=total,
            snapshots=response_items,
            timeseries_analytics=timeseries_metrics,
            portfolio_evolution=evolution_metrics,
            data_quality_warnings=list(dict.fromkeys(warnings)),
        )

    # -------------------------------------------------------------------------
    # Program Snapshots
    # -------------------------------------------------------------------------

    async def create_program_snapshot(
        self,
        organization_id: uuid.UUID,
        program_id: uuid.UUID,
        request: Optional[CreateProgramSnapshotRequest] = None,
        user_id: Optional[uuid.UUID] = None,
    ) -> ProgramSnapshotResponse:
        """Captures a point-in-time snapshot of a strategic program."""
        start_time = time.perf_counter()
        req = request or CreateProgramSnapshotRequest()
        prog = await self.program_repo.get_by_id(program_id, organization_id)
        if not prog:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Strategic Program '{program_id}' not found.",
            )

        now = datetime.now(timezone.utc)
        prog_ana = await self.analytics_service.get_program_analytics(organization_id, program_id)
        m = prog_ana.metrics

        filters = InitiativeFilterParams(program_id=program_id, limit=500)
        inits, _ = await self.initiative_repo.list(organization_id, filters)
        ms_count = 0
        for i in inits:
            ms = await self.milestone_repo.list_by_initiative(i.id, organization_id)
            ms_count += len(ms)

        deep_payload = {
            "program_id": str(program_id),
            "title": prog.title,
            "captured_at": now.isoformat(),
            "initiatives": [{"id": str(i.id), "title": i.title} for i in inits],
        }
        deep_payload = json.loads(json.dumps(deep_payload, default=str))
        checksum = calculate_snapshot_checksum(deep_payload)
        elapsed_ms = int((time.perf_counter() - start_time) * 1000)

        snap = ProgramSnapshot(
            id=uuid.uuid4(),
            organization_id=organization_id,
            program_id=program_id,
            parent_snapshot_id=req.parent_snapshot_id,
            snapshot_date=date.today(),
            snapshot_timestamp=now,
            is_baseline_snapshot=req.is_baseline_snapshot,
            snapshot_retention_category=req.snapshot_retention_category,
            snapshot_trigger_source=SnapshotTriggerSource.MANUAL,
            snapshot_created_by=user_id,
            generation_status=SnapshotGenerationStatus.SUCCESS,
            capture_duration_ms=elapsed_ms,
            program_health_score=float(m.strategic_value_score if m else 100.0),
            program_risk_score=float(max(0.0, 100.0 - (m.execution_health_component if m else 100.0))),
            program_governance_score=float(m.governance_maturity_component if m else 100.0),
            program_outcome_score=float(m.outcome_achievement_component if m else 0.0),
            program_roi_score=float(m.roi_score_component if m else 0.0),
            program_maturity_score=float(m.governance_maturity_component if m else 0.0),
            snapshot_completeness_score=100.0,
            snapshot_coverage_rate=100.0,
            snapshot_quality_level=SnapshotQualityLevel.EXCELLENT,
            snapshot_checksum=checksum,
            last_integrity_verified_at=now,
            source_initiative_count=len(inits),
            source_milestone_count=ms_count,
            source_outcome_count=len(inits),
            snapshot_payload=deep_payload,
        )
        persisted = await self.snapshot_repo.create_program_snapshot(snap)
        return self._to_program_response(persisted, integrity_status=SnapshotIntegrityStatus.VALID)

    async def get_program_snapshot(
        self,
        organization_id: uuid.UUID,
        program_id: uuid.UUID,
    ) -> ProgramSnapshotHistoryResponse:
        """Retrieves history of snapshots for a program."""
        snaps = await self.snapshot_repo.list_program_snapshots(program_id, organization_id)
        if not snaps:
            # Auto-create initial snapshot
            init_snap = await self.create_program_snapshot(organization_id, program_id)
            return ProgramSnapshotHistoryResponse(
                program_id=program_id,
                organization_id=organization_id,
                total_snapshots=1,
                snapshots=[init_snap],
            )
        items = [self._to_program_response(s) for s in snaps]
        return ProgramSnapshotHistoryResponse(
            program_id=program_id,
            organization_id=organization_id,
            total_snapshots=len(items),
            snapshots=items,
        )

    # -------------------------------------------------------------------------
    # Initiative Snapshots
    # -------------------------------------------------------------------------

    async def create_initiative_snapshot(
        self,
        organization_id: uuid.UUID,
        initiative_id: uuid.UUID,
        request: Optional[CreateInitiativeSnapshotRequest] = None,
        user_id: Optional[uuid.UUID] = None,
    ) -> InitiativeSnapshotResponse:
        """Captures a point-in-time snapshot of an initiative."""
        start_time = time.perf_counter()
        req = request or CreateInitiativeSnapshotRequest()
        init = await self.initiative_repo.get_by_id(initiative_id, organization_id)
        if not init:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Strategic Initiative '{initiative_id}' not found.",
            )

        now = datetime.now(timezone.utc)
        init_ana = await self.analytics_service.get_initiative_analytics(organization_id, initiative_id)
        m = init_ana.metrics

        ms = await self.milestone_repo.list_by_initiative(initiative_id, organization_id)
        outs = await self.outcome_repo.list_outcomes(organization_id=organization_id, initiative_id=initiative_id)
        bens = await self.benefit_repo.list_benefits(organization_id=organization_id, initiative_id=initiative_id)

        deep_payload = {
            "initiative_id": str(initiative_id),
            "title": init.title,
            "captured_at": now.isoformat(),
            "milestones": [{"id": str(x.id), "title": x.title} for x in ms],
            "outcomes": [{"id": str(x.id), "metric": x.target_metric} for x in outs],
            "benefits": [{"id": str(x.id), "type": x.benefit_type.value} for x in bens],
        }
        deep_payload = json.loads(json.dumps(deep_payload, default=str))
        checksum = calculate_snapshot_checksum(deep_payload)
        elapsed_ms = int((time.perf_counter() - start_time) * 1000)

        snap = InitiativeSnapshot(
            id=uuid.uuid4(),
            organization_id=organization_id,
            initiative_id=initiative_id,
            parent_snapshot_id=req.parent_snapshot_id,
            snapshot_date=date.today(),
            snapshot_timestamp=now,
            is_baseline_snapshot=req.is_baseline_snapshot,
            snapshot_retention_category=req.snapshot_retention_category,
            snapshot_trigger_source=SnapshotTriggerSource.MANUAL,
            snapshot_created_by=user_id,
            generation_status=SnapshotGenerationStatus.SUCCESS,
            capture_duration_ms=elapsed_ms,
            initiative_health_score=float(m.strategic_value_score if m else 100.0),
            initiative_risk_score=float(max(0.0, 100.0 - (m.execution_health_component if m else 100.0))),
            initiative_outcome_score=float(m.outcome_achievement_component if m else 0.0),
            initiative_benefit_score=float(m.benefit_realization_component if m else 0.0),
            initiative_roi_score=float(m.roi_score_component if m else 0.0),
            initiative_alignment_score=float(m.strategic_alignment_score if m else 100.0),
            initiative_attention_score=float(m.strategic_confidence_score if m else 0.0),
            snapshot_completeness_score=100.0,
            snapshot_coverage_rate=100.0,
            snapshot_quality_level=SnapshotQualityLevel.EXCELLENT,
            snapshot_checksum=checksum,
            last_integrity_verified_at=now,
            source_milestone_count=len(ms),
            source_outcome_count=len(outs),
            source_benefit_count=len(bens),
            snapshot_payload=deep_payload,
        )
        persisted = await self.snapshot_repo.create_initiative_snapshot(snap)
        return self._to_initiative_response(persisted, integrity_status=SnapshotIntegrityStatus.VALID)

    async def get_initiative_snapshot(
        self,
        organization_id: uuid.UUID,
        initiative_id: uuid.UUID,
    ) -> InitiativeSnapshotHistoryResponse:
        """Retrieves history of snapshots for an initiative."""
        snaps = await self.snapshot_repo.list_initiative_snapshots(initiative_id, organization_id)
        if not snaps:
            init_snap = await self.create_initiative_snapshot(organization_id, initiative_id)
            return InitiativeSnapshotHistoryResponse(
                initiative_id=initiative_id,
                organization_id=organization_id,
                total_snapshots=1,
                snapshots=[init_snap],
            )
        items = [self._to_initiative_response(s) for s in snaps]
        return InitiativeSnapshotHistoryResponse(
            initiative_id=initiative_id,
            organization_id=organization_id,
            total_snapshots=len(items),
            snapshots=items,
        )

    # -------------------------------------------------------------------------
    # Replay
    # -------------------------------------------------------------------------

    async def replay_portfolio_snapshot(
        self,
        organization_id: uuid.UUID,
        snapshot_id: uuid.UUID,
    ) -> PortfolioReplayResponse:
        """Reconstructs exact historical state from a PortfolioSnapshot."""
        snap = await self.snapshot_repo.get_portfolio_snapshot_by_id(snapshot_id, organization_id)
        if not snap:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Portfolio Snapshot '{snapshot_id}' not found.",
            )
        res = SnapshotReplayEngine.reconstruct_portfolio_state(snap)
        return PortfolioReplayResponse(
            snapshot_id=snap.id,
            organization_id=snap.organization_id,
            parent_snapshot_id=snap.parent_snapshot_id,
            snapshot_date=snap.snapshot_date,
            snapshot_timestamp=snap.snapshot_timestamp,
            is_baseline_snapshot=snap.is_baseline_snapshot,
            snapshot_schema_version=res["snapshot_schema_version"],
            snapshot_checksum=snap.snapshot_checksum,
            snapshot_integrity_status=res["snapshot_integrity_status"],
            last_integrity_verified_at=res["last_integrity_verified_at"],
            reconstructed_state=res["reconstructed_state"],
            reconstructed_at=res["reconstructed_at"],
        )

    async def replay_program_snapshot(
        self,
        organization_id: uuid.UUID,
        snapshot_id: uuid.UUID,
    ) -> ProgramReplayResponse:
        """Reconstructs program historical state."""
        snap = await self.snapshot_repo.get_program_snapshot_by_id(snapshot_id, organization_id)
        if not snap:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Program Snapshot '{snapshot_id}' not found.",
            )
        res = SnapshotReplayEngine.reconstruct_program_state(snap)
        return ProgramReplayResponse(
            snapshot_id=snap.id,
            program_id=snap.program_id,
            organization_id=snap.organization_id,
            parent_snapshot_id=snap.parent_snapshot_id,
            snapshot_date=snap.snapshot_date,
            snapshot_timestamp=snap.snapshot_timestamp,
            is_baseline_snapshot=snap.is_baseline_snapshot,
            snapshot_schema_version=res["snapshot_schema_version"],
            snapshot_checksum=snap.snapshot_checksum,
            snapshot_integrity_status=res["snapshot_integrity_status"],
            last_integrity_verified_at=res["last_integrity_verified_at"],
            reconstructed_state=res["reconstructed_state"],
            reconstructed_at=res["reconstructed_at"],
        )

    async def replay_initiative_snapshot(
        self,
        organization_id: uuid.UUID,
        snapshot_id: uuid.UUID,
    ) -> InitiativeReplayResponse:
        """Reconstructs initiative historical state."""
        snap = await self.snapshot_repo.get_initiative_snapshot_by_id(snapshot_id, organization_id)
        if not snap:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Initiative Snapshot '{snapshot_id}' not found.",
            )
        res = SnapshotReplayEngine.reconstruct_initiative_state(snap)
        return InitiativeReplayResponse(
            snapshot_id=snap.id,
            initiative_id=snap.initiative_id,
            organization_id=snap.organization_id,
            parent_snapshot_id=snap.parent_snapshot_id,
            snapshot_date=snap.snapshot_date,
            snapshot_timestamp=snap.snapshot_timestamp,
            is_baseline_snapshot=snap.is_baseline_snapshot,
            snapshot_schema_version=res["snapshot_schema_version"],
            snapshot_checksum=snap.snapshot_checksum,
            snapshot_integrity_status=res["snapshot_integrity_status"],
            last_integrity_verified_at=res["last_integrity_verified_at"],
            reconstructed_state=res["reconstructed_state"],
            reconstructed_at=res["reconstructed_at"],
        )

    # -------------------------------------------------------------------------
    # Differential Snapshot Comparison
    # -------------------------------------------------------------------------

    async def compare_snapshots(
        self,
        organization_id: uuid.UUID,
        snapshot_a_id: Optional[uuid.UUID] = None,
        snapshot_b_id: Optional[uuid.UUID] = None,
        baseline_compare: bool = False,
    ) -> SnapshotComparisonResponse:
        """
        Calculates deterministic differential deltas between two snapshots or against baseline.
        Snapshot A is the baseline/older snapshot, Snapshot B is the comparison/newer snapshot.
        """
        now = datetime.now(timezone.utc)
        warnings: List[str] = []

        if baseline_compare or snapshot_a_id is None:
            snap_a = await self.snapshot_repo.get_baseline_portfolio_snapshot(organization_id)
            if not snap_a:
                # Fallback to oldest snapshot
                snaps, _ = await self.snapshot_repo.list_portfolio_snapshots(organization_id, limit=1)
                snap_a = snaps[0] if snaps else None
        else:
            snap_a = await self.snapshot_repo.get_portfolio_snapshot_by_id(snapshot_a_id, organization_id)

        if snapshot_b_id is None:
            snap_b = await self.snapshot_repo.get_latest_portfolio_snapshot(organization_id)
        else:
            snap_b = await self.snapshot_repo.get_portfolio_snapshot_by_id(snapshot_b_id, organization_id)

        if not snap_a or not snap_b:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Unable to resolve two portfolio snapshots for comparison.",
            )

        # Temporal guardrail
        period_days = abs((snap_b.snapshot_date - snap_a.snapshot_date).days)
        if period_days < 7:
            warnings.append(f"Short comparison period ({period_days} days). Percentage movements may reflect short-term noise.")

        # Metric deltas evaluation
        metric_specs = [
            ("Portfolio Health Score", snap_a.portfolio_health_score, snap_b.portfolio_health_score, True, True),
            ("Portfolio Risk Score", snap_a.portfolio_risk_score, snap_b.portfolio_risk_score, False, True),
            ("Portfolio Governance Score", snap_a.portfolio_governance_score, snap_b.portfolio_governance_score, True, False),
            ("Portfolio Outcome Attainment", snap_a.portfolio_outcome_attainment_rate, snap_b.portfolio_outcome_attainment_rate, True, True),
            ("Portfolio Benefit Realization", snap_a.portfolio_benefit_realization_rate, snap_b.portfolio_benefit_realization_rate, True, False),
            ("Portfolio ROI Score", snap_a.portfolio_roi_score, snap_b.portfolio_roi_score, True, True),
            ("Portfolio Strategic Maturity", snap_a.portfolio_strategic_maturity_score, snap_b.portfolio_strategic_maturity_score, True, False),
            ("Portfolio Value Realization Efficiency", snap_a.portfolio_value_realization_efficiency, snap_b.portfolio_value_realization_efficiency, True, False),
            ("Portfolio Concentration Risk", snap_a.portfolio_concentration_risk_score, snap_b.portfolio_concentration_risk_score, False, True),
            ("Portfolio Executive Attention", snap_a.portfolio_attention_score, snap_b.portfolio_attention_score, False, True),
        ]

        metric_deltas: List[MetricDeltaItem] = []
        trend_changes: Dict[str, TrendDirection] = {}

        for name, val_a, val_b, higher_better, is_crit in metric_specs:
            abs_d = round(val_b - val_a, 2)
            if abs(val_a) > 1e-6:
                pct_d = round(((val_b - val_a) / abs(val_a)) * 100.0, 2)
            else:
                pct_d = 100.0 if val_b > 0 else (0.0 if val_b == 0 else -100.0)

            t_dir = calculate_trend_direction(pct_d, higher_is_better=higher_better)
            sev = calculate_change_severity(pct_d, is_critical_metric=is_crit)

            metric_deltas.append(
                MetricDeltaItem(
                    metric_name=name,
                    snapshot_a_value=val_a,
                    snapshot_b_value=val_b,
                    absolute_delta=abs_d,
                    percentage_delta=pct_d,
                    trend_direction=t_dir,
                    change_severity=sev,
                )
            )
            trend_changes[name] = t_dir

        return SnapshotComparisonResponse(
            snapshot_a_id=snap_a.id,
            snapshot_b_id=snap_b.id,
            snapshot_a_date=snap_a.snapshot_date,
            snapshot_b_date=snap_b.snapshot_date,
            comparison_period_days=period_days,
            metric_deltas=metric_deltas,
            trend_changes=trend_changes,
            maturity_changes={
                "strategic_maturity_delta": round(snap_b.portfolio_strategic_maturity_score - snap_a.portfolio_strategic_maturity_score, 2),
                "governance_score_delta": round(snap_b.portfolio_governance_score - snap_a.portfolio_governance_score, 2),
            },
            risk_changes={
                "risk_score_delta": round(snap_b.portfolio_risk_score - snap_a.portfolio_risk_score, 2),
                "dependency_exposure_delta": round(snap_b.portfolio_dependency_exposure_score - snap_a.portfolio_dependency_exposure_score, 2),
            },
            roi_changes={
                "roi_score_delta": round(snap_b.portfolio_roi_score - snap_a.portfolio_roi_score, 2),
                "benefit_realization_delta": round(snap_b.portfolio_benefit_realization_rate - snap_a.portfolio_benefit_realization_rate, 2),
            },
            concentration_changes={
                "concentration_risk_delta": round(snap_b.portfolio_concentration_risk_score - snap_a.portfolio_concentration_risk_score, 2),
            },
            attention_changes={
                "attention_score_delta": round(snap_b.portfolio_attention_score - snap_a.portfolio_attention_score, 2),
            },
            data_quality_warnings=warnings,
            compared_at=now,
        )

    # -------------------------------------------------------------------------
    # Helper Mappers
    # -------------------------------------------------------------------------

    def _to_portfolio_response(
        self,
        snap: PortfolioSnapshot,
        integrity_status: SnapshotIntegrityStatus = SnapshotIntegrityStatus.NOT_VERIFIED,
    ) -> PortfolioSnapshotResponse:
        return PortfolioSnapshotResponse(
            id=snap.id,
            organization_id=snap.organization_id,
            parent_snapshot_id=snap.parent_snapshot_id,
            snapshot_date=snap.snapshot_date,
            snapshot_timestamp=snap.snapshot_timestamp,
            is_baseline_snapshot=snap.is_baseline_snapshot,
            snapshot_retention_category=snap.snapshot_retention_category,
            snapshot_trigger_source=snap.snapshot_trigger_source,
            snapshot_created_by=snap.snapshot_created_by,
            generation_status=snap.generation_status,
            capture_duration_ms=snap.capture_duration_ms,
            portfolio_health_score=snap.portfolio_health_score,
            portfolio_risk_score=snap.portfolio_risk_score,
            portfolio_governance_score=snap.portfolio_governance_score,
            portfolio_outcome_attainment_rate=snap.portfolio_outcome_attainment_rate,
            portfolio_outcomes_achieved_rate=snap.portfolio_outcomes_achieved_rate,
            portfolio_benefit_realization_rate=snap.portfolio_benefit_realization_rate,
            portfolio_roi_score=snap.portfolio_roi_score,
            portfolio_roi_percentage=snap.portfolio_roi_percentage,
            portfolio_strategic_maturity_score=snap.portfolio_strategic_maturity_score,
            portfolio_value_realization_efficiency=snap.portfolio_value_realization_efficiency,
            portfolio_dependency_exposure_score=snap.portfolio_dependency_exposure_score,
            portfolio_concentration_risk_score=snap.portfolio_concentration_risk_score,
            portfolio_attention_score=snap.portfolio_attention_score,
            snapshot_completeness_score=snap.snapshot_completeness_score,
            snapshot_coverage_rate=snap.snapshot_coverage_rate,
            snapshot_quality_level=snap.snapshot_quality_level,
            snapshot_checksum=snap.snapshot_checksum,
            snapshot_integrity_status=integrity_status,
            last_integrity_verified_at=snap.last_integrity_verified_at,
            source_initiative_count=snap.source_initiative_count,
            source_program_count=snap.source_program_count,
            source_outcome_count=snap.source_outcome_count,
            source_benefit_count=snap.source_benefit_count,
            source_risk_count=snap.source_risk_count,
            source_milestone_count=snap.source_milestone_count,
            snapshot_version=snap.snapshot_version,
            snapshot_schema_version=snap.snapshot_schema_version,
            metric_version=snap.metric_version,
            engine_version=snap.engine_version,
            created_at=snap.created_at,
        )

    def _to_program_response(
        self,
        snap: ProgramSnapshot,
        integrity_status: SnapshotIntegrityStatus = SnapshotIntegrityStatus.NOT_VERIFIED,
    ) -> ProgramSnapshotResponse:
        return ProgramSnapshotResponse(
            id=snap.id,
            organization_id=snap.organization_id,
            program_id=snap.program_id,
            parent_snapshot_id=snap.parent_snapshot_id,
            snapshot_date=snap.snapshot_date,
            snapshot_timestamp=snap.snapshot_timestamp,
            is_baseline_snapshot=snap.is_baseline_snapshot,
            snapshot_retention_category=snap.snapshot_retention_category,
            snapshot_trigger_source=snap.snapshot_trigger_source,
            snapshot_created_by=snap.snapshot_created_by,
            generation_status=snap.generation_status,
            capture_duration_ms=snap.capture_duration_ms,
            program_health_score=snap.program_health_score,
            program_risk_score=snap.program_risk_score,
            program_governance_score=snap.program_governance_score,
            program_outcome_score=snap.program_outcome_score,
            program_roi_score=snap.program_roi_score,
            program_maturity_score=snap.program_maturity_score,
            snapshot_completeness_score=snap.snapshot_completeness_score,
            snapshot_coverage_rate=snap.snapshot_coverage_rate,
            snapshot_quality_level=snap.snapshot_quality_level,
            snapshot_checksum=snap.snapshot_checksum,
            snapshot_integrity_status=integrity_status,
            last_integrity_verified_at=snap.last_integrity_verified_at,
            source_initiative_count=snap.source_initiative_count,
            source_milestone_count=snap.source_milestone_count,
            source_outcome_count=snap.source_outcome_count,
            snapshot_version=snap.snapshot_version,
            snapshot_schema_version=snap.snapshot_schema_version,
            metric_version=snap.metric_version,
            engine_version=snap.engine_version,
            created_at=snap.created_at,
        )

    def _to_initiative_response(
        self,
        snap: InitiativeSnapshot,
        integrity_status: SnapshotIntegrityStatus = SnapshotIntegrityStatus.NOT_VERIFIED,
    ) -> InitiativeSnapshotResponse:
        return InitiativeSnapshotResponse(
            id=snap.id,
            organization_id=snap.organization_id,
            initiative_id=snap.initiative_id,
            parent_snapshot_id=snap.parent_snapshot_id,
            snapshot_date=snap.snapshot_date,
            snapshot_timestamp=snap.snapshot_timestamp,
            is_baseline_snapshot=snap.is_baseline_snapshot,
            snapshot_retention_category=snap.snapshot_retention_category,
            snapshot_trigger_source=snap.snapshot_trigger_source,
            snapshot_created_by=snap.snapshot_created_by,
            generation_status=snap.generation_status,
            capture_duration_ms=snap.capture_duration_ms,
            initiative_health_score=snap.initiative_health_score,
            initiative_risk_score=snap.initiative_risk_score,
            initiative_outcome_score=snap.initiative_outcome_score,
            initiative_benefit_score=snap.initiative_benefit_score,
            initiative_roi_score=snap.initiative_roi_score,
            initiative_alignment_score=snap.initiative_alignment_score,
            initiative_attention_score=snap.initiative_attention_score,
            snapshot_completeness_score=snap.snapshot_completeness_score,
            snapshot_coverage_rate=snap.snapshot_coverage_rate,
            snapshot_quality_level=snap.snapshot_quality_level,
            snapshot_checksum=snap.snapshot_checksum,
            snapshot_integrity_status=integrity_status,
            last_integrity_verified_at=snap.last_integrity_verified_at,
            source_milestone_count=snap.source_milestone_count,
            source_outcome_count=snap.source_outcome_count,
            source_benefit_count=snap.source_benefit_count,
            snapshot_version=snap.snapshot_version,
            snapshot_schema_version=snap.snapshot_schema_version,
            metric_version=snap.metric_version,
            engine_version=snap.engine_version,
            created_at=snap.created_at,
        )

    def _snapshot_to_dict(self, s: PortfolioSnapshot) -> Dict[str, Any]:
        return {
            "id": s.id,
            "snapshot_date": s.snapshot_date,
            "snapshot_timestamp": s.snapshot_timestamp,
            "created_at": s.created_at,
            "portfolio_health_score": s.portfolio_health_score,
            "portfolio_risk_score": s.portfolio_risk_score,
            "portfolio_governance_score": s.portfolio_governance_score,
            "portfolio_outcome_attainment_rate": s.portfolio_outcome_attainment_rate,
            "portfolio_roi_score": s.portfolio_roi_score,
            "portfolio_strategic_maturity_score": s.portfolio_strategic_maturity_score,
            "portfolio_attention_score": s.portfolio_attention_score,
            "top_10_percent_value_share": s.portfolio_concentration_risk_score,
            "top_20_percent_value_share": s.portfolio_concentration_risk_score * 1.3,
            "herfindahl_index": s.portfolio_concentration_risk_score * 30.0,
            "portfolio_dependency_exposure_score": s.portfolio_dependency_exposure_score,
        }
