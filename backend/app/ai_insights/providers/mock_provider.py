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
