"""Strategic Roadmap Builder for Phase 11.6: Executive Decision Simulation & Strategic Roadmap Intelligence."""

from datetime import datetime, timezone
from typing import Dict, List, Optional
from uuid import UUID

from app.portfolio.roadmaps.constants import (
    DECISION_ENGINE_VERSION,
    ROADMAP_ENGINE_VERSION,
    ROADMAP_VERSION,
    InitiativeHorizon,
)
from app.portfolio.roadmaps.schemas import (
    QuarterlyRoadmap,
    StrategicInitiative,
    StrategicRoadmapResponse,
)


class StrategicRoadmapBuilder:
    """
    Sequences strategic initiatives across Q1-Q4 execution horizons,
    calculates quarterly effort allocation, and computes aggregate portfolio roadmap metrics.
    """

    HORIZON_METADATA: Dict[InitiativeHorizon, Dict[str, any]] = {
        InitiativeHorizon.Q1: {
            "title": "Quarter 1: Critical Risk Elimination & Stabilization",
            "focus_areas": [
                "Immediate Risk Remediation",
                "Executive Governance Cadence",
                "Severe Finding Backlog Triage",
            ],
        },
        InitiativeHorizon.Q2: {
            "title": "Quarter 2: Operational Turnaround & Performance Growth",
            "focus_areas": [
                "Trend Reversal",
                "Root-Cause KPI Diagnostics",
                "Positive Velocity Recovery",
            ],
        },
        InitiativeHorizon.Q3: {
            "title": "Quarter 3: High-Performance Expansion & Playbook Scaling",
            "focus_areas": [
                "Cohort Promotion Acceleration",
                "Flagship Operating Framework Replication",
                "Peer Group Upgrades",
            ],
        },
        InitiativeHorizon.Q4: {
            "title": "Quarter 4: Portfolio Rebalancing & Long-Term Optimization",
            "focus_areas": [
                "Performance Dispersion Compression",
                "Capital & Resource Re-Allocation",
                "Operating Model Standardization",
            ],
        },
    }

    @classmethod
    def build_roadmap(
        cls,
        organization_id: UUID,
        initiatives: List[StrategicInitiative],
        total_portfolio: int,
        analyzed_count: int,
        source_snapshot_id: Optional[UUID] = None,
        source_snapshot_generated_at: Optional[datetime] = None,
    ) -> StrategicRoadmapResponse:
        """
        Partitions initiatives into quarterly execution horizons and compiles comprehensive roadmap response.
        """
        quarters: List[QuarterlyRoadmap] = []

        q_map: Dict[InitiativeHorizon, List[StrategicInitiative]] = {
            InitiativeHorizon.Q1: [],
            InitiativeHorizon.Q2: [],
            InitiativeHorizon.Q3: [],
            InitiativeHorizon.Q4: [],
        }

        for init in initiatives:
            q_map.setdefault(init.horizon, []).append(init)

        for horiz in [InitiativeHorizon.Q1, InitiativeHorizon.Q2, InitiativeHorizon.Q3, InitiativeHorizon.Q4]:
            q_inits = q_map.get(horiz, [])
            meta = cls.HORIZON_METADATA.get(horiz, {"title": f"Quarter {horiz.value}", "focus_areas": []})

            q_effort = round(sum(i.effort_weight for i in q_inits), 1)
            q_health = round(sum(i.expected_health_gain for i in q_inits), 1)
            q_risk = round(sum(i.risk_reduction_pct for i in q_inits), 1)

            quarters.append(
                QuarterlyRoadmap(
                    quarter=horiz,
                    title=meta["title"],
                    initiatives=q_inits,
                    initiative_count=len(q_inits),
                    quarter_effort=q_effort,
                    quarter_health_gain=q_health,
                    quarter_risk_reduction_pct=q_risk,
                    focus_areas=meta["focus_areas"],
                )
            )

        q1_count = len(q_map[InitiativeHorizon.Q1])
        q2_count = len(q_map[InitiativeHorizon.Q2])
        q3_count = len(q_map[InitiativeHorizon.Q3])
        q4_count = len(q_map[InitiativeHorizon.Q4])

        total_gain = round(sum(i.expected_health_gain for i in initiatives), 1)
        total_risk = round(min(100.0, sum(i.risk_reduction_pct for i in initiatives)), 1)
        total_effort = round(sum(i.effort_weight for i in initiatives), 1)
        overall_roi = round(total_gain / max(0.5, total_effort), 2)

        now = datetime.now(timezone.utc)
        return StrategicRoadmapResponse(
            organization_id=organization_id,
            portfolio_size=total_portfolio,
            analyzed_workspaces=analyzed_count,
            q1_initiative_count=q1_count,
            q2_initiative_count=q2_count,
            q3_initiative_count=q3_count,
            q4_initiative_count=q4_count,
            quarters=quarters,
            total_initiatives=len(initiatives),
            total_projected_health_gain=total_gain,
            total_projected_risk_reduction=total_risk,
            total_effort_weight=total_effort,
            overall_roi_score=overall_roi,
            source_snapshot_id=source_snapshot_id,
            source_snapshot_generated_at=source_snapshot_generated_at,
            roadmap_version=ROADMAP_VERSION,
            roadmap_engine_version=ROADMAP_ENGINE_VERSION,
            roadmap_generated_at=now,
            generated_at=now,
        )
