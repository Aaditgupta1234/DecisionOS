"""Deterministic Mock LLM Provider for offline execution, CI/CD testing, and fallback."""

import json
import logging
from typing import Any, Dict, Optional

from app.ai_insights.constants import DEFAULT_MODEL_NAME, PROVIDER_MOCK
from app.ai_insights.providers.base_llm_provider import BaseLLMProvider

logger = logging.getLogger(__name__)


class MockLLMProvider(BaseLLMProvider):
    """
    Deterministic Mock LLM Provider ensuring reliable offline test execution
    and zero-cost development with executive-grade default responses.
    """

    def __init__(self, model_name: str = DEFAULT_MODEL_NAME):
        self._model_name = model_name

    @property
    def provider_name(self) -> str:
        return PROVIDER_MOCK

    @property
    def model_name(self) -> str:
        return self._model_name

    async def health_check(self) -> bool:
        return True

    async def list_models(self) -> list[str]:
        """Mock provider reports only its configured model name."""
        return [self._model_name]

    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 2500,
    ) -> str:
        return (
            "Executive Briefing: Revenue has contracted primarily due to escalating customer churn. "
            "Operational processes remain stable, but customer retention interventions require immediate capital and leadership prioritization."
        )

    async def generate_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
    ) -> Dict[str, Any]:
        """
        Synthesizes deterministic structured JSON matching the generator schemas based on prompt keywords.
        """
        p_lower = prompt.lower()

        # Helper to extract context JSON from prompt
        def _extract_ctx() -> Dict[str, Any]:
            try:
                if "```json" in prompt:
                    raw_block = prompt.split("```json")[1].split("```")[0].strip()
                    return json.loads(raw_block)
                elif "```" in prompt:
                    raw_block = prompt.split("```")[1].split("```")[0].strip()
                    return json.loads(raw_block)
            except Exception:
                pass
            return {}

        # 0.0 Phase 9.4: AI Chat Analyst Conversational Dispatcher
        if "task: answer the user's business intelligence question" in p_lower or ("cited_finding_ids" in p_lower and "cited_recommendation_ids" in p_lower):
            ctx_data = _extract_ctx()
            findings = ctx_data.get("findings") or []
            root_causes = ctx_data.get("root_causes") or []
            recommendations = ctx_data.get("recommendations") or []
            h_score = ctx_data.get("business_health_score", 85)
            h_status = ctx_data.get("business_health_status", "HEALTHY")

            f_ids = [str(f.get("id")) for f in findings if f.get("id")]
            rca_ids = [str(r.get("id")) for r in root_causes if r.get("id")]
            rec_ids = [str(r.get("id")) for r in recommendations if r.get("id")]

            p_find = findings[0].get("title") if findings else "operational performance"
            p_rca = root_causes[0].get("cause") if root_causes else "operational friction"
            p_rec = recommendations[0].get("title") if recommendations else "standard execution cadence"

            ans = (
                f"Based on verified diagnostic analysis for this dataset, enterprise performance reflects a Business Health Score of "
                f"{h_score}/100 ({h_status}). Diagnostic telemetry identifies '{p_find}' as the primary operational variance. "
                f"Root-cause attribution confirms this variance is driven by '{p_rca}'. "
                f"To resolve this bottleneck, DecisionOS recommends executing '{p_rec}' to safeguard gross margins and customer retention."
            )

            return {
                "answer": ans,
                "response_type": "ROOT_CAUSE" if "why" in p_lower or "cause" in p_lower else ("RECOMMENDATION" if "recommend" in p_lower or "action" in p_lower else "GENERAL"),
                "cited_finding_ids": f_ids[:2],
                "cited_root_cause_ids": rca_ids[:2],
                "cited_recommendation_ids": rec_ids[:2],
                "cited_forecast_ids": [],
                "cited_scenario_ids": [],
            }

        # 0.0 Phase 9.3: Executive Insight Synthesis Handlers
        if "task: synthesize top strategic business risks" in p_lower or ("top_risks" in p_lower and "source_finding_ids" in p_lower):
            ctx_data = _extract_ctx()
            findings = ctx_data.get("findings") or []
            root_causes = ctx_data.get("root_causes") or []
            risks = []
            if findings:
                for idx, f in enumerate(findings[:3]):
                    title = f.get("title", f"Strategic Risk {idx+1}")
                    sev = str(f.get("severity", "HIGH")).upper()
                    conf = float(f.get("confidence_score", 0.90))
                    f_id = str(f.get("id")) if f.get("id") else f"find-{idx+1}"
                    rca_ids = [str(r.get("id")) for r in root_causes if r.get("id")]
                    risks.append({
                        "title": f"Risk: {title}",
                        "description": (
                            f"Verified diagnostic telemetry confirms that '{title}' constitutes a primary operational risk factor. "
                            f"Diagnostic analysis isolates this variance as an active impediment to baseline performance trajectory, "
                            f"requiring prompt executive review and mitigation."
                        ),
                        "severity": sev if sev in ["CRITICAL", "HIGH", "MEDIUM", "LOW"] else "HIGH",
                        "confidence": conf,
                        "ranking_score": 0.88 - idx * 0.1,
                        "supporting_evidence": [f"Identified anomaly in {title}"],
                        "source_finding_ids": [f_id],
                        "source_root_cause_ids": rca_ids,
                    })
            else:
                risks.append({
                    "title": "Risk: Operational Baseline Drift",
                    "description": (
                        "Baseline business telemetry reflects steady state operations with localized opportunities "
                        "for proactive monitoring to prevent unexpected margin compression across future reporting periods."
                    ),
                    "severity": "LOW",
                    "confidence": 0.90,
                    "ranking_score": 0.35,
                    "supporting_evidence": ["Steady state telemetry"],
                    "source_finding_ids": [],
                    "source_root_cause_ids": [],
                })
            return {"top_risks": risks}

        if "task: synthesize top strategic opportunities" in p_lower or ("top_opportunities" in p_lower and "source_recommendation_ids" in p_lower):
            ctx_data = _extract_ctx()
            recs = ctx_data.get("recommendations") or []
            opps = []
            if recs:
                for idx, r in enumerate(recs[:3]):
                    title = r.get("title", f"Optimization {idx+1}")
                    prio = str(r.get("priority", "HIGH")).upper()
                    conf = float(r.get("confidence_score", 0.92))
                    r_id = str(r.get("id")) if r.get("id") else f"rec-{idx+1}"
                    opps.append({
                        "title": f"Opportunity: {title}",
                        "description": (
                            f"Executing '{title}' represents a significant high-leverage growth and margin stabilization opportunity. "
                            f"Analytical modeling projects that structured implementation will effectively resolve primary diagnostic vulnerabilities "
                            f"and capture measurable top-line operational upside."
                        ),
                        "impact": prio if prio in ["CRITICAL", "HIGH", "MEDIUM", "LOW"] else "HIGH",
                        "confidence": conf,
                        "ranking_score": 0.91 - idx * 0.1,
                        "supporting_evidence": [r.get("rationale") or "Decision rule outcome"],
                        "source_recommendation_ids": [r_id],
                    })
            else:
                opps.append({
                    "title": "Opportunity: Continuous Operational Optimization",
                    "description": (
                        "Enterprise processes indicate opportunities to institutionalize lean standard operating procedures "
                        "and optimize recurring cost structures to sustain competitive advantages and protect healthy gross margins."
                    ),
                    "impact": "MEDIUM",
                    "confidence": 0.85,
                    "ranking_score": 0.60,
                    "supporting_evidence": ["Operational baseline"],
                    "source_recommendation_ids": [],
                })
            return {"top_opportunities": opps}

        if "task: synthesize executive priority actions" in p_lower or ("priority_actions" in p_lower and "expected_impact" in p_lower and "difficulty" in p_lower):
            ctx_data = _extract_ctx()
            recs = ctx_data.get("recommendations") or []
            actions = []
            if recs:
                for idx, r in enumerate(recs[:3]):
                    title = r.get("title", f"Action {idx+1}")
                    prio = str(r.get("priority", "HIGH")).upper()
                    r_id = str(r.get("id")) if r.get("id") else f"rec-{idx+1}"
                    actions.append({
                        "action": title,
                        "priority": prio if prio in ["CRITICAL", "HIGH", "MEDIUM", "LOW"] else "HIGH",
                        "expected_impact": str(r.get("expected_outcome") or "Accelerates operational recovery."),
                        "difficulty": "MODERATE",
                        "ranking_score": 0.89 - idx * 0.1,
                        "rationale": "Directly addresses primary diagnostic telemetry by implementing verified decision rule interventions to restore target KPI baselines.",
                        "source_recommendation_ids": [r_id],
                    })
            else:
                actions.append({
                    "action": "Institutionalize Baseline Operating Cadence",
                    "priority": "MEDIUM",
                    "expected_impact": "Maintains predictable top-line stability and throughput velocity.",
                    "difficulty": "EASY",
                    "ranking_score": 0.55,
                    "rationale": "Maintains organizational velocity and ensures timely identification of emerging diagnostic anomalies.",
                    "source_recommendation_ids": [],
                })
            return {"priority_actions": actions}

        if "task: synthesize high-level strategic themes" in p_lower or ("strategic_themes" in p_lower and "key_pillars" in p_lower):
            ctx_data = _extract_ctx()
            recs = ctx_data.get("recommendations") or []
            rec_titles = [r.get("title", "Initiative") for r in recs]
            return {
                "strategic_themes": [
                    {
                        "theme": "Operational Resilience & Efficiency",
                        "description": "Streamline core business processes and eliminate systemic friction across operating workflows.",
                        "key_pillars": ["Diagnostic telemetry tracking", "Root-cause elimination", "Cross-functional execution"],
                        "aligned_initiatives": rec_titles[:2] if rec_titles else ["Sustain core operating cadence"],
                    },
                    {
                        "theme": "Revenue Protection & Customer Retention",
                        "description": "Protect recurring top-line revenue by proactively mitigating customer churn and contract attrition.",
                        "key_pillars": ["High-touch retention taskforces", "Renewal health monitoring", "Value realization loops"],
                        "aligned_initiatives": rec_titles[2:4] if len(rec_titles) > 2 else ["Customer success audit"],
                    },
                ]
            }

        if "task: synthesize real-time executive alerts" in p_lower or ("executive_alerts" in p_lower and "recommended_immediate_step" in p_lower):
            ctx_data = _extract_ctx()
            findings = ctx_data.get("findings") or []
            alerts = []
            for f in findings:
                sev = str(f.get("severity", "")).upper()
                if sev in ["CRITICAL", "HIGH"]:
                    f_id = str(f.get("id")) if f.get("id") else "find-01"
                    alerts.append({
                        "alert_level": sev,
                        "headline": f"Operational Alert: {f.get('title', 'Variance Detected')}",
                        "detail": str(f.get("description") or "Diagnostic anomaly exceeds standard operational tolerance threshold."),
                        "recommended_immediate_step": "Deploy dedicated triage taskforce and audit upstream causal drivers.",
                        "source_finding_ids": [f_id],
                    })
            if not alerts:
                alerts.append({
                    "alert_level": "INFO",
                    "headline": "System Status: Nominal Operating Telemetry",
                    "detail": "All monitored business indicators reside within expected statistical tolerance parameters.",
                    "recommended_immediate_step": "Maintain standard executive review schedule.",
                    "source_finding_ids": [],
                })
            return {"executive_alerts": alerts}

        if "task: synthesize board-level strategic commentary" in p_lower or ("strategic_outlook" in p_lower and "health_summary" in p_lower):
            ctx_data = _extract_ctx()
            h_score = ctx_data.get("business_health_score", 85)
            h_status = ctx_data.get("business_health_status", "GOOD")
            findings = ctx_data.get("findings") or []
            recommendations = ctx_data.get("recommendations") or []
            p_find = findings[0].get("title") if findings else "operational variance"
            p_rec = recommendations[0].get("title") if recommendations else "standard governance protocols"

            commentary = (
                f"During the current performance evaluation cycle, enterprise operations recorded a composite Business Health Score of "
                f"{h_score} out of 100, reflecting a {h_status.lower()} operational profile across analyzed business divisions. "
                f"Diagnostic telemetry isolated {len(findings)} key performance findings across operational indicators, with primary vulnerability categorized as '{p_find}'. "
                f"Executive leadership must prioritize deploying '{p_rec}' alongside {len(recommendations)} supporting initiatives to accelerate margin recovery, stabilize customer retention, and institutionalize resilient operating standards across corporate divisions. "
                f"The Business Health Score of {h_score}/100 confirms a {h_status.lower()} operating profile with manageable variance and actionable upside potential across upcoming quarters. "
                f"Board oversight should ensure capital and operational capacity remain dedicated to executing strategic priorities on schedule, while monitoring forecasted revenue recovery trends across each key reporting business unit."
            )
            return {
                "headline": f"Board Briefing: Business Health Evaluated at {h_score}/100 ({h_status})",
                "commentary": commentary,
                "strategic_outlook": "Predictable operational trajectory with measurable upside upon execution of prioritized strategic interventions.",
                "health_summary": f"Composite Health Score of {h_score}/100 confirms {h_status} operational profile.",
            }

        # 0.0 Phase 9.2: Executive Narrative Synthesis
        if "task: synthesize executive narrative from verified analytics" in p_lower or ("task: synthesize executive narrative" in p_lower and "key_takeaways" in p_lower) or ("headline" in p_lower and "key_takeaways" in p_lower and "health_assessment" in p_lower):
            ctx_data = _extract_ctx()
            h_score = ctx_data.get("business_health_score", 85)
            h_status = ctx_data.get("business_health_status", "GOOD")
            findings = ctx_data.get("findings") or []
            root_causes = ctx_data.get("root_causes") or []
            recommendations = ctx_data.get("recommendations") or []
            p_find = findings[0].get("title") if findings else "operational stability"
            p_rca = root_causes[0].get("cause") if root_causes else "steady baseline dynamics"
            p_rec = recommendations[0].get("title") if recommendations else "maintain current operational standards"

            return {
                "headline": f"Executive Briefing: Business Health Index Evaluated at {h_score}/100 ({h_status})",
                "executive_summary": (
                    f"During the current performance evaluation cycle, enterprise operations recorded a composite Business Health Score of "
                    f"{h_score} out of 100, reflecting a {h_status.lower()} operational environment across analyzed business streams. "
                    f"Diagnostic analysis isolated {len(findings)} key performance findings across operational indicators. "
                    f"The primary vulnerability impacting top-line outcomes is categorized as '{p_find}', with root-cause causal telemetry "
                    f"attributing this variance directly to '{p_rca}'. Leadership prioritization must concentrate on executing '{p_rec}' "
                    f"alongside {len(recommendations)} supporting initiatives to accelerate margin recovery, stabilize customer retention, "
                    f"and institutionalize resilient operating standards across corporate divisions."
                ),
                "health_assessment": (
                    f"The Business Health Score of {h_score}/100 confirms a {h_status.lower()} operating profile with manageable variance "
                    f"and actionable upside potential across all operational divisions."
                ),
                "key_takeaways": [
                    f"Composite Business Health Index currently evaluated at {h_score}/100 ({h_status}).",
                    f"Primary operational constraint identified: '{p_find}'.",
                    f"Strategic intervention prioritized for executive rollout: '{p_rec}'.",
                ],
                "primary_risk": p_find,
                "recommended_focus": p_rec,
            }

        # 0.1 Phase 9.2: KPI Performance Narrative Synthesis
        if "task: synthesize kpi" in p_lower or ("metric_highlights" in p_lower and "stability_assessment" in p_lower):
            ctx_data = _extract_ctx()
            metrics = ctx_data.get("metrics") or []
            highlights = []
            for m in metrics[:4]:
                name = m.get("name") or m.get("metric_key", "Metric")
                cat = m.get("category", "OPERATIONAL")
                val = m.get("value", 0.0)
                highlights.append({
                    "category": cat,
                    "observation": f"{name} is currently recorded at {val}, reflecting consistent operating velocity.",
                })
            return {
                "summary": (
                    f"Evaluation of {len(metrics)} primary performance metrics across revenue, customer, and operational categories "
                    f"demonstrates consistent underlying business stability. Performance telemetry shows steady operational execution "
                    f"with focused opportunities for margin enhancement and accelerated customer expansion."
                ),
                "metric_highlights": highlights,
                "anomaly_commentary": "Telemetry reveals normal statistical distribution across core operational indicators.",
                "stability_assessment": "STABLE",
            }

        # 0.2 Phase 9.2: Root Cause Narrative Synthesis
        if "task: synthesize root cause" in p_lower or ("primary_drivers" in p_lower and "causal_chain_narrative" in p_lower):
            ctx_data = _extract_ctx()
            rcas = ctx_data.get("root_causes") or []
            drivers = []
            attributions = []
            if rcas:
                for idx, r in enumerate(rcas[:3]):
                    cause = r.get("cause", "Operational Friction")
                    effect = r.get("effect", "Performance Variance")
                    drivers.append({
                        "cause": cause,
                        "effect": effect,
                        "strength": "STRONG",
                        "attribution_percentage": float(65.0 - idx * 15),
                    })
                    attributions.append(f"{cause} accounts for primary variance observed in {effect}.")
            else:
                drivers.append({
                    "cause": "Baseline Operational Steady State",
                    "effect": "Overall Performance",
                    "strength": "MODERATE",
                    "attribution_percentage": 50.0,
                })
                attributions.append("Operational telemetry indicates normal baseline variance across functional areas.")

            p_cause = drivers[0]["cause"]
            p_effect = drivers[0]["effect"]

            return {
                "summary": (
                    f"Causal graph analysis across diagnostic telemetry isolated {len(rcas)} primary root-cause linkages. "
                    f"The dominant systemic driver identified is '{p_cause}', directly influencing '{p_effect}'. "
                    f"Interventions targeting upstream operational drivers will yield systemic recovery across downstream KPIs."
                ),
                "primary_drivers": drivers,
                "causal_chain_narrative": (
                    f"Upstream factor '{p_cause}' propagates directly through operational workflows to trigger '{p_effect}', "
                    f"confirming that targeted root-cause remediation will produce immediate downstream relief."
                ),
                "attribution_breakdown": attributions,
            }

        # 0.3 Phase 9.2: Recommendation Narrative Synthesis
        if "task: synthesize strategic recommendations" in p_lower or ("priority_actions" in p_lower and "expected_impact_narrative" in p_lower):
            ctx_data = _extract_ctx()
            recs = ctx_data.get("recommendations") or []
            actions = []
            for r in recs[:3]:
                actions.append({
                    "title": r.get("title", "Strategic Initiative"),
                    "priority": r.get("priority", "HIGH"),
                    "rationale": r.get("rationale", "Directly targets identified root causes."),
                    "expected_outcome": r.get("expected_outcome", "Restores operational margin and growth."),
                })
            first_rec = actions[0]["title"] if actions else "Operational Stabilization"
            return {
                "summary": (
                    f"Strategic synthesis prioritized {len(recs)} high-leverage initiatives designed to address verified root causes. "
                    f"Immediate leadership focus centers on executing '{first_rec}' to restore baseline operational efficiency "
                    f"and capture measurable top-line improvement across upcoming quarters."
                ),
                "priority_actions": actions,
                "expected_impact_narrative": (
                    "Execution of prioritized interventions is projected to eliminate root-cause bottlenecks and drive "
                    "a 10-15% recovery across primary operating margins."
                ),
                "time_to_value_summary": (
                    "Initial operational triage delivers measurable impact within 30 days, with complete milestone "
                    "institutionalization achieved across 90 days."
                ),
            }

        # 0.4 Phase 9.2: Time-Series Forecast Narrative Synthesis
        if "task: synthesize time-series forecasting" in p_lower or ("horizon_commentary" in p_lower and "confidence_assessment" in p_lower):
            ctx_data = _extract_ctx()
            m_key = ctx_data.get("metric_key", "Core Revenue")
            trend = ctx_data.get("trend_direction", "STABLE")
            return {
                "summary": (
                    f"Statistical forecasting models project a {trend.lower()} trajectory for '{m_key}' across upcoming reporting periods. "
                    f"Baseline projections indicate steady performance continuation under prevailing operating parameters."
                ),
                "trend_direction": trend.upper(),
                "horizon_commentary": (
                    f"Projections across short and medium horizons show steady consistency with historical variance, "
                    f"reinforcing predictable top-line performance."
                ),
                "confidence_assessment": (
                    "Statistical evaluation metrics confirm high prediction confidence with narrow uncertainty intervals."
                ),
                "risk_warnings": [
                    f"Unresolved operational constraints could induce downside volatility to {m_key} projections.",
                    "Sudden shifts in market or customer dynamics may impact baseline trajectories.",
                ],
            }

        # 0.5 Phase 9.2: Scenario Simulation Narrative Synthesis
        if "task: synthesize scenario simulation" in p_lower or ("baseline_vs_scenario_comparison" in p_lower and "strategic_implications" in p_lower):
            ctx_data = _extract_ctx()
            sc_name = ctx_data.get("scenario_name", "Target Strategic Intervention")
            return {
                "summary": (
                    f"Scenario simulation modeling evaluated the business impact of executing '{sc_name}' relative to baseline operations. "
                    f"The projection indicates positive metric acceleration and improved operational resilience."
                ),
                "baseline_vs_scenario_comparison": (
                    "Compared to baseline projections, the simulated intervention drives accelerated metric recovery and "
                    "significantly reduces operational downside exposure."
                ),
                "sensitivity_insights": [
                    f"Execution of {sc_name} delivers robust sensitivity margins across varying operating conditions.",
                    "Resource allocation should be structured to capitalize on projected volume gains.",
                ],
                "strategic_implications": (
                    "Executive leadership is advised to proceed with scenario implementation based on favorable "
                    "risk-adjusted returns."
                ),
            }

        # 0.0 AI Strategy Planner Execution Strategy Generation
        if "task: generate strategic execution plan" in p_lower or ("strategic_priorities" in p_lower and "action_items" in p_lower and "milestones" in p_lower and "success_criteria" in p_lower):

            # Extract context JSON from prompt
            ctx_data = {}
            try:
                if "```json" in prompt:
                    raw_block = prompt.split("```json")[1].split("```")[0].strip()
                    ctx_data = json.loads(raw_block)
                elif "```" in prompt:
                    raw_block = prompt.split("```")[1].split("```")[0].strip()
                    ctx_data = json.loads(raw_block)
            except Exception:
                ctx_data = {}

            recommendations = ctx_data.get("recommendations") or []
            available_kpis = ctx_data.get("available_kpis") or ctx_data.get("metrics") or []
            kpi_keys = [
                k.get("metric_key") or k.get("name")
                for k in available_kpis
                if (k.get("metric_key") or k.get("name"))
            ]
            valid_kpi = kpi_keys[0] if kpi_keys else "recurring_revenue"

            # If no recommendations exist, return empty
            if not recommendations:
                return {
                    "title": "Strategic Execution Plan",
                    "objective": "Operationalize recommendations into time-phased execution roadmap.",
                    "executive_summary": "No approved recommendations available to formulate a strategy plan.",
                    "strategic_priorities": [],
                    "action_items": [],
                    "milestones": [],
                    "success_criteria": [],
                    "source_recommendation_ids": [],
                }

            rec_ids = [str(r.get("id")) for r in recommendations if r.get("id")]
            rec_titles = [r.get("title", "Strategic Initiative") for r in recommendations]
            first_id = rec_ids[0] if rec_ids else "rec-001"
            first_title = rec_titles[0] if rec_titles else "Operational Initiative"
            first_priority = recommendations[0].get("priority", "HIGH")

            return {
                "title": f"Strategic Execution Plan: {first_title}",
                "objective": f"Systematically operationalize '{first_title}' and supporting interventions across 90-day time horizons.",
                "executive_summary": (
                    f"This executive strategy translates approved DecisionOS recommendation '{first_title}' "
                    f"into immediate, 30-day, 60-day, and 90-day operational milestones. "
                    f"By focusing execution on root causes and tracking performance via existing KPI '{valid_kpi}', "
                    f"the business establishes clear accountability and time-to-value."
                ),
                "strategic_priorities": [
                    {
                        "title": f"Execute {first_title}",
                        "priority": first_priority,
                        "source_recommendation_ids": [first_id],
                        "rationale": f"High impact intervention prioritized to address primary operational diagnostic findings.",
                    }
                ],
                "action_items": [
                    {
                        "title": f"Phase 1 Triage & Setup for {first_title}",
                        "description": "Establish dedicated cross-functional taskforce and audit operational bottlenecks.",
                        "time_horizon": "IMMEDIATE",
                        "source_recommendation_id": first_id,
                        "dependencies": [],
                    },
                    {
                        "title": f"Deploy Core Workflows for {first_title}",
                        "description": "Roll out primary execution steps and enable live operational telemetry.",
                        "time_horizon": "30_DAYS",
                        "source_recommendation_id": first_id,
                        "dependencies": [f"Phase 1 Triage & Setup for {first_title}"],
                    },
                    {
                        "title": f"Scale and Calibrate {first_title}",
                        "description": "Iterate operational processes and expand coverage across target customer cohorts.",
                        "time_horizon": "60_DAYS",
                        "source_recommendation_id": first_id,
                        "dependencies": [],
                    },
                    {
                        "title": f"Institutionalize & Review {first_title}",
                        "description": "Formally institutionalize standard operating procedures and evaluate outcome ROI.",
                        "time_horizon": "90_DAYS",
                        "source_recommendation_id": first_id,
                        "dependencies": [],
                    },
                ],
                "milestones": [
                    {
                        "title": "Immediate Operational Alignment",
                        "time_horizon": "IMMEDIATE",
                        "focus_area": "Preparation & Ownership",
                        "key_deliverables": ["Taskforce chartered", "Root cause audit complete"],
                        "success_criteria": ["Operational readiness 100%"],
                    },
                    {
                        "title": "30-Day Deployment Milestone",
                        "time_horizon": "30_DAYS",
                        "focus_area": "Initial Rollout",
                        "key_deliverables": ["Pilot workflows live", "Initial feedback loop active"],
                        "success_criteria": [f"Initial stability observed in {valid_kpi}"],
                    },
                    {
                        "title": "60-Day Calibration Milestone",
                        "time_horizon": "60_DAYS",
                        "focus_area": "Process Optimization",
                        "key_deliverables": ["Mid-point performance review", "Workflow adjustments deployed"],
                        "success_criteria": [f"Measurable improvement trajectory in {valid_kpi}"],
                    },
                    {
                        "title": "90-Day Full Outcome Evaluation",
                        "time_horizon": "90_DAYS",
                        "focus_area": "Sustained Stabilization",
                        "key_deliverables": ["Final retrospective report", "Permanent SOP established"],
                        "success_criteria": [f"Target baseline restored for {valid_kpi}"],
                    },
                ],
                "success_criteria": [
                    {
                        "metric_key": valid_kpi,
                        "target_direction": "IMPROVE",
                        "source": "existing_kpi",
                        "rationale": f"Primary corporate KPI utilized to track recovery outcomes from {first_title}.",
                    }
                ],
                "source_recommendation_ids": rec_ids,
            }

        # 0. AI Chat Analyst Conversational Queries (Evaluated first to avoid context substring collisions)
        if "user question:" in p_lower or "task: answer the user's business question" in p_lower or ("sources" in p_lower and "answer" in p_lower and "confidence" in p_lower):
            # Attempt to extract context JSON from prompt
            ctx_data = {}
            try:
                if "```json" in prompt:
                    raw_block = prompt.split("```json")[1].split("```")[0].strip()
                    ctx_data = json.loads(raw_block)
                elif "```" in prompt:
                    raw_block = prompt.split("```")[1].split("```")[0].strip()
                    ctx_data = json.loads(raw_block)
            except Exception:
                ctx_data = {}

            # Extract dynamic artifacts from context
            findings = ctx_data.get("findings") or []
            root_causes = ctx_data.get("root_causes") or []
            recommendations = ctx_data.get("recommendations") or []
            health_score = ctx_data.get("business_health_score")
            health_status = ctx_data.get("business_health_status")
            primary_issue = ctx_data.get("primary_issue", "No primary issue")

            # If completely empty context or no evidence available
            if not findings and not root_causes and not recommendations and health_score is None:
                return {
                    "answer": "DecisionOS does not currently have sufficient evidence to answer this question.",
                    "confidence": 0.0,
                    "sources": [],
                }

            sources = []
            f_title = findings[0].get("title", "Diagnostic Finding") if findings else primary_issue
            if findings:
                sources.append(f"finding:{findings[0].get('title', 'Primary Finding')}")
            if root_causes:
                rc_name = root_causes[0].get("cause") or root_causes[0].get("root_cause_title") or "Root Cause Analysis"
                sources.append(f"rca:{rc_name}")
            if recommendations:
                sources.append(f"rec:{recommendations[0].get('title', 'Actionable Recommendation')}")

            # Grounded conversational responses
            if "health" in p_lower or "score" in p_lower or "doing" in p_lower:
                answer = (
                    f"Your current business health score is {health_score}, placing the business in {health_status} status. "
                    f"The primary concern flagged is '{primary_issue}'. "
                )
                if recommendations:
                    answer += f"The highest-priority recommendation available to address this is '{recommendations[0].get('title')}'. "
            elif "why" in p_lower and ("revenue" in p_lower or "decline" in p_lower or "drop" in p_lower or "down" in p_lower):
                answer = f"Revenue is under pressure primarily due to '{f_title}'. "
                if root_causes:
                    rc_exp = root_causes[0].get("explanation") or root_causes[0].get("cause")
                    answer += f"The root cause analysis directly attributes this to {rc_exp}. "
                if recommendations:
                    answer += f"DecisionOS recommends implementing '{recommendations[0].get('title')}' as an immediate countermeasure."
            elif "risk" in p_lower:
                answer = f"The most critical operational risk identified is '{f_title}'. "
                if root_causes:
                    answer += f"Root cause telemetry confirms this is driven by '{root_causes[0].get('cause', 'underlying operational friction')}'. "
                if recommendations:
                    answer += f"Mitigation should focus on '{recommendations[0].get('title')}'. "
            elif "prioriti" in p_lower or "focus" in p_lower or "action" in p_lower or "what should" in p_lower or "next" in p_lower:
                if recommendations:
                    rec = recommendations[0]
                    answer = (
                        f"Based on existing DecisionOS recommendation priorities, you should focus first on '{rec.get('title')}'. "
                        f"This initiative has a priority of {rec.get('priority', 'HIGH')} with an estimated impact score of {rec.get('impact', 0.85)}."
                    )
                else:
                    answer = f"To address '{f_title}', immediate focus should be directed toward operational stabilization."
            elif "churn" in p_lower or "customer" in p_lower:
                answer = f"Customer retention is flagged because '{f_title}' is impacting business performance. "
                if root_causes:
                    answer += f"Root cause diagnostic analysis links this behavior to '{root_causes[0].get('cause', 'operational delays')}'. "
                if recommendations:
                    answer += f"The recommended initiative is '{recommendations[0].get('title')}'. "
            else:
                answer = (
                    f"Based on DecisionOS intelligence, the primary operational focus is '{primary_issue}'. "
                    f"Business health is currently at {health_score}/100 ({health_status}). "
                )
                if recommendations:
                    answer += f"Top recommended action: '{recommendations[0].get('title')}'. "

            return {
                "answer": answer.strip(),
                "confidence": 0.89,
                "sources": sources,
            }

        # 1. Executive Narrative
        if "executive_narrative" in p_lower or "executive summary" in p_lower or "headline" in p_lower:
            return {
                "headline": "Strategic Contraction Driven by Customer Churn Requires Immediate Retention Focus",
                "executive_summary": (
                    "Over the observed operating period, enterprise performance experienced measurable headwinds. "
                    "Diagnostic telemetry isolates top-line decline directly to accelerating customer cancellations. "
                    "Core cost and fulfillment operations remain structurally resilient, creating a window to reverse churn trends through targeted retention."
                ),
                "primary_issue_summary": (
                    "Quarterly revenue decline is directly caused by elevated customer churn. "
                    "Stabilizing subscriber cohort retention is the primary requirement to restore baseline trajectory."
                ),
                "health_assessment": (
                    "Corporate health is categorized in Watch List status. "
                    "While systemic failure is absent, unmitigated churn will compound margin compression within 60-90 days."
                ),
            }

        # 2. Business Assessment
        if "business_assessment" in p_lower or "strengths" in p_lower or "weaknesses" in p_lower:
            return {
                "strengths": [
                    "Operating fulfillment and order throughput maintain stable baseline efficiency.",
                    "Product gross margins remain resilient against cost fluctuations.",
                    "Core enterprise client segments display predictable recurring order patterns.",
                ],
                "weaknesses": [
                    "Customer churn has accelerated beyond normal operating tolerance thresholds.",
                    "Concentration risk in top-tier product catalog lines increases volatility.",
                    "LTV to CAC efficiency has declined across recent acquisition cohorts.",
                ],
                "revenue_observations": [
                    "Top-line contraction is highly correlated with lost account ARR.",
                    "Average order value (AOV) has held steady despite volume contraction.",
                ],
                "customer_observations": [
                    "Early-tenure customer cohorts exhibit the highest attrition velocity.",
                    "Net promoter feedback points to onboarding friction and service touchpoints.",
                ],
                "operational_observations": [
                    "Cost structures are controlled with no severe unexpected cost spikes.",
                    "Delivery cycles meet standard SLAs without significant fulfillment backlogs.",
                ],
                "product_observations": [
                    "Flagship offerings generate majority revenue, indicating low catalog diversification.",
                    "Secondary product lines suffer from under-penetration in existing customer accounts.",
                ],
            }

        # 3. Risk Analysis
        if "risk_analysis" in p_lower or "top_risks" in p_lower or "overall_risk_level" in p_lower:
            return {
                "overall_risk_level": "ELEVATED",
                "top_risks": [
                    {
                        "title": "Compounding Customer Churn",
                        "severity": "CRITICAL",
                        "likelihood": "HIGH",
                        "business_impact": "Accelerated loss of recurring revenue and margin erosion over next 2 quarters.",
                        "mitigation_summary": "Deploy proactive customer success interventions and win-back campaigns.",
                    },
                    {
                        "title": "Product Concentration Exposure",
                        "severity": "HIGH",
                        "likelihood": "MEDIUM",
                        "business_impact": "Disproportionate revenue impact if primary product line encounters market shifts.",
                        "mitigation_summary": "Accelerate cross-selling and secondary product tier promotions.",
                    },
                    {
                        "title": "Acquisition Cost Inefficiency",
                        "severity": "MEDIUM",
                        "likelihood": "MEDIUM",
                        "business_impact": "Sub-optimal marketing ROI while onboarding churn-prone accounts.",
                        "mitigation_summary": "Refine ICP targeting criteria to prioritize high-retention segments.",
                    },
                ],
            }

        # 4. Opportunity Assessment
        if "opportunity" in p_lower or "growth_opportunities" in p_lower:
            return {
                "growth_opportunities": [
                    {
                        "title": "Targeted Customer Retention Campaign",
                        "category": "GROWTH",
                        "estimated_value": "Recovers estimated 15-20% of at-risk subscription run-rate ARR.",
                        "description": "Engage high-risk churn accounts with customized renewal incentives and tailored success plans.",
                    },
                ],
                "efficiency_opportunities": [
                    {
                        "title": "Automated Onboarding Sequence",
                        "category": "EFFICIENCY",
                        "estimated_value": "Reduces early-stage support ticket volume by 25%.",
                        "description": "Streamline new account setup workflows to accelerate time-to-first-value.",
                    },
                ],
                "customer_opportunities": [
                    {
                        "title": "Tiered Loyalty & Retention Incentives",
                        "category": "CUSTOMER",
                        "estimated_value": "Improves repeat purchase frequency by 10-15%.",
                        "description": "Introduce structured milestone rewards for multi-month active subscribers.",
                    },
                ],
                "revenue_opportunities": [
                    {
                        "title": "Win-Back Campaign for Inactive Cohorts",
                        "category": "REVENUE",
                        "estimated_value": "Reactivates 8-12% of churned accounts within 45 days.",
                        "description": "Deliver tailored win-back messaging and re-activation discounts to dormant accounts.",
                    },
                ],
            }

        # 5. Strategic Priorities
        if "strategic_priorities" in p_lower or "immediate_priorities" in p_lower:
            return {
                "immediate_priorities": [
                    {
                        "title": "Launch Churn Interception Taskforce",
                        "priority_tier": "IMMEDIATE",
                        "timeframe": "1-7 days",
                        "rationale": "Directly halts ongoing ARR bleed in most vulnerable accounts.",
                        "expected_impact": "Immediate stabilization of cancellation volume.",
                    },
                ],
                "short_term_priorities": [
                    {
                        "title": "Deploy Customer Loyalty & Win-Back Programs",
                        "priority_tier": "HIGH",
                        "timeframe": "30 days",
                        "rationale": "Creates structured retention mechanics across middle-tier cohorts.",
                        "expected_impact": "Measurable lift in 30-day retention and repeat order rates.",
                    },
                ],
                "medium_term_priorities": [
                    {
                        "title": "Diversify Product Catalog & Cross-Sell",
                        "priority_tier": "MEDIUM",
                        "timeframe": "60-90 days",
                        "rationale": "Reduces reliance on single product lines and increases account LTV.",
                        "expected_impact": "Broadened revenue base and expanded customer lifetime value.",
                    },
                ],
                "prioritization_rationale": (
                    "Immediate focus is placed on halting churn because top-line erosion undermines all other expansion efforts. "
                    "Once cohort retention is stabilized, capital can safely be deployed into loyalty and catalog diversification."
                ),
            }

        # 6. Action Plan Roadmap (90 Days)
        if "action_plan" in p_lower or "immediate_actions" in p_lower or "90-day" in p_lower:
            return {
                "immediate_actions": {
                    "phase_name": "Immediate Triage",
                    "timeframe": "Days 1-7",
                    "key_actions": [
                        "Audit top 50 at-risk client accounts by usage decline.",
                        "Establish executive customer success outreach protocol.",
                        "Freeze aggressive acquisition spend on underperforming channels.",
                    ],
                    "expected_milestones": [
                        "Complete risk audits for top churn cohorts.",
                        "Deploy initial emergency retention offers.",
                    ],
                },
                "days_30_milestones": {
                    "phase_name": "Foundational Stabilization",
                    "timeframe": "Days 8-30",
                    "key_actions": [
                        "Launch automated email retention sequence for at-risk cohorts.",
                        "Roll out win-back incentives to recently churned customers.",
                        "Implement weekly customer health scoring dashboards.",
                    ],
                    "expected_milestones": [
                        "Attain 10% reduction in weekly churn rate.",
                        "Reactivate minimum 5% of dormant accounts.",
                    ],
                },
                "days_60_milestones": {
                    "phase_name": "Program Expansion",
                    "timeframe": "Days 31-60",
                    "key_actions": [
                        "Launch structured loyalty and rewards program.",
                        "Introduce cross-sell bundles to established customer accounts.",
                        "Refine ICP onboarding flows based on retention learnings.",
                    ],
                    "expected_milestones": [
                        "Loyalty program adoption reaches 20% of active base.",
                        "Repeat purchase rate improves by 8%.",
                    ],
                },
                "days_90_milestones": {
                    "phase_name": "Scale & Optimization",
                    "timeframe": "Days 61-90",
                    "key_actions": [
                        "Evaluate 90-day retention cohort outcomes against baseline.",
                        "Institutionalize revised customer journey protocols.",
                        "Resume disciplined acquisition scaling on high-retention channels.",
                    ],
                    "expected_milestones": [
                        "Restore business health score to Healthy (>75) tier.",
                        "Full recovery of lost recurring revenue run-rate.",
                    ],
                },
                "success_criteria": [
                    "Reduction in overall customer churn rate below 12%.",
                    "Quarterly revenue recovery reaching >= 15% improvement over baseline.",
                    "Business health score index improved to >= 80/100.",
                ],
            }

        # Generic fallback
        return {
            "headline": "Business Intelligence Summary",
            "summary": "Analysis completed successfully.",
        }
