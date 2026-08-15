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
