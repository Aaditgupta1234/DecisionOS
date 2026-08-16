"""
Deterministic Critical Path Engine for Phase 12.3.7.
Calculates Directed Acyclic Graph (DAG) Critical Path, topological sequencing,
float/slack analysis, downstream delay propagation, and critical path stability scores (0-100).
"""

from collections import defaultdict, deque
from datetime import datetime, timezone
import uuid
from typing import Dict, List, Optional, Set, Tuple

from app.execution.constants import (
    CRITICAL_PATH_ENGINE_VERSION,
    MilestoneStatus,
)
from app.execution.models.milestone import InitiativeMilestone
from app.execution.models.milestone_dependency import MilestoneDependency
from app.execution.schemas.timeline import CriticalPathMetrics


class CriticalPathEngine:
    """Deterministic mathematical engine for DAG Critical Path Method (CPM) analytics."""

    @classmethod
    def calculate_critical_path(
        cls,
        milestones: List[InitiativeMilestone],
        dependencies: Optional[List[MilestoneDependency]] = None,
        as_of_date: Optional[datetime] = None,
    ) -> CriticalPathMetrics:
        """
        Computes the critical path, total slack, projected delay impact, and stability score.
        """
        now = as_of_date or datetime.now(timezone.utc)
        ms_list = milestones or []
        dep_list = dependencies or []

        if not ms_list:
            return CriticalPathMetrics(
                critical_path_length=0,
                critical_milestone_count=0,
                critical_initiative_count=0,
                critical_path_duration_days=0,
                projected_delay_days=0,
                critical_path_stability_score=100.0,
                critical_path_nodes=[],
                engine_version=CRITICAL_PATH_ENGINE_VERSION,
            )

        ms_map: Dict[uuid.UUID, InitiativeMilestone] = {m.id: m for m in ms_list}

        # 1. Calculate duration for each milestone
        durations: Dict[uuid.UUID, int] = {}
        for m in ms_list:
            dur = 7  # default standard milestone duration in days
            start_d = m.planned_start_date or m.baseline_start_date
            due_d = m.planned_due_date or m.due_date or m.baseline_due_date
            if start_d and due_d:
                s_dt = start_d if isinstance(start_d, datetime) else datetime.combine(start_d, datetime.min.time(), tzinfo=timezone.utc)
                d_dt = due_d if isinstance(due_d, datetime) else datetime.combine(due_d, datetime.min.time(), tzinfo=timezone.utc)
                dur = max(1, (d_dt.date() - s_dt.date()).days)
            durations[m.id] = dur

        # 2. Build Adjacency and In-Degree structures for Topological Sort
        adj: Dict[uuid.UUID, List[uuid.UUID]] = defaultdict(list)
        rev_adj: Dict[uuid.UUID, List[uuid.UUID]] = defaultdict(list)
        in_degree: Dict[uuid.UUID, int] = {m.id: 0 for m in ms_list}

        for dep in dep_list:
            if dep.predecessor_milestone_id in ms_map and dep.successor_milestone_id in ms_map:
                p = dep.predecessor_milestone_id
                s = dep.successor_milestone_id
                adj[p].append(s)
                rev_adj[s].append(p)
                in_degree[s] += 1

        # 3. Kahn's algorithm for Topological Sort
        queue = deque([node for node, deg in in_degree.items() if deg == 0])
        topo_order: List[uuid.UUID] = []

        while queue:
            curr = queue.popleft()
            topo_order.append(curr)
            for neighbor in adj[curr]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        # Fallback if unlinked or circular nodes exist
        for m in ms_list:
            if m.id not in topo_order:
                topo_order.append(m.id)

        # 4. Forward Pass: Compute Early Start (ES) and Early Finish (EF)
        es: Dict[uuid.UUID, int] = {m.id: 0 for m in ms_list}
        ef: Dict[uuid.UUID, int] = {m.id: durations[m.id] for m in ms_list}

        for u in topo_order:
            for v in adj[u]:
                if ef[u] > es[v]:
                    es[v] = ef[u]
                    ef[v] = es[v] + durations[v]

        max_project_duration = max((ef[m.id] for m in ms_list), default=0)

        # 5. Backward Pass: Compute Late Start (LS) and Late Finish (LF)
        lf: Dict[uuid.UUID, int] = {m.id: max_project_duration for m in ms_list}
        ls: Dict[uuid.UUID, int] = {m.id: max_project_duration - durations[m.id] for m in ms_list}

        for u in reversed(topo_order):
            for p in rev_adj[u]:
                if ls[u] < lf[p]:
                    lf[p] = ls[u]
                    ls[p] = lf[p] - durations[p]

        # 6. Calculate Float / Slack (LS - ES)
        # Critical nodes have minimum slack (Slack == 0)
        critical_nodes: List[uuid.UUID] = []
        for u in topo_order:
            slack = ls[u] - es[u]
            if slack <= 0:
                critical_nodes.append(u)

        if not critical_nodes:
            critical_nodes = topo_order[:1]

        critical_path_dur = sum(durations[n] for n in critical_nodes)

        # 7. Projected Delay Impact calculation
        # Check if any critical milestone is currently overdue or blocked
        projected_delay_days = 0
        blocked_critical_nodes = 0

        for node_id in critical_nodes:
            m = ms_map[node_id]
            if m.status == MilestoneStatus.BLOCKED:
                blocked_critical_nodes += 1
                projected_delay_days += 7  # projected week push for blocked critical path node

            if m.status not in (MilestoneStatus.COMPLETED, MilestoneStatus.CANCELLED):
                eff_due = m.planned_due_date or m.due_date or m.baseline_due_date
                if eff_due:
                    eff_dt = eff_due if isinstance(eff_due, datetime) else datetime.combine(eff_due, datetime.min.time(), tzinfo=timezone.utc)
                    if eff_dt.tzinfo is None:
                        eff_dt = eff_dt.replace(tzinfo=timezone.utc)
                    if eff_dt.date() < now.date():
                        delay = (now.date() - eff_dt.date()).days
                        projected_delay_days = max(projected_delay_days, delay)

        # 8. Critical Path Stability Score (0-100)
        base_stability = 100.0
        stability_penalty = 0.0

        if blocked_critical_nodes > 0:
            stability_penalty += blocked_critical_nodes * 25.0

        if projected_delay_days > 0:
            stability_penalty += min(50.0, projected_delay_days * 2.5)

        stability_score = round(min(100.0, max(0.0, base_stability - stability_penalty)), 1)

        return CriticalPathMetrics(
            critical_path_length=len(critical_nodes),
            critical_milestone_count=len(critical_nodes),
            critical_initiative_count=1,
            critical_path_duration_days=critical_path_dur,
            projected_delay_days=projected_delay_days,
            critical_path_stability_score=stability_score,
            critical_path_nodes=critical_nodes,
            engine_version=CRITICAL_PATH_ENGINE_VERSION,
        )
