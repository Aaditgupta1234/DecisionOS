"""Citation Builder constructing verified reference objects linked to platform artifacts."""

from typing import Any, Dict, List
from app.chat_analyst.schemas.responses import CitationItem, CitationResponse


class CitationBuilder:
    """
    Builds structured citation metadata from verified finding, RCA, recommendation,
    forecast, and scenario artifacts.
    """

    @classmethod
    def build_citations(
        cls,
        context: Dict[str, Any],
        finding_ids: List[str],
        root_cause_ids: List[str],
        recommendation_ids: List[str],
        forecast_ids: List[str],
        scenario_ids: List[str],
    ) -> CitationResponse:
        """
        Resolves UUID strings to human-readable titles and summaries.
        """
        # Lookup maps
        f_map = {str(f.get("id")): f for f in context.get("findings", []) if f.get("id")}
        rca_map = {str(r.get("id")): r for r in context.get("root_causes", []) if r.get("id")}
        rec_map = {str(r.get("id")): r for r in context.get("recommendations", []) if r.get("id")}
        fc_map = {str(fc.get("id")): fc for fc in context.get("forecasts", []) if fc.get("id")}
        sc_map = {str(sc.get("id")): sc for sc in context.get("scenarios", []) if sc.get("id")}

        # Build items
        cited_findings = []
        for fid in finding_ids:
            f = f_map.get(fid)
            if f:
                cited_findings.append(
                    CitationItem(
                        id=fid,
                        title=f.get("title", "Diagnostic Finding"),
                        artifact_type="FINDING",
                        summary=f.get("impact") or f.get("description"),
                    )
                )

        cited_rcas = []
        for rid in root_cause_ids:
            r = rca_map.get(rid)
            if r:
                title = f"{r.get('cause', 'Cause')} -> {r.get('effect', 'Effect')}"
                cited_rcas.append(
                    CitationItem(
                        id=rid,
                        title=title,
                        artifact_type="ROOT_CAUSE",
                        summary=f"Causal strength: {r.get('strength', 'STRONG')}",
                    )
                )

        cited_recs = []
        for rec_id in recommendation_ids:
            rec = rec_map.get(rec_id)
            if rec:
                cited_recs.append(
                    CitationItem(
                        id=rec_id,
                        title=rec.get("title", "Actionable Recommendation"),
                        artifact_type="RECOMMENDATION",
                        summary=rec.get("rationale"),
                    )
                )

        cited_fcs = []
        for fc_id in forecast_ids:
            fc = fc_map.get(fc_id)
            if fc:
                cited_fcs.append(
                    CitationItem(
                        id=fc_id,
                        title=f"Forecast: {fc.get('metric_key', 'Metric')}",
                        artifact_type="FORECAST",
                        summary=f"Model: {fc.get('model_type', 'AUTO')} (MAPE: {fc.get('mape', 0.0)}%)",
                    )
                )

        cited_scs = []
        for sc_id in scenario_ids:
            sc = sc_map.get(sc_id)
            if sc:
                cited_scs.append(
                    CitationItem(
                        id=sc_id,
                        title=f"Scenario: {sc.get('name', 'Simulation')}",
                        artifact_type="SCENARIO",
                        summary=f"Status: {sc.get('status', 'COMPLETED')}",
                    )
                )

        # Fallback citation if none cited explicitly but context exists
        if not (cited_findings or cited_rcas or cited_recs or cited_fcs or cited_scs):
            if context.get("findings"):
                first_f = context["findings"][0]
                cited_findings.append(
                    CitationItem(
                        id=str(first_f.get("id")),
                        title=first_f.get("title", "Primary Anomaly"),
                        artifact_type="FINDING",
                        summary=first_f.get("impact"),
                    )
                )

        return CitationResponse(
            findings=cited_findings,
            root_causes=cited_rcas,
            recommendations=cited_recs,
            forecasts=cited_fcs,
            scenarios=cited_scs,
        )

    @classmethod
    def to_legacy_source_list(cls, citations: CitationResponse) -> List[str]:
        """Flattens citations into a string list for backward compatibility."""
        sources = []
        for f in citations.findings:
            sources.append(f"Finding: {f.title}")
        for r in citations.root_causes:
            sources.append(f"Root Cause: {r.title}")
        for rec in citations.recommendations:
            sources.append(f"Recommendation: {rec.title}")
        for fc in citations.forecasts:
            sources.append(f"Forecast: {fc.title}")
        for sc in citations.scenarios:
            sources.append(f"Scenario: {sc.title}")
        return sources
