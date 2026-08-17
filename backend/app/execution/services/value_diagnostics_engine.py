"""Value Diagnostics & Portfolio Concentration Engine for Phase 12.7."""

import math
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.execution.constants import (
    STRATEGIC_SNAPSHOT_METRIC_VERSION,
    VALUE_DIAGNOSTICS_ENGINE_VERSION,
)


class ValueDiagnosticsEngine:
    """
    Deterministic diagnostics engine categorizing initiatives into 7 strategic cohorts
    and calculating Pareto value & dependency concentration risks.
    """

    ENGINE_VERSION = VALUE_DIAGNOSTICS_ENGINE_VERSION
    SNAPSHOT_METRIC_VERSION = STRATEGIC_SNAPSHOT_METRIC_VERSION

    @classmethod
    def diagnose_portfolio(
        cls,
        initiatives: List[Dict[str, Any]],
        dependencies: Optional[List[Dict[str, Any]]] = None,
        governance_issues: Optional[List[Dict[str, Any]]] = None,
        critical_outcomes: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Runs comprehensive deterministic diagnostic evaluation across all portfolio initiatives.
        """
        now = datetime.now(timezone.utc)
        warnings: List[str] = []

        if not initiatives:
            warnings.append("No initiatives available for value diagnostics.")
            empty_val_conc = {
                "top_10_percent_value_share": 0.0,
                "top_20_percent_value_share": 0.0,
                "herfindahl_index": 0.0,
                "concentration_risk_level": "LOW",
            }
            empty_dep_conc = {
                "max_dependent_initiatives": 0,
                "critical_path_bottlenecks_count": 0,
                "single_point_of_failure_count": 0,
                "dependency_risk_level": "LOW",
            }
            return {
                "high_value_initiatives": [],
                "high_roi_initiatives": [],
                "underperforming_initiatives": [],
                "high_cost_low_return_initiatives": [],
                "high_risk_low_value_initiatives": [],
                "governance_bottlenecks": [],
                "critical_outcome_exposures": [],
                "value_concentration": empty_val_conc,
                "dependency_concentration": empty_dep_conc,
                "data_quality_warnings": warnings,
                "calculated_at": now,
            }

        total_count = len(initiatives)

        # 1. Medians for Comparative Diagnostics
        costs = [float(i.get("actual_cost", i.get("budget_allocated", 0.0))) for i in initiatives]
        values = [float(i.get("strategic_value_score", 50.0)) for i in initiatives]
        rois = [float(i.get("roi_score", 50.0)) for i in initiatives]

        costs.sort()
        values.sort()
        rois.sort()

        median_cost = costs[total_count // 2] if total_count > 0 else 0.0
        median_value = values[total_count // 2] if total_count > 0 else 50.0
        median_roi = rois[total_count // 2] if total_count > 0 else 50.0

        # 2. Dependency Graph Degree Calculations
        dependent_counts: Dict[str, int] = {}
        blocking_counts: Dict[str, int] = {}
        is_on_critical_path: Dict[str, bool] = {}

        if dependencies:
            for dep in dependencies:
                source_id = str(dep.get("source_initiative_id", dep.get("initiative_id", "")))
                target_id = str(dep.get("target_initiative_id", dep.get("depends_on_initiative_id", "")))
                if source_id:
                    blocking_counts[source_id] = blocking_counts.get(source_id, 0) + 1
                if target_id:
                    dependent_counts[target_id] = dependent_counts.get(target_id, 0) + 1

        for i in initiatives:
            init_id_str = str(i.get("id", i.get("initiative_id", "")))
            if i.get("is_on_critical_path") or i.get("critical_path_exposure", 0.0) > 60.0:
                is_on_critical_path[init_id_str] = True

        # 3. Classify the 7 Cohorts
        high_value: List[Dict[str, Any]] = []
        high_roi: List[Dict[str, Any]] = []
        underperforming: List[Dict[str, Any]] = []
        high_cost_low_return: List[Dict[str, Any]] = []
        high_risk_low_value: List[Dict[str, Any]] = []
        governance_bottlenecks: List[Dict[str, Any]] = []
        critical_outcome_exposures: List[Dict[str, Any]] = []

        gov_map = {str(g.get("initiative_id")): g for g in (governance_issues or [])}
        crit_out_map = {str(o.get("initiative_id")): o for o in (critical_outcomes or [])}

        for init in initiatives:
            init_id = init.get("id", init.get("initiative_id", uuid.uuid4()))
            init_id_str = str(init_id)
            title = init.get("title", init.get("name", f"Initiative {init_id_str[:8]}"))
            
            val_score = float(init.get("strategic_value_score", 50.0))
            roi_score = float(init.get("roi_score", 50.0))
            health_score = float(init.get("health_score", init.get("execution_health", 70.0)))
            risk_score = float(init.get("risk_score", init.get("execution_risk", 20.0)))
            outcome_ach = float(init.get("outcome_achievement", init.get("outcome_score", 70.0)))
            cost = float(init.get("actual_cost", init.get("budget_allocated", 0.0)))
            gov_score = float(init.get("governance_maturity_score", init.get("governance_score", 80.0)))

            base_item = {
                "initiative_id": init_id,
                "title": title,
                "strategic_value_score": round(val_score, 2),
                "roi_score": round(roi_score, 2),
                "health_score": round(health_score, 2),
                "risk_score": round(risk_score, 2),
            }

            # 1. High Value (>= 75.0)
            if val_score >= 75.0:
                high_value.append({
                    **base_item,
                    "reason": f"Delivering exceptional strategic value ({val_score:.1f}/100)",
                })

            # 2. High ROI (>= 75.0 or ROI % >= 50%)
            if roi_score >= 75.0 or init.get("roi_percentage", 0.0) >= 50.0:
                high_roi.append({
                    **base_item,
                    "reason": f"Generating strong capital return with ROI score of {roi_score:.1f}",
                })

            # 3. Underperforming (Health < 60 or Outcome < 50)
            if health_score < 60.0 or outcome_ach < 50.0:
                underperforming.append({
                    **base_item,
                    "reason": f"Sub-optimal delivery performance (Health: {health_score:.1f}, Outcomes: {outcome_ach:.1f}%)",
                })

            # 4. High Cost / Low Return (Cost > median and (Value < median or ROI < median))
            if cost > median_cost and (val_score < median_value or roi_score < median_roi):
                high_cost_low_return.append({
                    **base_item,
                    "reason": f"Disproportionate resource consumption relative to delivered value/ROI",
                })

            # 5. High Risk / Low Value (Risk >= 60 and Value < 50)
            if risk_score >= 60.0 and val_score < 50.0:
                high_risk_low_value.append({
                    **base_item,
                    "reason": f"Elevated delivery risk ({risk_score:.1f}) with limited strategic yield ({val_score:.1f})",
                })

            # 6. Governance Bottlenecks (Gov < 60 or overdue reviews / blocked actions)
            has_gov_issue = init_id_str in gov_map or gov_score < 60.0 or init.get("overdue_reviews_count", 0) > 0
            if has_gov_issue:
                governance_bottlenecks.append({
                    **base_item,
                    "reason": f"Governance maturity deficit ({gov_score:.1f}) or overdue decision checkpoints",
                })

            # 7. Critical Outcome Exposure
            has_crit_out = (
                init_id_str in crit_out_map
                or init.get("critical_outcomes_at_risk_count", 0) > 0
                or (outcome_ach < 60.0 and init.get("is_strategic_core", False))
            )
            if has_crit_out:
                critical_outcome_exposures.append({
                    **base_item,
                    "reason": "Core strategic outcomes are off-track or facing realization delays",
                })

        # 4. Portfolio Value Concentration Calculation (Pareto 80/20 & Herfindahl)
        # Sort initiatives descending by strategic value
        sorted_by_val = sorted(initiatives, key=lambda x: float(x.get("strategic_value_score", 0.0)), reverse=True)
        total_val = sum(float(x.get("strategic_value_score", 0.0)) for x in sorted_by_val)

        if total_val > 0:
            top_10_count = max(1, math.ceil(total_count * 0.10))
            top_20_count = max(1, math.ceil(total_count * 0.20))

            top_10_val = sum(float(x.get("strategic_value_score", 0.0)) for x in sorted_by_val[:top_10_count])
            top_20_val = sum(float(x.get("strategic_value_score", 0.0)) for x in sorted_by_val[:top_20_count])

            top_10_pct = round((top_10_val / total_val) * 100.0, 2)
            top_20_pct = round((top_20_val / total_val) * 100.0, 2)

            # Herfindahl Index = Sum( (val_i / total_val * 100)^2 )
            hhi = sum(((float(x.get("strategic_value_score", 0.0)) / total_val) * 100.0) ** 2 for x in sorted_by_val)
            hhi = round(hhi, 2)
        else:
            top_10_pct = 0.0
            top_20_pct = 0.0
            hhi = 0.0

        if top_20_pct >= 85.0:
            val_risk_level = "CRITICAL"
        elif top_20_pct >= 70.0:
            val_risk_level = "HIGH"
        elif top_20_pct >= 50.0:
            val_risk_level = "MODERATE"
        else:
            val_risk_level = "LOW"

        value_conc_summary = {
            "top_10_percent_value_share": top_10_pct,
            "top_20_percent_value_share": top_20_pct,
            "herfindahl_index": hhi,
            "concentration_risk_level": val_risk_level,
        }

        # 5. Portfolio Dependency Concentration Calculation
        max_deps = max(blocking_counts.values()) if blocking_counts else 0
        crit_bottlenecks = sum(1 for init_id_str, count in blocking_counts.items() if count >= 2 and is_on_critical_path.get(init_id_str, False))
        single_point_of_failures = sum(1 for init_id_str, count in blocking_counts.items() if count >= 3)

        if max_deps >= 6 or single_point_of_failures >= 3:
            dep_risk_level = "CRITICAL"
        elif max_deps >= 4 or single_point_of_failures >= 1:
            dep_risk_level = "HIGH"
        elif max_deps >= 2:
            dep_risk_level = "MODERATE"
        else:
            dep_risk_level = "LOW"

        dep_conc_summary = {
            "max_dependent_initiatives": max_deps,
            "critical_path_bottlenecks_count": crit_bottlenecks,
            "single_point_of_failure_count": single_point_of_failures,
            "dependency_risk_level": dep_risk_level,
        }

        if val_risk_level in ("HIGH", "CRITICAL"):
            warnings.append(f"High portfolio value concentration: top 20% initiatives drive {top_20_pct:.1f}% of total value.")
        if dep_risk_level in ("HIGH", "CRITICAL"):
            warnings.append(f"Significant dependency concentration detected with {single_point_of_failures} single point(s) of failure.")

        return {
            "high_value_initiatives": high_value,
            "high_roi_initiatives": high_roi,
            "underperforming_initiatives": underperforming,
            "high_cost_low_return_initiatives": high_cost_low_return,
            "high_risk_low_value_initiatives": high_risk_low_value,
            "governance_bottlenecks": governance_bottlenecks,
            "critical_outcome_exposures": critical_outcome_exposures,
            "value_concentration": value_conc_summary,
            "dependency_concentration": dep_conc_summary,
            "data_quality_warnings": warnings,
            "calculated_at": now,
        }
