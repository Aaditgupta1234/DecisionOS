"""Dashboard Snapshot Builder for Phase 9.6 Executive Dashboard."""

import hashlib
import json
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from app.dashboard.constants import (
    AVAILABLE_SECTIONS_DEFAULT,
    QUESTION_GENERATION_VERSION,
    SNAPSHOT_VERSION,
    WORKSPACE_VERSION,
)
from app.dashboard.read_model import DashboardReadModel
from app.dashboard.repositories.dashboard_query_repository import DashboardQueryRepository
from app.models.dataset import Dataset


class DashboardSnapshotBuilder:
    """
    Builds the complete serialized workspace_json payload from verified repository artifacts,
    computes SHA256 snapshot_hash for no-op detection, and records build telemetry.
    """

    def __init__(self, query_repo: DashboardQueryRepository):
        self.query_repo = query_repo

    async def build(
        self, dataset_id: uuid.UUID
    ) -> Tuple[Dict[str, Any], Dict[str, Any], str, uuid.UUID, float, int, int]:
        """
        Executes parallel artifact queries and assembles workspace_json.

        Returns:
            (workspace_json, artifact_versions, snapshot_hash, workspace_generation_id, build_time_ms, snapshot_size_bytes, artifact_count)
        """
        start_time = time.perf_counter()
        workspace_generation_id = uuid.uuid4()

        # 1. Fetch all artifacts from query repository
        dataset = await self.query_repo.get_dataset(dataset_id)
        if not dataset:
            raise ValueError(f"Dataset {dataset_id} not found")

        metrics = await self.query_repo.get_metrics(dataset_id)
        findings = await self.query_repo.get_findings(dataset_id)
        root_causes = await self.query_repo.get_root_causes(dataset_id)
        recommendations = await self.query_repo.get_recommendations(dataset_id)
        forecasts = await self.query_repo.get_forecasts(dataset_id)
        scenarios = await self.query_repo.get_scenarios(dataset_id)
        narratives = await self.query_repo.get_narratives(dataset_id)
        insight_report = await self.query_repo.get_executive_insights(dataset_id)
        reports = await self.query_repo.get_reports(dataset_id)
        chat_sessions = await self.query_repo.get_chat_sessions(dataset_id)

        artifact_count = (
            len(metrics)
            + len(findings)
            + len(root_causes)
            + len(recommendations)
            + len(forecasts)
            + len(scenarios)
            + len(narratives)
            + (1 if insight_report else 0)
            + len(reports)
        )

        # 2. Build domain sections via ReadModel
        kpis_data = DashboardReadModel.build_kpis(metrics)
        findings_data = DashboardReadModel.build_findings(findings)
        root_causes_data = DashboardReadModel.build_root_causes(root_causes)
        recs_data = DashboardReadModel.build_recommendations(recommendations)
        forecasts_data = DashboardReadModel.build_forecasts(forecasts)
        scenarios_data = DashboardReadModel.build_scenarios(scenarios)
        narratives_data = DashboardReadModel.build_narratives(narratives)
        insights_data = DashboardReadModel.build_insights(insight_report)
        reports_data = DashboardReadModel.build_reports_summary(reports)

        suggested_questions = DashboardReadModel.build_suggested_questions(
            findings=findings,
            recommendations=recommendations,
            forecasts=forecasts,
        )

        chat_data = {
            "session_count": len(chat_sessions),
            "last_message_at": chat_sessions[0].updated_at.isoformat() if chat_sessions and chat_sessions[0].updated_at else None,
            "suggested_questions": suggested_questions,
        }

        overview_data = DashboardReadModel.build_overview(
            dataset=dataset,
            metrics=metrics,
            findings=findings,
            root_causes=root_causes,
            recommendations=recommendations,
            forecasts=forecasts,
            scenarios=scenarios,
            reports=reports,
            insight_report=insight_report,
        )

        # 3. Assemble complete workspace_json
        workspace_json = {
            "overview": overview_data,
            "kpis": kpis_data,
            "findings": findings_data,
            "root_causes": root_causes_data,
            "recommendations": recs_data,
            "forecasts": forecasts_data,
            "scenarios": scenarios_data,
            "narratives": narratives_data,
            "insights": insights_data,
            "reports": reports_data,
            "chat": chat_data,
        }

        # 4. Assemble artifact_versions provenance map
        artifact_versions = {
            "dataset_id": str(dataset_id),
            "insight_report_id": str(insight_report.id) if insight_report else None,
            "narrative_ids": [str(n.id) for n in narratives],
            "forecast_ids": [str(f.id) for f in forecasts],
            "scenario_ids": [str(s.id) for s in scenarios],
            "report_export_ids": [str(r.id) for r in reports],
            "metric_ids": [str(m.id) for m in metrics],
            "finding_ids": [str(f.id) for f in findings],
            "root_cause_ids": [str(rc.id) for rc in root_causes],
            "recommendation_ids": [str(r.id) for r in recommendations],
        }

        # 5. Compute SHA256 snapshot_hash from pure business intelligence state
        from app.dashboard.hash_projection_builder import HashProjectionBuilder
        canonical_state = HashProjectionBuilder.canonical_json(workspace_json)
        snapshot_hash = hashlib.sha256(canonical_state.encode("utf-8")).hexdigest()
        raw_serialized = json.dumps(workspace_json, sort_keys=True, default=str)
        snapshot_size_bytes = len(raw_serialized.encode("utf-8"))

        build_time_ms = (time.perf_counter() - start_time) * 1000.0

        return (
            workspace_json,
            artifact_versions,
            snapshot_hash,
            workspace_generation_id,
            round(build_time_ms, 2),
            snapshot_size_bytes,
            artifact_count,
        )
