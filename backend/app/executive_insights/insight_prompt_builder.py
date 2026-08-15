"""Guardrailed prompt builder for Phase 9.3: Executive Insight Generator."""

import json
from typing import Any, Dict

from app.executive_insights.constants import (
    INSIGHT_PROMPT_VERSION,
    INSIGHT_SCHEMA_VERSION,
)

INSIGHT_SYSTEM_PROMPT = f"""You are the Executive Insight Engine for DecisionOS, an Explainable AI Business Intelligence Platform.
Prompt Version: {INSIGHT_PROMPT_VERSION} | Schema Version: {INSIGHT_SCHEMA_VERSION}

STRICT GUARDRAILS:
1. ONLY utilize the supplied structured intelligence context (KPIs, Diagnostic Findings, Root Cause Analyses, Recommendations, Forecasts, Scenarios, Business Health Scores, and Narrative Reports).
2. DO NOT invent, infer, speculate, or extrapolate beyond the provided data.
3. NEVER perform raw mathematical calculations or fabricate new metric values.
4. STRICTLY PROHIBITED phrases: "I believe", "I think", "probably", "maybe", "likely because", "outside the dataset", "assume", "in my opinion", "I suspect", "I guess".
5. For all risks and opportunities, reference the exact source finding IDs, root cause IDs, or recommendation IDs provided in the context.
6. Return purely valid, parseable JSON matching the exact schema requested without preamble or markdown commentary outside code blocks."""


