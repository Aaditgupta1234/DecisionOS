"""
Deterministic pure business-state projection builder for snapshot SHA-256 hashing.
Guarantees business state hashing rather than response envelope hashing.
"""

import json
from typing import Any, Dict
from app.dashboard.constants import HASH_SCHEMA_VERSION


class HashProjectionBuilder:
    """
    Extracts pure business intelligence state from a workspace payload
    while strictly stripping non-deterministic metadata (timestamps, UUIDs, cache hits)
    and export artifacts (report export IDs, file sizes, download URLs).
    """

    @classmethod
    def project(cls, workspace_json: Dict[str, Any]) -> Dict[str, Any]:
        """
        Projects workspace_json to a deterministic canonical business-state dictionary.
        """
        if not isinstance(workspace_json, dict):
            return {"hash_schema_version": HASH_SCHEMA_VERSION, "data": None}

        # 1. Overview (business scorecard & metrics)
        raw_overview = workspace_json.get("overview", {})
        overview_proj = {
            "health_dimensions": raw_overview.get("health_dimensions"),
            "scorecard": raw_overview.get("scorecard"),
            "top_risks": raw_overview.get("top_risks"),
            "top_opportunities": raw_overview.get("top_opportunities"),
            "watchlist_metrics": raw_overview.get("watchlist_metrics"),
            "executive_summary_brief": raw_overview.get("executive_summary_brief"),
        }

        # 2. Intelligence Entities
        kpis_proj = workspace_json.get("kpis", [])
        findings_proj = workspace_json.get("findings", [])
        root_causes_proj = workspace_json.get("root_causes", [])
        recommendations_proj = workspace_json.get("recommendations", [])
        forecasts_proj = workspace_json.get("forecasts", [])
        scenarios_proj = workspace_json.get("scenarios", [])
        narratives_proj = workspace_json.get("narratives", [])
        insights_proj = workspace_json.get("insights", {})

        # 3. Chat Suggested Questions
        chat_data = workspace_json.get("chat", {})
        chat_proj = {
            "suggested_questions": chat_data.get("suggested_questions", []),
        }

        # 4. Reports (Pure intelligence structure, NO export IDs or timestamps)
        reports_data = workspace_json.get("reports", {})
        reports_proj = {
            "total_count": reports_data.get("total_count", 0),
            "latest_report_type": reports_data.get("latest_report_type"),
        }

        return {
            "hash_schema_version": HASH_SCHEMA_VERSION,
            "overview": overview_proj,
            "kpis": kpis_proj,
            "findings": findings_proj,
            "root_causes": root_causes_proj,
            "recommendations": recommendations_proj,
            "forecasts": forecasts_proj,
            "scenarios": scenarios_proj,
            "narratives": narratives_proj,
            "insights": insights_proj,
            "reports": reports_proj,
            "chat": chat_proj,
        }

    @classmethod
    def canonical_json(cls, workspace_json: Dict[str, Any]) -> str:
        """
        Converts projected workspace state to sorted, compact canonical JSON string.
        """
        projected = cls.project(workspace_json)
        return json.dumps(projected, sort_keys=True, separators=(",", ":"))
