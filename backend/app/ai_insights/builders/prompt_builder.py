"""PromptBuilder formulating standardized, low-hallucination executive prompts."""

from typing import Any, Dict
from app.ai_insights.builders.context_builder import ContextBuilder

SYSTEM_PROMPT = """You are a Senior Strategic Advisor and Chief Strategy Officer at a top-tier management consultancy.
Your responsibility is to translate deterministic business telemetry, diagnostics, and recommendations into crisp, boardroom-ready executive insights.

STRICT GUARDRAILS:
1. Ground every claim ONLY in the provided structured context.
2. DO NOT invent or hallucinate metrics, percentages, root causes, or ungrounded recommendations.
3. DO NOT recalculate or contradict the provided Health Score, Finding Severities, or Causal DAG.
4. Maintain an objective, assertive, and executive-level tone.
5. ALWAYS respond in valid, well-formed JSON matching the specified schema format precisely.
"""


class PromptBuilder:
    """
    Constructs standardized, guardrailed prompts for the 6 specialized AI insight generators.
    """

    @classmethod
    def get_system_prompt(cls) -> str:
        return SYSTEM_PROMPT

    @classmethod
    def build_executive_narrative_prompt(cls, context: Dict[str, Any]) -> str:
        context_json = ContextBuilder.to_json_str(context)
        return f"""Task: Synthesize the Executive Narrative and Board Briefing.

Analyze the structured corporate context below:
```json
{context_json}
```

Required JSON Output Schema:
{{
  "headline": "<Board-level summary headline>",
  "executive_summary": "<Comprehensive 2-3 paragraph executive narrative detailing trajectory, core drivers, and leadership focus>",
  "primary_issue_summary": "<Concise explanation of the single primary operational/financial risk>",
  "health_assessment": "<Qualitative interpretation of the business health score and stability index>"
}}

Respond ONLY in valid JSON matching this schema."""

    @classmethod
    def build_business_assessment_prompt(cls, context: Dict[str, Any]) -> str:
        context_json = ContextBuilder.to_json_str(context)
        return f"""Task: Generate a comprehensive Business Assessment across functional domains.

Analyze the structured corporate context below:
```json
{context_json}
```

Required JSON Output Schema:
{{
  "strengths": ["<Validated business strength based on positive metrics/stable areas>", ...],
  "weaknesses": ["<Identified vulnerability based on diagnostic findings>", ...],
  "revenue_observations": ["<Key observation on top-line trend, margin, or ARR dynamics>", ...],
  "customer_observations": ["<Observation on retention, churn, concentration, or cohort behavior>", ...],
  "operational_observations": ["<Observation on process efficiency, delivery SLAs, or cost structures>", ...],
  "product_observations": ["<Observation on catalog mix, product concentration, or offering performance>", ...]
}}

Respond ONLY in valid JSON matching this schema."""

    @classmethod
    def build_risk_analysis_prompt(cls, context: Dict[str, Any]) -> str:
        context_json = ContextBuilder.to_json_str(context)
        return f"""Task: Formulate the Enterprise Risk Matrix and vulnerability ranking.

Analyze the structured corporate context below:
```json
{context_json}
```

Required JSON Output Schema:
{{
  "overall_risk_level": "<CRITICAL | ELEVATED | MODERATE | LOW>",
  "top_risks": [
    {{
      "title": "<Concise risk title>",
      "severity": "<CRITICAL | HIGH | MEDIUM | LOW>",
      "likelihood": "<HIGH | MEDIUM | LOW>",
      "business_impact": "<Projected business and financial downside if unmitigated>",
      "mitigation_summary": "<Countermeasure derived directly from recommendations>"
    }}
  ]
}}

Respond ONLY in valid JSON matching this schema."""

    @classmethod
    def build_opportunity_prompt(cls, context: Dict[str, Any]) -> str:
        context_json = ContextBuilder.to_json_str(context)
        return f"""Task: Identify categorized growth and operational efficiency opportunities.

Analyze the structured corporate context below:
```json
{context_json}
```

Required JSON Output Schema:
{{
  "growth_opportunities": [
    {{
      "title": "<Opportunity title>",
      "category": "GROWTH",
      "estimated_value": "<Projected top-line recovery or growth narrative>",
      "description": "<Implementation pathway grounded in recommendations>"
    }}
  ],
  "efficiency_opportunities": [
    {{
      "title": "<Efficiency title>",
      "category": "EFFICIENCY",
      "estimated_value": "<Projected cost or time savings>",
      "description": "<Operational streamlining step>"
    }}
  ],
  "customer_opportunities": [
    {{
      "title": "<Customer value title>",
      "category": "CUSTOMER",
      "estimated_value": "<Retention or LTV expansion upside>",
      "description": "<Customer engagement pathway>"
    }}
  ],
  "revenue_opportunities": [
    {{
      "title": "<Revenue initiative title>",
      "category": "REVENUE",
      "estimated_value": "<Recovery or pricing gain estimate>",
      "description": "<Monetization and win-back action>"
    }}
  ]
}}

Respond ONLY in valid JSON matching this schema."""

    @classmethod
    def build_strategic_priority_prompt(cls, context: Dict[str, Any]) -> str:
        context_json = ContextBuilder.to_json_str(context)
        return f"""Task: Sequence strategic executive priorities by urgency, impact, and effort.

Analyze the structured corporate context below:
```json
{context_json}
```

Required JSON Output Schema:
{{
  "immediate_priorities": [
    {{
      "title": "<Immediate action title>",
      "priority_tier": "IMMEDIATE",
      "timeframe": "1-7 days",
      "rationale": "<Why this takes precedence>",
      "expected_impact": "<Direct near-term return>"
    }}
  ],
  "short_term_priorities": [
    {{
      "title": "<Short-term action title>",
      "priority_tier": "HIGH",
      "timeframe": "30 days",
      "rationale": "<Core execution rationale>",
      "expected_impact": "<Stabilization milestone>"
    }}
  ],
  "medium_term_priorities": [
    {{
      "title": "<Medium-term action title>",
      "priority_tier": "MEDIUM",
      "timeframe": "60-90 days",
      "rationale": "<Structural transformation rationale>",
      "expected_impact": "<Long-term expansion return>"
    }}
  ],
  "prioritization_rationale": "<Strategic narrative explaining the overall sequencing of initiatives>"
}}

Respond ONLY in valid JSON matching this schema."""

    @classmethod
    def build_action_plan_prompt(cls, context: Dict[str, Any]) -> str:
        context_json = ContextBuilder.to_json_str(context)
        return f"""Task: Synthesize the 90-Day Execution Roadmap grounded purely in approved recommendations.

Analyze the structured corporate context below:
```json
{context_json}
```

Required JSON Output Schema:
{{
  "immediate_actions": {{
    "phase_name": "Immediate Interventions",
    "timeframe": "Days 1-7",
    "key_actions": ["<Action 1>", ...],
    "expected_milestones": ["<Milestone 1>", ...]
  }},
  "days_30_milestones": {{
    "phase_name": "Foundational Stabilization",
    "timeframe": "Days 8-30",
    "key_actions": ["<Action 1>", ...],
    "expected_milestones": ["<Milestone 1>", ...]
  }},
  "days_60_milestones": {{
    "phase_name": "Program Acceleration",
    "timeframe": "Days 31-60",
    "key_actions": ["<Action 1>", ...],
    "expected_milestones": ["<Milestone 1>", ...]
  }},
  "days_90_milestones": {{
    "phase_name": "Measurement & Scale",
    "timeframe": "Days 61-90",
    "key_actions": ["<Action 1>", ...],
    "expected_milestones": ["<Milestone 1>", ...]
  }},
  "success_criteria": ["<Key metric target or health index threshold to measure success>", ...]
}}

Respond ONLY in valid JSON matching this schema."""
