"""PromptBuilder formulating standardized, guardrailed executive narrative prompts."""

import json
from typing import Any, Dict
from app.narratives.constants import NARRATIVE_PROMPT_VERSION

NARRATIVE_SYSTEM_PROMPT = f"""You are an Executive Business Intelligence Advisor and Chief Strategy Officer at DecisionOS.
Your responsibility is to translate deterministic business telemetry, diagnostics, and predictive models into boardroom-ready executive narratives.

STRICT GUARDRAILS (Prompt Version {NARRATIVE_PROMPT_VERSION}):
1. Ground every claim ONLY in the provided structured context facts below.
2. DO NOT invent or hallucinate metrics, percentages, root causes, or ungrounded recommendations.
3. DO NOT infer missing facts or extrapolate speculative trends outside the supplied data.
4. DO NOT recalculate or contradict the provided Health Score, Finding Severities, or Causal DAG relationships.
5. Maintain a professional, objective, assertive, and executive-level tone.
6. ALWAYS respond in valid, well-formed JSON matching the specified schema format precisely.
"""


class NarrativePromptBuilder:
    """
    Constructs standardized, guardrailed prompts for the 6 specialized AI narrative perspectives.
    """

    @classmethod
    def get_system_prompt(cls) -> str:
        return NARRATIVE_SYSTEM_PROMPT

    @classmethod
    def to_json_str(cls, data: Any) -> str:
        """Serializes context dictionary to clean JSON string with sorted keys."""
        return json.dumps(data, indent=2, default=str)

    @classmethod
    def build_executive_summary_prompt(cls, context: Dict[str, Any]) -> str:
        context_json = cls.to_json_str(context)
        return f"""Task: Synthesize Executive Narrative and Boardroom Briefing.

Analyze the structured corporate context below:
```json
{context_json}
```

Required JSON Output Schema:
{{
  "headline": "<Board-level summary headline>",
  "executive_summary": "<Comprehensive 2-3 paragraph executive narrative detailing trajectory, core drivers, and leadership focus>",
  "health_assessment": "<Qualitative interpretation of the business health score and stability index>",
  "key_takeaways": [
    "<High-level takeaway 1>",
    "<High-level takeaway 2>",
    "<High-level takeaway 3>"
  ],
  "primary_risk": "<Concise explanation of the single primary operational or financial risk>",
  "recommended_focus": "<Key recommended strategic intervention for executive leadership>"
}}

Respond ONLY in valid JSON matching this schema."""

    @classmethod
    def build_kpi_prompt(cls, context: Dict[str, Any]) -> str:
        context_json = cls.to_json_str(context)
        return f"""Task: Synthesize KPI Performance Narrative.

Analyze the structured corporate context below:
```json
{context_json}
```

Required JSON Output Schema:
{{
  "summary": "<2-paragraph executive narrative explaining metric movements, growth vs contraction, and performance across functional domains>",
  "metric_highlights": [
    {{
      "category": "<REVENUE | CUSTOMER | OPERATIONAL | PRODUCT>",
      "observation": "<Specific metric observation based on provided values>"
    }}
  ],
  "anomaly_commentary": "<Commentary on metric volatility, spikes, or anomalous drops observed in data>",
  "stability_assessment": "<Assessment of whether overall metric performance is STABLE, VOLATILE, or ACCELERATING>"
}}

Respond ONLY in valid JSON matching this schema."""

    @classmethod
    def build_root_cause_prompt(cls, context: Dict[str, Any]) -> str:
        context_json = cls.to_json_str(context)
        return f"""Task: Synthesize Root Cause Analysis Narrative.

Analyze the structured corporate context below:
```json
{context_json}
```

Required JSON Output Schema:
{{
  "summary": "<2-paragraph narrative synthesizing primary root causes, mechanism of failure, and organizational impact>",
  "primary_drivers": [
    {{
      "cause": "<Identified root cause>",
      "effect": "<Primary affected metric or diagnostic finding>",
      "strength": "<STRONG | MODERATE | WEAK>",
      "attribution_percentage": <Estimated impact percentage or relative weight>
    }}
  ],
  "causal_chain_narrative": "<Step-by-step narrative explaining the causal chain path from upstream trigger to downstream symptom>",
  "attribution_breakdown": [
    "<Attribution statement 1>",
    "<Attribution statement 2>"
  ]
}}

Respond ONLY in valid JSON matching this schema."""

    @classmethod
    def build_recommendation_prompt(cls, context: Dict[str, Any]) -> str:
        context_json = cls.to_json_str(context)
        return f"""Task: Synthesize Strategic Recommendations Narrative.

Analyze the structured corporate context below:
```json
{context_json}
```

Required JSON Output Schema:
{{
  "summary": "<2-paragraph executive narrative outlining strategic intervention plan and prioritization rationale>",
  "priority_actions": [
    {{
      "title": "<Action title>",
      "priority": "<HIGH | MEDIUM | LOW>",
      "rationale": "<Why this action addresses the discovered root causes>",
      "expected_outcome": "<Expected business impact>"
    }}
  ],
  "expected_impact_narrative": "<Narrative explaining overall projected ROI, business turnaround, and margin recovery>",
  "time_to_value_summary": "<Summary of short-term (30d) vs medium-term (90d) time-to-value milestones>"
}}

Respond ONLY in valid JSON matching this schema."""

    @classmethod
    def build_forecast_prompt(cls, context: Dict[str, Any]) -> str:
        context_json = cls.to_json_str(context)
        return f"""Task: Synthesize Time-Series Forecasting Narrative.

Analyze the structured forecast context below:
```json
{context_json}
```

Required JSON Output Schema:
{{
  "summary": "<2-paragraph executive narrative explaining baseline projected trajectory over upcoming reporting periods>",
  "trend_direction": "<GROWING | DECLINING | STABLE>",
  "horizon_commentary": "<Detailed timeline breakdown across short and medium-term forecast horizons>",
  "confidence_assessment": "<Qualitative commentary on prediction intervals and forecast statistical confidence>",
  "risk_warnings": [
    "<Downside risk warning 1>",
    "<Downside risk warning 2>"
  ]
}}

Respond ONLY in valid JSON matching this schema."""

    @classmethod
    def build_scenario_prompt(cls, context: Dict[str, Any]) -> str:
        context_json = cls.to_json_str(context)
        return f"""Task: Synthesize Scenario Simulation Narrative.

Analyze the structured scenario simulation context below:
```json
{context_json}
```

Required JSON Output Schema:
{{
  "summary": "<2-paragraph executive narrative comparing simulated scenario against baseline trajectory>",
  "baseline_vs_scenario_comparison": "<Direct comparative analysis detailing projected delta, revenue recovery, or efficiency gains>",
  "sensitivity_insights": [
    "<Sensitivity insight 1>",
    "<Sensitivity insight 2>"
  ],
  "strategic_implications": "<Boardroom implications on whether leadership should execute the simulated intervention>"
}}

Respond ONLY in valid JSON matching this schema."""
