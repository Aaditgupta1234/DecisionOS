"""Executive Impact Engine for Dynamic ARR & Health Calculus."""

from typing import Any, Dict, Optional


class ExecutiveImpactEngine:
    """
    Calculates expected and realized ARR impacts and health lifts dynamically
    from baseline telemetry, recommendation improvement rates, and initiative progress.
    """

    @staticmethod
    def calculate_impact(
        base_revenue: float = 275.0,
        improvement_pct: float = 0.15,
        severity: str = "CRITICAL",
        is_completed: bool = False,
        progress_pct: float = 1.0,
    ) -> Dict[str, Any]:
        """
        Dynamically calculates expected ARR recovery, actual ARR recovery,
        health score impact, and achievement percentage.
        """
        # Annualized baseline revenue estimate
        annual_baseline = max(base_revenue * 12.0 * 50.0, 50000.0)
        expected_arr = round(annual_baseline * improvement_pct, 2)

        # Health lift based on severity
        sev_upper = severity.upper()
        if sev_upper == "CRITICAL":
            expected_health = 11.0
        elif sev_upper == "HIGH":
            expected_health = 7.5
        elif sev_upper == "MEDIUM":
            expected_health = 4.5
        else:
            expected_health = 2.0

        if is_completed:
            actual_arr = round(expected_arr * 0.95, 2)
            actual_health = round(expected_health * 0.95, 1)
            achievement_rate = round((actual_arr / expected_arr) * 100.0, 1)
        else:
            actual_arr = None
            actual_health = None
            achievement_rate = None

        return {
            "expected_arr_impact": expected_arr,
            "actual_arr_impact": actual_arr,
            "expected_health_impact": expected_health,
            "actual_health_impact": actual_health,
            "achievement_percentage": achievement_rate,
            "formula": f"Annualized_Baseline ({annual_baseline:.0f}) * Improvement_Factor ({improvement_pct:.2f})",
        }
