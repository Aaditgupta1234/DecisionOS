"""Portfolio Aggregation Service for Phase 11.0: Portfolio Intelligence Foundation."""

import statistics
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from app.portfolio.constants import (
    DEGRADED_HEALTH_SCORE,
    HEALTHY_HEALTH_SCORE,
    MIN_BENCHMARK_WORKSPACES,
    PORTFOLIO_VERSION,
    PortfolioStatus,
)
from app.portfolio.repositories.portfolio_repository import PortfolioRepository
from app.portfolio.services.health_extractor import WorkspaceHealthExtractor


@dataclass
class WorkspaceDataPoint:
    """Normalized internal data point representing a single workspace's operational telemetry."""
    workspace_id: uuid.UUID
    workspace_name: str
    health_score: float
    finding_count: int = 0
    critical_finding_count: int = 0
    recommendation_count: int = 0
    forecast_confidence: Optional[float] = None
    last_snapshot_at: Optional[datetime] = None
    snapshot_age_seconds: Optional[float] = None


class PortfolioAggregationService:
    """
    Collects verified intelligence outputs from individual workspaces across an organization,
    aggregates KPIs, health scores, and diagnostics, and builds portfolio-level summaries.
    """

    def __init__(self, repo: PortfolioRepository) -> None:
        self.repo = repo

    async def collect_workspace_data(
        self, organization_id: uuid.UUID
    ) -> Tuple[List[WorkspaceDataPoint], int]:
        """
        Queries all datasets in the organization, checks for their latest READY dashboard snapshot,
        and parses intelligence telemetry via WorkspaceHealthExtractor.

        Returns:
            (analyzed_data_points, total_workspace_count)
        """
        datasets = await self.repo.get_datasets_for_org(organization_id)
        total_workspace_count = len(datasets)

        data_points: List[WorkspaceDataPoint] = []
        now_utc = datetime.now(timezone.utc)

        for dataset in datasets:
            snapshot = await self.repo.get_latest_ready_snapshot_for_dataset(dataset.id)
            if not snapshot or not snapshot.workspace_json:
                continue

            health_score = WorkspaceHealthExtractor.extract(snapshot.workspace_json)
            stats = WorkspaceHealthExtractor.extract_statistics(snapshot.workspace_json)

            snapshot_age = None
            if snapshot.generated_at:
                gen_at = snapshot.generated_at
                if gen_at.tzinfo is None:
                    gen_at = gen_at.replace(tzinfo=timezone.utc)
                snapshot_age = max(0.0, (now_utc - gen_at).total_seconds())

            dp = WorkspaceDataPoint(
                workspace_id=dataset.id,
                workspace_name=dataset.name,
                health_score=health_score,
                finding_count=stats.get("finding_count", 0),
                critical_finding_count=stats.get("critical_finding_count", 0),
                recommendation_count=stats.get("recommendation_count", 0),
                forecast_confidence=stats.get("forecast_confidence"),
                last_snapshot_at=snapshot.generated_at,
                snapshot_age_seconds=snapshot_age,
            )
            data_points.append(dp)

        return data_points, total_workspace_count

    @staticmethod
    def calculate_average_health(data_points: List[WorkspaceDataPoint]) -> Optional[float]:
        """Calculate arithmetic mean of health scores across analyzed workspaces."""
        if not data_points:
            return None
        scores = [dp.health_score for dp in data_points]
        return round(float(statistics.mean(scores)), 1)

    @staticmethod
    def calculate_median_health(data_points: List[WorkspaceDataPoint]) -> Optional[float]:
        """Calculate median health score across analyzed workspaces."""
        if not data_points:
            return None
        scores = [dp.health_score for dp in data_points]
        return round(float(statistics.median(scores)), 1)

    @staticmethod
    def identify_best_workspace(
        data_points: List[WorkspaceDataPoint],
    ) -> Optional[WorkspaceDataPoint]:
        """Find the workspace with the highest health score (first in tie-breaker)."""
        if not data_points:
            return None
        return max(data_points, key=lambda dp: dp.health_score)

    @staticmethod
    def identify_worst_workspace(
        data_points: List[WorkspaceDataPoint],
    ) -> Optional[WorkspaceDataPoint]:
        """Find the workspace with the lowest health score."""
        if not data_points:
            return None
        return min(data_points, key=lambda dp: dp.health_score)

    @staticmethod
    def determine_portfolio_status(
        average_health: Optional[float],
        analyzed_count: int,
        total_critical_findings: int = 0,
    ) -> PortfolioStatus:
        """
        Determine deterministic PortfolioStatus based on score thresholds and critical findings.
        """
        if analyzed_count == 0 or average_health is None:
            return PortfolioStatus.INSUFFICIENT_DATA

        if average_health >= HEALTHY_HEALTH_SCORE and total_critical_findings == 0:
            return PortfolioStatus.HEALTHY
        elif average_health >= DEGRADED_HEALTH_SCORE or (average_health >= HEALTHY_HEALTH_SCORE and total_critical_findings > 0):
            return PortfolioStatus.DEGRADED
        else:
            return PortfolioStatus.CRITICAL
