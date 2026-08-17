"""Snapshot Replay Engine for Phase 12.8: Historical State Reconstruction."""

from datetime import datetime, timezone
from typing import Any, Dict, Optional
from app.execution.constants import (
    SNAPSHOT_REPLAY_ENGINE_VERSION,
    SNAPSHOT_SCHEMA_VERSION,
    STRATEGIC_SNAPSHOT_METRIC_VERSION,
    SnapshotIntegrityStatus,
    verify_snapshot_checksum,
)
from app.execution.models.snapshot import (
    InitiativeSnapshot,
    PortfolioSnapshot,
    ProgramSnapshot,
)


class SnapshotReplayEngine:
    """
    Deterministic historical state reconstruction engine.
    Validates cryptographic payload checksums and schema compatibility for lossless state replay.
    """

    ENGINE_VERSION = SNAPSHOT_REPLAY_ENGINE_VERSION
    SNAPSHOT_METRIC_VERSION = STRATEGIC_SNAPSHOT_METRIC_VERSION

    @classmethod
    def reconstruct_portfolio_state(
        cls,
        snapshot: PortfolioSnapshot,
    ) -> Dict[str, Any]:
        """Reconstructs lossless portfolio execution, outcome, and ranking state from a PortfolioSnapshot."""
        now = datetime.now(timezone.utc)
        payload = snapshot.snapshot_payload or {}

        # 1. Cryptographic Checksum Integrity Validation
        integrity_status = verify_snapshot_checksum(payload, snapshot.snapshot_checksum)

        # 2. Schema compatibility check
        schema_ver = getattr(snapshot, "snapshot_schema_version", None) or SNAPSHOT_SCHEMA_VERSION
        is_compatible = schema_ver.split(".")[0] == SNAPSHOT_SCHEMA_VERSION.split(".")[0]

        # 3. Structure reconstructed state
        reconstructed = {
            "snapshot_id": snapshot.id,
            "organization_id": snapshot.organization_id,
            "parent_snapshot_id": snapshot.parent_snapshot_id,
            "snapshot_date": snapshot.snapshot_date,
            "snapshot_timestamp": snapshot.snapshot_timestamp,
            "is_baseline_snapshot": snapshot.is_baseline_snapshot,
            "snapshot_schema_version": schema_ver,
            "schema_compatible": is_compatible,
            "snapshot_checksum": snapshot.snapshot_checksum,
            "snapshot_integrity_status": integrity_status,
            "last_integrity_verified_at": now,
            "generation_status": snapshot.generation_status,
            "capture_duration_ms": snapshot.capture_duration_ms,
            "scores": {
                "health_score": snapshot.portfolio_health_score,
                "risk_score": snapshot.portfolio_risk_score,
                "governance_score": snapshot.portfolio_governance_score,
                "outcome_attainment_rate": snapshot.portfolio_outcome_attainment_rate,
                "outcomes_achieved_rate": snapshot.portfolio_outcomes_achieved_rate,
                "benefit_realization_rate": snapshot.portfolio_benefit_realization_rate,
                "roi_score": snapshot.portfolio_roi_score,
                "roi_percentage": snapshot.portfolio_roi_percentage,
                "strategic_maturity_score": snapshot.portfolio_strategic_maturity_score,
                "value_realization_efficiency": snapshot.portfolio_value_realization_efficiency,
                "dependency_exposure_score": snapshot.portfolio_dependency_exposure_score,
                "concentration_risk_score": snapshot.portfolio_concentration_risk_score,
                "attention_score": snapshot.portfolio_attention_score,
                "completeness_score": snapshot.snapshot_completeness_score,
                "coverage_rate": snapshot.snapshot_coverage_rate,
                "quality_level": snapshot.snapshot_quality_level,
            },
            "source_counts": {
                "initiatives": snapshot.source_initiative_count,
                "programs": snapshot.source_program_count,
                "outcomes": snapshot.source_outcome_count,
                "benefits": snapshot.source_benefit_count,
                "risks": snapshot.source_risk_count,
                "milestones": snapshot.source_milestone_count,
            },
            "reconstructed_state": payload,
            "reconstructed_at": now,
        }

        return reconstructed

    @classmethod
    def reconstruct_program_state(
        cls,
        snapshot: ProgramSnapshot,
    ) -> Dict[str, Any]:
        """Reconstructs program execution state from a ProgramSnapshot."""
        now = datetime.now(timezone.utc)
        payload = snapshot.snapshot_payload or {}

        integrity_status = verify_snapshot_checksum(payload, snapshot.snapshot_checksum)
        schema_ver = getattr(snapshot, "snapshot_schema_version", None) or SNAPSHOT_SCHEMA_VERSION

        return {
            "snapshot_id": snapshot.id,
            "program_id": snapshot.program_id,
            "organization_id": snapshot.organization_id,
            "parent_snapshot_id": snapshot.parent_snapshot_id,
            "snapshot_date": snapshot.snapshot_date,
            "snapshot_timestamp": snapshot.snapshot_timestamp,
            "is_baseline_snapshot": snapshot.is_baseline_snapshot,
            "snapshot_schema_version": schema_ver,
            "snapshot_checksum": snapshot.snapshot_checksum,
            "snapshot_integrity_status": integrity_status,
            "last_integrity_verified_at": now,
            "scores": {
                "health_score": snapshot.program_health_score,
                "risk_score": snapshot.program_risk_score,
                "governance_score": snapshot.program_governance_score,
                "outcome_score": snapshot.program_outcome_score,
                "roi_score": snapshot.program_roi_score,
                "maturity_score": snapshot.program_maturity_score,
                "completeness_score": snapshot.snapshot_completeness_score,
                "coverage_rate": snapshot.snapshot_coverage_rate,
                "quality_level": snapshot.snapshot_quality_level,
            },
            "source_counts": {
                "initiatives": snapshot.source_initiative_count,
                "milestones": snapshot.source_milestone_count,
                "outcomes": snapshot.source_outcome_count,
            },
            "reconstructed_state": payload,
            "reconstructed_at": now,
        }

    @classmethod
    def reconstruct_initiative_state(
        cls,
        snapshot: InitiativeSnapshot,
    ) -> Dict[str, Any]:
        """Reconstructs initiative execution state from an InitiativeSnapshot."""
        now = datetime.now(timezone.utc)
        payload = snapshot.snapshot_payload or {}

        integrity_status = verify_snapshot_checksum(payload, snapshot.snapshot_checksum)
        schema_ver = getattr(snapshot, "snapshot_schema_version", None) or SNAPSHOT_SCHEMA_VERSION

        return {
            "snapshot_id": snapshot.id,
            "initiative_id": snapshot.initiative_id,
            "organization_id": snapshot.organization_id,
            "parent_snapshot_id": snapshot.parent_snapshot_id,
            "snapshot_date": snapshot.snapshot_date,
            "snapshot_timestamp": snapshot.snapshot_timestamp,
            "is_baseline_snapshot": snapshot.is_baseline_snapshot,
            "snapshot_schema_version": schema_ver,
            "snapshot_checksum": snapshot.snapshot_checksum,
            "snapshot_integrity_status": integrity_status,
            "last_integrity_verified_at": now,
            "scores": {
                "health_score": snapshot.initiative_health_score,
                "risk_score": snapshot.initiative_risk_score,
                "outcome_score": snapshot.initiative_outcome_score,
                "benefit_score": snapshot.initiative_benefit_score,
                "roi_score": snapshot.initiative_roi_score,
                "alignment_score": snapshot.initiative_alignment_score,
                "attention_score": snapshot.initiative_attention_score,
                "completeness_score": snapshot.snapshot_completeness_score,
                "coverage_rate": snapshot.snapshot_coverage_rate,
                "quality_level": snapshot.snapshot_quality_level,
            },
            "source_counts": {
                "milestones": snapshot.source_milestone_count,
                "outcomes": snapshot.source_outcome_count,
                "benefits": snapshot.source_benefit_count,
            },
            "reconstructed_state": payload,
            "reconstructed_at": now,
        }