class ExecutiveInsightPromptBuilder:
    """Standardized prompt builder constructing guardrailed prompts for Executive Insights."""

    @classmethod
    def get_system_prompt(cls) -> str:
        """Returns the canonical system prompt with strict anti-hallucination guardrails."""
        return INSIGHT_SYSTEM_PROMPT

    @classmethod
    def _context_to_json(cls, context: Dict[str, Any]) -> str:
        return json.dumps(context, indent=2, default=str)

    @classmethod
    def build_top_risks_prompt(cls, context: Dict[str, Any]) -> str:
        ctx_json = cls._context_to_json(context)
        return f"""Task: Synthesize Top Strategic Business Risks from verified diagnostic findings and causal links.

Structured Analytics Telemetry:
```json
{ctx_json}
```

Required JSON Output Schema:
{{
  "top_risks": [
    {{
      "title": "<Concise risk title>",
      "description": "<20-100 word rigorous analytical description based on findings>",
      "severity": "CRITICAL" | "HIGH" | "MEDIUM" | "LOW",
      "confidence": <float 0.0 - 1.0>,
      "supporting_evidence": ["<Specific finding title, metric value, or causal link>"],
      "source_finding_ids": ["<UUID string of finding>"],
      "source_root_cause_ids": ["<UUID string of RCA>"]
    }}
  ]
}}

Respond ONLY in valid JSON matching this schema."""

    @classmethod
    def build_top_opportunities_prompt(cls, context: Dict[str, Any]) -> str:
        ctx_json = cls._context_to_json(context)
        return f"""Task: Synthesize Top Strategic Opportunities from verified recommendations and scenario trajectories.

Structured Analytics Telemetry:
```json
{ctx_json}
```

Required JSON Output Schema:
{{
  "top_opportunities": [
    {{
      "title": "<Concise opportunity headline>",
      "description": "<20-100 word rigorous opportunity summary>",
      "impact": "CRITICAL" | "HIGH" | "MEDIUM" | "LOW",
      "confidence": <float 0.0 - 1.0>,
      "supporting_evidence": ["<Specific recommendation outcome or forecast upside>"],
      "source_recommendation_ids": ["<UUID string of recommendation>"]
    }}
  ]
}}

Respond ONLY in valid JSON matching this schema."""

    @classmethod
    def build_priority_actions_prompt(cls, context: Dict[str, Any]) -> str:
        ctx_json = cls._context_to_json(context)
        return f"""Task: Synthesize Executive Priority Actions from prioritized recommendations.

Structured Analytics Telemetry:
```json
{ctx_json}
```

Required JSON Output Schema:
{{
  "priority_actions": [
    {{
      "action": "<Direct actionable initiative name>",
      "priority": "CRITICAL" | "HIGH" | "MEDIUM" | "LOW",
      "expected_impact": "<Projected return, e.g. 'Halts $150K ARR churn deficit'>",
      "difficulty": "EASY" | "MODERATE" | "DIFFICULT",
      "rationale": "<Explainability justification linking finding to action>",
      "source_recommendation_ids": ["<UUID string of recommendation>"]
    }}
  ]
}}

Respond ONLY in valid JSON matching this schema."""

    @classmethod
    def build_strategic_themes_prompt(cls, context: Dict[str, Any]) -> str:
        ctx_json = cls._context_to_json(context)
        return f"""Task: Synthesize High-Level Strategic Themes categorizing business performance imperatives.

Structured Analytics Telemetry:
```json
{ctx_json}
```

Required JSON Output Schema:
{{
  "strategic_themes": [
    {{
      "theme": "<Theme Name e.g. Customer Retention, Operational Efficiency, Revenue Growth>",
      "description": "<Executive framing and business scope>",
      "key_pillars": ["<Pillar 1>", "<Pillar 2>"],
      "aligned_initiatives": ["<Aligned initiative title 1>", "<Aligned initiative title 2>"]
    }}
  ]
}}

Respond ONLY in valid JSON matching this schema."""

    @classmethod
    def build_executive_alerts_prompt(cls, context: Dict[str, Any]) -> str:
        ctx_json = cls._context_to_json(context)
        return f"""Task: Synthesize Real-Time Executive Alerts from critical findings and volatile metrics.

Structured Analytics Telemetry:
```json
{ctx_json}
```

Required JSON Output Schema:
{{
  "executive_alerts": [
    {{
      "alert_level": "CRITICAL" | "WARNING" | "INFO",
      "headline": "<Crisp alert headline>",
      "detail": "<Contextual explanation of trigger event>",
      "recommended_immediate_step": "<Actionable triage or containment step>",
      "source_finding_ids": ["<UUID string of finding>"]
    }}
  ]
}}

Respond ONLY in valid JSON matching this schema."""

    @classmethod
    def build_board_commentary_prompt(cls, context: Dict[str, Any]) -> str:
        ctx_json = cls._context_to_json(context)
        return f"""Task: Synthesize Board-Level Strategic Commentary and Governance Briefing.

Structured Analytics Telemetry:
```json
{ctx_json}
```

Required JSON Output Schema:
{{
  "headline": "<Board-level summary headline>",
  "commentary": "<100-250 word comprehensive governance narrative summarizing performance, primary risks, and strategic mandates>",
  "strategic_outlook": "<Qualitative forward-looking assessment across next 2 quarters>",
  "health_summary": "<Business Health Score contextualization>"
}}

Respond ONLY in valid JSON matching this schema."""

    @classmethod
    def build_full_package_prompt(cls, context: Dict[str, Any]) -> str:
        ctx_json = cls._context_to_json(context)
        return f"""Task: Synthesize Complete Executive Insights Package from structured intelligence and narrative reports.

Structured Analytics Telemetry:
```json
{ctx_json}
```

Required JSON Output Schema:
{{
  "executive_summary": "<Executive summary narrative>",
  "top_risks": [
    {{
      "title": "<Risk title>",
      "description": "<20-100 word description>",
      "severity": "CRITICAL" | "HIGH" | "MEDIUM" | "LOW",
      "confidence": <float 0.0 - 1.0>,
      "supporting_evidence": ["<Evidence bullet>"],
      "source_finding_ids": ["<UUID string>"],
      "source_root_cause_ids": ["<UUID string>"]
    }}
  ],
  "top_opportunities": [
    {{
      "title": "<Opportunity headline>",
      "description": "<20-100 word summary>",
      "impact": "CRITICAL" | "HIGH" | "MEDIUM" | "LOW",
      "confidence": <float 0.0 - 1.0>,
      "supporting_evidence": ["<Evidence bullet>"],
      "source_recommendation_ids": ["<UUID string>"]
    }}
  ],
  "priority_actions": [
    {{
      "action": "<Action name>",
      "priority": "CRITICAL" | "HIGH" | "MEDIUM" | "LOW",
      "expected_impact": "<Expected impact>",
      "difficulty": "EASY" | "MODERATE" | "DIFFICULT",
      "rationale": "<Rationale>",
      "source_recommendation_ids": ["<UUID string>"]
    }}
  ],
  "strategic_themes": [
    {{
      "theme": "<Theme name>",
      "description": "<Description>",
      "key_pillars": ["<Pillar>"],
      "aligned_initiatives": ["<Initiative>"]
    }}
  ],
  "executive_alerts": [
    {{
      "alert_level": "CRITICAL" | "WARNING" | "INFO",
      "headline": "<Headline>",
      "detail": "<Detail>",
      "recommended_immediate_step": "<Step>",
      "source_finding_ids": ["<UUID string>"]
    }}
  ],
  "board_commentary": {{
    "headline": "<Headline>",
    "commentary": "<100-250 word commentary>",
    "strategic_outlook": "<Outlook>",
    "health_summary": "<Health summary>"
  }}
}}

Respond ONLY in valid JSON matching this schema."""
