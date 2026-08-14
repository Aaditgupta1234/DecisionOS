"""StrategyPromptBuilder formulating standardized, guardrailed prompts for the Strategic Execution Planner."""

from typing import Any, Dict
from app.strategy_planner.builders.strategy_context_builder import StrategyContextBuilder

STRATEGY_SYSTEM_PROMPT = """You are the DecisionOS Strategic Execution Planner.
You transform approved DecisionOS recommendations into an executive-grade, time-phased strategic execution plan.

STRICT GUARDRAILS & PLANNING INSTRUCTIONS:
1. The recommendations provided in the structured context are authoritative. You MUST NOT create new recommendations.
2. Every strategic action item MUST explicitly trace to an existing `source_recommendation_id` present in the context.
3. Success criteria MUST use ONLY existing DecisionOS `metric_key`s provided in the `available_kpis` allowlist. DO NOT invent new KPI keys.
4. Structure the execution roadmap across four explicit time horizons:
   - IMMEDIATE (Days 1 - 7): Triage, taskforce mobilization, baseline audits.
   - 30_DAYS (Days 8 - 30): Primary deployment, pilot workflow rollout, initial telemetry.
   - 60_DAYS (Days 31 - 60): Scale, process optimization, mid-point telemetry review.
   - 90_DAYS (Days 61 - 90): Sustained outcome evaluation, standard operating procedure (SOP) institutionalization.
5. DO NOT fabricate financial numbers, business constraints, or unsupported ROI claims.
6. Use concise, executive-grade business language.
7. ALWAYS respond ONLY in valid, well-formed JSON matching the specified schema format precisely.
"""


class StrategyPromptBuilder:
    """
    Constructs low-hallucination, traceability-enforced prompts for strategic execution plans.
    """

    @classmethod
    def get_system_prompt(cls) -> str:
        return STRATEGY_SYSTEM_PROMPT

    @classmethod
    def build_strategy_prompt(cls, context: Dict[str, Any]) -> str:
        context_json = StrategyContextBuilder.to_json_str(context)

        return f"""Task: Generate a strategic execution plan based strictly on the approved DecisionOS recommendations and available KPI telemetry below.

Structured Corporate Context:
```json
{context_json}
```

Required JSON Output Schema:
{{
  "title": "<Executive Headline for the Strategic Execution Plan>",
  "objective": "<Concise overarching strategic objective>",
  "executive_summary": "<Comprehensive executive strategic narrative explaining the transformation of recommendations into milestones>",
  "strategic_priorities": [
    {{
      "title": "<Priority Headline>",
      "priority": "<LOW | MEDIUM | HIGH | CRITICAL>",
      "source_recommendation_ids": ["<source recommendation UUID string>"],
      "rationale": "<Strategic justification linking to diagnostic findings>"
    }}
  ],
  "action_items": [
    {{
      "title": "<Specific Action Item Title>",
      "description": "<Detailed operational instructions>",
      "time_horizon": "<IMMEDIATE | 30_DAYS | 60_DAYS | 90_DAYS>",
      "source_recommendation_id": "<exact source recommendation UUID from context>",
      "dependencies": ["<optional dependency action title>"]
    }}
  ],
  "milestones": [
    {{
      "title": "<Milestone Headline>",
      "time_horizon": "<IMMEDIATE | 30_DAYS | 60_DAYS | 90_DAYS>",
      "focus_area": "<Operational Focus Area>",
      "key_deliverables": ["<Deliverable 1>", "<Deliverable 2>"],
      "success_criteria": ["<Qualitative checkpoint criterion>"]
    }}
  ],
  "success_criteria": [
    {{
      "metric_key": "<exact metric_key from available_kpis in context>",
      "target_direction": "<IMPROVE | INCREASE | DECREASE | STABILIZE | MAINTAIN>",
      "source": "existing_kpi",
      "rationale": "<How this KPI validates execution outcome>"
    }}
  ],
  "source_recommendation_ids": ["<all recommendation UUIDs utilized in this plan>"]
}}

Respond ONLY in valid JSON matching this schema."""
