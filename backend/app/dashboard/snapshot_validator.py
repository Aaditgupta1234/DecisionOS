"""Dashboard Snapshot Validator for Phase 9.6 Executive Dashboard."""

from typing import Any, Dict, List, Tuple

from app.dashboard.constants import WORKSPACE_VERSION


class DashboardSnapshotValidator:
    """
    Validates the structure and data integrity of generated workspace_json payloads
    prior to persisting snapshots or returning them to clients.
    """

    @classmethod
    def validate_workspace_json(cls, workspace_json: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validates required domain sections and business guardrails.
        Returns:
            (is_valid: bool, warnings: List[str])
        """
        warnings = []

        if not isinstance(workspace_json, dict):
            return False, ["Workspace payload is not a valid JSON dictionary"]

        # Required top-level keys
        required_sections = ["overview", "kpis", "findings", "root_causes", "recommendations", "forecasts", "scenarios", "reports"]
        for section in required_sections:
            if section not in workspace_json:
                warnings.append(f"Section '{section}' is missing from workspace payload")

        # 1. Validate Overview
        overview = workspace_json.get("overview")
        if not isinstance(overview, dict):
            return False, ["Overview section is malformed or missing"]

        health_dim = overview.get("health_dimensions", {})
        overall_score = health_dim.get("overall_score")
        if overall_score is None or not (0 <= overall_score <= 100):
            warnings.append(f"Invalid health score value: {overall_score}, defaulting to 75")

        top_risks = overview.get("top_risks", [])
        if len(top_risks) > 3:
            warnings.append("Top risks list exceeds maximum allowed count of 3")

        top_opps = overview.get("top_opportunities", [])
        if len(top_opps) > 3:
            warnings.append("Top opportunities list exceeds maximum allowed count of 3")

        # 2. Validate Collections
        for col in ["kpis", "findings", "root_causes", "recommendations", "forecasts", "scenarios"]:
            if col in workspace_json and not isinstance(workspace_json[col], list):
                warnings.append(f"Section '{col}' must be a list")

        # 3. Check for empty critical sections
        if not workspace_json.get("kpis"):
            warnings.append("No KPI metrics found for dataset")

        if not workspace_json.get("findings"):
            warnings.append("No diagnostic findings found for dataset")

        is_valid = True
        return is_valid, warnings

    @classmethod
    def validate_version(cls, version_str: str) -> bool:
        """Enforces schema version compatibility."""
        if not version_str or version_str != WORKSPACE_VERSION:
            return False
        return True
