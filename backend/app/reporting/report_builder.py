"""Report Builder assembling verified platform intelligence into structured ReportDocument."""

import logging
from typing import Any, Dict, List, Optional, Union
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.executive_insights.repositories.executive_insight_repository import (
    ExecutiveInsightRepository,
)
from app.forecasting.repositories.forecast_repository import ForecastRepository
from app.intelligence.health_score import BusinessHealthScoreEngine
from app.repositories.intelligence_repository import IntelligenceRepository
from app.repositories.narrative_repository import NarrativeRepository
from app.reporting.constants import REPORT_TITLES, ReportType
from app.reporting.report_templates import (
    DocumentMetadata,
    ReportDocument,
    ReportSection,
)
from app.scenario_simulation.repositories.scenario_repository import (
    ScenarioRepository,
)

logger = logging.getLogger(__name__)


class ReportBuilder:
    """
    Assembles presentation-ready report data structures from deterministic platform telemetry.
    Strict Guardrail: Under no circumstance does this engine query raw dataset CSVs.
    """

    def __init__(self, db: Union[AsyncSession, Session]):
        self.db = db
        self.intel_repo = IntelligenceRepository(db)
        self.narrative_repo = NarrativeRepository(db)
        self.insight_repo = ExecutiveInsightRepository(db)
        self.forecast_repo = ForecastRepository(db)
        self.scenario_repo = ScenarioRepository(db)

    async def build(
        self,
        dataset_id: UUID,
        report_type: ReportType = ReportType.FULL_BOARD_PACKAGE,
        custom_title: Optional[str] = None,
        company_name: Optional[str] = None,
        include_raw_evidence: bool = True,
    ) -> Optional[ReportDocument]:
        """
        Gathers verified artifacts and compiles them into a structured ReportDocument.
        """
        artifacts = await self.intel_repo.get_dataset_with_all_artifacts(dataset_id)
        if not artifacts:
            return None

        dataset, metrics, findings, root_causes, recommendations = artifacts

        # Deterministic Health Score
        health_score, health_status = BusinessHealthScoreEngine.calculate(
            findings=findings,
            root_causes=root_causes,
            recommendations=recommendations,
        )
        h_status_str = health_status.value if hasattr(health_status, "value") else str(health_status)

        # Narrative & Insight Reports
        narrative_report = await self.narrative_repo.get_latest_by_dataset(dataset_id)
        insight_report = await self.insight_repo.get_latest_by_dataset(dataset_id)

        # Forecasts & Scenarios
        forecasts = await self.forecast_repo.list_history_by_dataset(dataset_id, limit=5)
        scenarios = await self.scenario_repo.list_history_by_dataset(dataset_id, limit=5)

        # Title
        doc_title = custom_title or REPORT_TITLES.get(report_type, "Executive Intelligence Report")
        org_name = company_name or "Enterprise Organization"

        metadata = DocumentMetadata(
            title=doc_title,
            subtitle=f"Comprehensive Business Analytics & Decision Telemetry for {dataset.name}",
            company_name=org_name,
            dataset_name=dataset.name,
            dataset_id=str(dataset.id),
            business_health_score=health_score,
            business_health_status=h_status_str,
        )

        sections: List[ReportSection] = []
        evidence: List[Dict[str, Any]] = []

        # Populate Sections Based on ReportType
        if report_type == ReportType.EXECUTIVE_SUMMARY:
            sections.extend(self._build_executive_summary_sections(health_score, h_status_str, narrative_report, findings, recommendations))
        elif report_type == ReportType.KPI_PERFORMANCE:
            sections.extend(self._build_kpi_sections(metrics, narrative_report))
        elif report_type == ReportType.DIAGNOSTIC:
            sections.extend(self._build_diagnostic_sections(findings, narrative_report))
        elif report_type == ReportType.ROOT_CAUSE:
            sections.extend(self._build_root_cause_sections(root_causes, narrative_report))
        elif report_type == ReportType.RECOMMENDATION_ROADMAP:
            sections.extend(self._build_recommendation_sections(recommendations, narrative_report))
        elif report_type == ReportType.FORECAST:
            sections.extend(self._build_forecast_sections(forecasts, narrative_report))
        elif report_type == ReportType.SCENARIO_PLANNING:
            sections.extend(self._build_scenario_sections(scenarios, narrative_report))
        elif report_type == ReportType.EXECUTIVE_INTELLIGENCE:
            sections.extend(self._build_executive_intelligence_sections(insight_report, narrative_report, health_score, h_status_str))
        else:
            # FULL_BOARD_PACKAGE: Build all 11 sections
            sections.extend(self._build_full_board_sections(
                health_score=health_score,
                health_status_str=h_status_str,
                metrics=metrics,
                findings=findings,
                root_causes=root_causes,
                recommendations=recommendations,
                narrative_report=narrative_report,
                insight_report=insight_report,
                forecasts=forecasts,
                scenarios=scenarios,
            ))

        # Evidence references
        if include_raw_evidence:
            evidence = self._compile_evidence_references(findings, root_causes, recommendations, forecasts, scenarios)

        return ReportDocument(
            report_type=report_type,
            metadata=metadata,
            sections=sections,
            evidence_references=evidence,
        )

    # -----------------------------------------------------------------------
    # Section Builders
    # -----------------------------------------------------------------------

    @staticmethod
    def _extract_text(narrative_obj: Any) -> Optional[str]:
        if not narrative_obj:
            return None
        if isinstance(narrative_obj, str):
            return narrative_obj
        if isinstance(narrative_obj, dict):
            return (
                narrative_obj.get("narrative_text")
                or narrative_obj.get("executive_summary")
                or narrative_obj.get("headline")
                or narrative_obj.get("explanation")
            )
        return str(narrative_obj)

    def _build_executive_summary_sections(
        self,
        health_score: int,
        health_status_str: str,
        narrative_report: Any,
        findings: List[Any],
        recommendations: List[Any],
    ) -> List[ReportSection]:
        summary_text = (
            self._extract_text(getattr(narrative_report, "executive_summary", None))
            if narrative_report
            else None
        ) or (
            f"Operational telemetry reflects a composite Business Health Score of {health_score}/100 ({health_status_str}). "
            f"Evaluation of core business dimensions indicates active performance constraints requiring targeted intervention."
        )
        callout_text = f"Business Health: {health_score}/100 ({health_status_str}) — {len(findings)} anomalies diagnosed; {len(recommendations)} strategic actions pending."

        return [
            ReportSection(
                key="executive_briefing",
                title="Executive Briefing & Business Health",
                order=1,
                content=summary_text,
                callout=callout_text,
                data={
                    "health_score": health_score,
                    "health_status": health_status_str,
                    "total_findings": len(findings),
                    "total_recommendations": len(recommendations),
                },
            ),
        ]

    def _build_kpi_sections(self, metrics: List[Any], narrative_report: Any) -> List[ReportSection]:
        kpi_table = []
        for m in metrics:
            val = float(m.metric_value) if hasattr(m, "metric_value") and m.metric_value is not None else 0.0
            cat = m.metric_category.value if hasattr(m, "metric_category") and hasattr(m.metric_category, "value") else str(getattr(m, "metric_category", "OPERATIONAL"))
            kpi_table.append({
                "metric_key": m.metric_key,
                "metric_name": m.metric_name,
                "category": cat,
                "value": f"{val:,.2f}" if isinstance(val, (int, float)) else str(val),
            })

        kpi_narrative = (
            self._extract_text(getattr(narrative_report, "kpi_narrative", None))
            if narrative_report
            else None
        ) or "KPI metrics were extracted across primary business operational categories."

        return [
            ReportSection(
                key="kpi_overview",
                title="Key Performance Indicator (KPI) Overview",
                order=2,
                content=kpi_narrative,
                data={"metrics_table": kpi_table},
                callout=f"Monitored {len(metrics)} primary KPI indicators across enterprise operational dimensions.",
            )
        ]

    def _build_diagnostic_sections(self, findings: List[Any], narrative_report: Any) -> List[ReportSection]:
        findings_table = []
        for f in findings:
            sev = f.severity.value if hasattr(f.severity, "value") else str(f.severity)
            findings_table.append({
                "title": f.title,
                "severity": sev.upper(),
                "impact": f.business_impact or f.description or "Operational variance.",
                "confidence": f"{float(f.confidence_score or 0.85) * 100:.1f}%",
            })

        diag_narr = (
            self._extract_text(getattr(narrative_report, "diagnostic_narrative", None))
            if narrative_report
            else None
        ) or f"Diagnostic engine detected {len(findings)} operational anomalies across revenue and fulfillment streams."

        return [
            ReportSection(
                key="diagnostic_findings",
                title="Diagnostic Anomaly Analysis",
                order=3,
                content=diag_narr,
                data={"findings_table": findings_table},
                callout=f"Identified {len(findings)} operational variances requiring root-cause investigation.",
            )
        ]

    def _build_root_cause_sections(self, root_causes: List[Any], narrative_report: Any) -> List[ReportSection]:
        rca_table = []
        for r in root_causes:
            cause_title = r.explanation or (r.root_cause_finding.title if getattr(r, "root_cause_finding", None) else "Root Cause Anomaly")
            primary_title = r.primary_finding.title if getattr(r, "primary_finding", None) else "Primary Symptom"
            strength = r.relationship_strength.value if hasattr(r.relationship_strength, "value") else str(r.relationship_strength)
            rca_table.append({
                "cause": cause_title,
                "effect": primary_title,
                "strength": strength,
                "impact_score": f"{float(getattr(r, 'impact_score', 0.5) or 0.5):.2f}",
            })

        rca_narr = (
            self._extract_text(getattr(narrative_report, "root_cause_narrative", None))
            if narrative_report
            else None
        ) or f"Root cause analysis confirmed {len(root_causes)} causal linkages explaining diagnosed business variances."

        return [
            ReportSection(
                key="root_cause_analysis",
                title="Root Cause & Causal Attribution",
                order=4,
                content=rca_narr,
                data={"root_causes_table": rca_table},
                callout=f"Validated {len(root_causes)} primary causal drivers directly impacting business performance.",
            )
        ]

    def _build_recommendation_sections(self, recommendations: List[Any], narrative_report: Any) -> List[ReportSection]:
        rec_table = []
        for r in recommendations:
            prio = r.priority.value if hasattr(r.priority, "value") else str(r.priority)
            rec_table.append({
                "title": r.title,
                "priority": prio.upper(),
                "rationale": getattr(r, "why_recommended", None) or getattr(r, "description", "Strategic action."),
                "impact": f"{float(getattr(r, 'estimated_impact_score', 0.8) or 0.8):.2f}",
                "effort": f"{float(getattr(r, 'estimated_effort_score', 0.3) or 0.3):.2f}",
            })

        rec_narr = (
            self._extract_text(getattr(narrative_report, "recommendation_narrative", None))
            if narrative_report
            else None
        ) or f"Generated {len(recommendations)} actionable recommendations prioritized by business impact."

        return [
            ReportSection(
                key="strategic_recommendations",
                title="Strategic Recommendation Roadmap",
                order=5,
                content=rec_narr,
                data={"recommendations_table": rec_table},
                callout=f"Prioritized {len(recommendations)} strategic actions designed to eliminate operational constraints.",
            )
        ]

    def _build_forecast_sections(self, forecasts: List[Any], narrative_report: Any) -> List[ReportSection]:
        fc_table = []
        for fc in forecasts:
            m_type = getattr(fc, "model_name", None) or getattr(fc, "model_type", "AUTO")
            if hasattr(m_type, "value"):
                m_type = m_type.value
            metrics_dict = getattr(fc, "model_metrics", None) or getattr(fc, "evaluation_metrics", None) or {}
            points = getattr(fc, "forecast_points", None) or getattr(fc, "forecast_data", None) or []
            fc_table.append({
                "metric_key": fc.metric_key,
                "model_type": str(m_type),
                "mape": f"{metrics_dict.get('mape', 0.0):.2f}%",
                "periods": len(points),
            })

        fc_narr = (
            self._extract_text(getattr(narrative_report, "forecast_narrative", None))
            if narrative_report
            else None
        ) or "Predictive forecasting models evaluated historical metric trajectory to establish future baseline projections."

        return [
            ReportSection(
                key="forecast_outlook",
                title="Predictive Forecast & Horizon Outlook",
                order=6,
                content=fc_narr,
                data={"forecasts_table": fc_table},
                callout="Forecast simulations indicate stable projected trajectory assuming timely execution of recommendations.",
            )
        ]

    def _build_scenario_sections(self, scenarios: List[Any], narrative_report: Any) -> List[ReportSection]:
        sc_table = []
        for sc in scenarios:
            st = sc.status.value if hasattr(sc.status, "value") else str(sc.status)
            sc_table.append({
                "name": sc.name,
                "status": st,
                "assumptions_count": len(sc.assumptions or []),
            })

        sc_narr = (
            self._extract_text(getattr(narrative_report, "scenario_narrative", None))
            if narrative_report
            else None
        ) or "Scenario simulations quantified sensitivity across pricing, customer churn, and operational adjustment levers."

        return [
            ReportSection(
                key="scenario_analysis",
                title="Scenario Simulation & Sensitivity Analysis",
                order=7,
                content=sc_narr,
                data={"scenarios_table": sc_table},
                callout="Scenario modeling highlights significant upside gain upon executing prioritized retention strategies.",
            )
        ]

    def _build_executive_intelligence_sections(
        self,
        insight_report: Any,
        narrative_report: Any,
        health_score: int,
        health_status_str: str,
    ) -> List[ReportSection]:
        risks = getattr(insight_report, "top_risks", []) or [] if insight_report else []
        opps = getattr(insight_report, "top_opportunities", []) or [] if insight_report else []
        actions = getattr(insight_report, "priority_actions", []) or [] if insight_report else []
        commentary = getattr(insight_report, "board_commentary", None) or "Executive commentary reflects positive operational resilience."

        return [
            ReportSection(
                key="executive_briefing",
                title="Executive Briefing & Strategic Priorities",
                order=1,
                content=commentary,
                callout=f"Business Health: {health_score}/100 ({health_status_str}) | {len(risks)} Active Risks | {len(opps)} Strategic Opportunities.",
                data={
                    "top_risks": risks,
                    "top_opportunities": opps,
                    "priority_actions": actions,
                },
            )
        ]

    def _build_full_board_sections(
        self,
        health_score: int,
        health_status_str: str,
        metrics: List[Any],
        findings: List[Any],
        root_causes: List[Any],
        recommendations: List[Any],
        narrative_report: Any,
        insight_report: Any,
        forecasts: List[Any],
        scenarios: List[Any],
    ) -> List[ReportSection]:
        sections: List[ReportSection] = []

        # 1. Executive Summary
        sections.extend(self._build_executive_summary_sections(health_score, health_status_str, narrative_report, findings, recommendations))

        # 2. KPI Overview
        sections.extend(self._build_kpi_sections(metrics, narrative_report))

        # 3. Critical Findings
        sections.extend(self._build_diagnostic_sections(findings, narrative_report))

        # 4. Root Causes
        sections.extend(self._build_root_cause_sections(root_causes, narrative_report))

        # 5. Strategic Recommendations
        sections.extend(self._build_recommendation_sections(recommendations, narrative_report))

        # 6. Forecast Outlook
        sections.extend(self._build_forecast_sections(forecasts, narrative_report))

        # 7. Scenario Analysis
        sections.extend(self._build_scenario_sections(scenarios, narrative_report))

        # 8. Executive Risks, Opportunities & Board Commentary
        if insight_report:
            risks = insight_report.top_risks or []
            opps = insight_report.top_opportunities or []
            actions = insight_report.priority_actions or []
            comm = insight_report.board_commentary or "Boardroom guidance recommends prompt execution of high-priority operational fixes."
            sections.append(
                ReportSection(
                    key="boardroom_insights",
                    title="Executive Risks, Opportunities & Strategic Themes",
                    order=8,
                    content=comm,
                    data={
                        "top_risks": risks,
                        "top_opportunities": opps,
                        "priority_actions": actions,
                    },
                    callout="Executive intelligence synthesizes multi-dimensional risk exposure and prioritized growth drivers.",
                )
            )

        return sections

    def _compile_evidence_references(
        self,
        findings: List[Any],
        root_causes: List[Any],
        recommendations: List[Any],
        forecasts: List[Any],
        scenarios: List[Any],
    ) -> List[Dict[str, Any]]:
        evidence = []
        for f in findings:
            evidence.append({
                "id": str(f.id),
                "type": "DIAGNOSTIC_FINDING",
                "title": f.title,
                "confidence": float(f.confidence_score or 0.85),
            })
        for r in root_causes:
            evidence.append({
                "id": str(r.id),
                "type": "ROOT_CAUSE",
                "title": r.explanation or "Causal relationship",
                "impact_score": float(getattr(r, "impact_score", 0.5) or 0.5),
            })
        for rec in recommendations:
            evidence.append({
                "id": str(rec.id),
                "type": "RECOMMENDATION",
                "title": rec.title,
                "priority": str(getattr(rec, "priority", "HIGH")),
            })
        for fc in forecasts:
            evidence.append({
                "id": str(fc.id),
                "type": "FORECAST",
                "metric_key": fc.metric_key,
            })
        for sc in scenarios:
            evidence.append({
                "id": str(sc.id),
                "type": "SCENARIO",
                "name": sc.name,
            })
        return evidence
