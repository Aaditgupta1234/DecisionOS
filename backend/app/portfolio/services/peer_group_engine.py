"""Peer Group Cohort Engine for Phase 11.1: Portfolio Benchmarking."""

import statistics
from typing import Dict, List, Optional, Tuple

from app.portfolio.constants import MIN_BENCHMARK_WORKSPACES
from app.portfolio.constants.benchmark_constants import PeerGroup
from app.portfolio.schemas.benchmark import (
    PeerGroupSummaryResponse,
    WorkspaceBenchmarkDetailResponse,
)


class PeerGroupEngine:
    """
    Constructs performance peer group cohorts, evaluates cohort averages and medians,
    and builds structured cohort breakdown summaries.
    """

    PEER_GROUP_ORDER: List[PeerGroup] = [
        PeerGroup.TOP_PERFORMERS,
        PeerGroup.HIGH_PERFORMERS,
        PeerGroup.MID_PERFORMERS,
        PeerGroup.UNDERPERFORMERS,
        PeerGroup.CRITICAL_ATTENTION,
    ]

    @classmethod
    def group_workspaces_into_cohorts(
        cls, workspaces: List[WorkspaceBenchmarkDetailResponse]
    ) -> Dict[PeerGroup, List[WorkspaceBenchmarkDetailResponse]]:
        """
        Group workspace detail objects into their respective PeerGroup cohorts.
        Guarantees all 5 peer groups are present in the returned dictionary.
        """
        cohort_map: Dict[PeerGroup, List[WorkspaceBenchmarkDetailResponse]] = {
            group: [] for group in cls.PEER_GROUP_ORDER
        }

        for ws in workspaces:
            if ws.peer_group in cohort_map:
                cohort_map[ws.peer_group].append(ws)

        # Ensure each cohort is sorted descending by health score, then rank
        for group in cohort_map:
            cohort_map[group].sort(key=lambda w: (-w.health_score, w.rank, w.workspace_name))

        return cohort_map

    @classmethod
    def build_peer_group_summaries(
        cls,
        cohort_map: Dict[PeerGroup, List[WorkspaceBenchmarkDetailResponse]],
        total_portfolio_workspaces: int,
    ) -> List[PeerGroupSummaryResponse]:
        """
        Constructs executive PeerGroupSummaryResponse objects for each of the 5 cohorts.
        """
        summaries: List[PeerGroupSummaryResponse] = []

        for group in cls.PEER_GROUP_ORDER:
            members = cohort_map.get(group, [])
            count = len(members)
            
            # Peer group comparisons are statistically valid when the cohort has >= MIN_BENCHMARK_WORKSPACES
            # and the total portfolio has >= MIN_BENCHMARK_WORKSPACES
            avail = (count >= MIN_BENCHMARK_WORKSPACES and total_portfolio_workspaces >= MIN_BENCHMARK_WORKSPACES)

            avg_score: Optional[float] = None
            med_score: Optional[float] = None
            best_ws: Optional[WorkspaceBenchmarkDetailResponse] = None
            worst_ws: Optional[WorkspaceBenchmarkDetailResponse] = None

            if count > 0:
                scores = [w.health_score for w in members]
                avg_score = round(float(statistics.mean(scores)), 1)
                med_score = round(float(statistics.median(scores)), 1)
                best_ws = members[0]
                worst_ws = members[-1]

            summary = PeerGroupSummaryResponse(
                peer_group=group,
                workspace_count=count,
                cohort_size=count,
                peer_group_available=avail,
                average_health_score=avg_score,
                median_health_score=med_score,
                best_workspace=best_ws,
                worst_workspace=worst_ws,
                workspaces=members,
            )
            summaries.append(summary)

        return summaries

    @staticmethod
    def compute_cohort_metrics(
        members: List[WorkspaceBenchmarkDetailResponse],
    ) -> Tuple[Optional[float], Optional[float], float]:
        """
        Calculates arithmetic mean, median, and max-min spread for a list of cohort members.
        """
        if not members:
            return None, None, 0.0

        scores = [w.health_score for w in members]
        avg = round(float(statistics.mean(scores)), 1)
        med = round(float(statistics.median(scores)), 1)
        spread = round(float(max(scores) - min(scores)), 1)
        return avg, med, spread
