"""Guardrailed Prompt Builder for Phase 9.4 AI Chat Analyst."""

import json
from typing import Any, Dict, List
from app.chat_analyst.constants import CHAT_PROMPT_VERSION, CHAT_SCHEMA_VERSION
from app.chat_analyst.conversation_memory import ConversationMemory

CHAT_SYSTEM_PROMPT = f"""You are the Explainable AI Business Analyst for DecisionOS, an enterprise intelligence SaaS platform.
Prompt Version: {CHAT_PROMPT_VERSION} | Schema Version: {CHAT_SCHEMA_VERSION}

CRITICAL RULES & GUARDRAILS:
1. Ground every answer STRICTLY in the provided analytical context (KPIs, findings, root causes, recommendations, forecasts, scenarios, health scores).
2. DO NOT invent, guess, hallucinate, extrapolate, or assume metrics, causes, or outcomes outside the context.
3. NEVER perform raw mathematical calculations or fabricate new metric values.
4. STRICTLY PROHIBITED phrases: "I think", "I believe", "probably", "maybe", "likely because", "outside the dataset", "assume", "in my opinion", "I suspect", "I guess", "based on external knowledge".
5. For all analytical assertions, you MUST cite the relevant source UUIDs in the cited_*_ids arrays.
6. If the requested information is not available in the context, clearly state that DecisionOS has no verified evidence on this topic.
7. Return ONLY valid, parseable JSON matching the schema below without extra text or markdown outside code fences."""


class ChatPromptBuilder:
    """Constructs guardrailed prompts for the AI Chat Analyst."""

    @classmethod
    def get_system_prompt(cls) -> str:
        """Returns the canonical system prompt with anti-hallucination guardrails."""
        return CHAT_SYSTEM_PROMPT

    @classmethod
    def build_chat_prompt(
        cls,
        question: str,
        context: Dict[str, Any],
        history: List[Dict[str, str]],
    ) -> str:
        """
        Builds the complete inference prompt combining context, memory history, and question.
        """
        ctx_json = json.dumps(context, indent=2, default=str)
        history_text = ConversationMemory.to_prompt_block(history)

        return f"""Task: Answer the user's business intelligence question using ONLY verified telemetry.

Verified Business Intelligence Context:
```json
{ctx_json}
```

Recent Conversation History:
{history_text}

Current User Question:
"{question}"

Required JSON Output Schema:
{{
  "answer": "<20-250 word direct, professional analytical answer grounded entirely in the context>",
  "response_type": "ROOT_CAUSE" | "FORECAST" | "SCENARIO" | "RECOMMENDATION" | "HEALTH_SCORE" | "GENERAL",
  "cited_finding_ids": ["<UUID string of finding>"],
  "cited_root_cause_ids": ["<UUID string of RCA>"],
  "cited_recommendation_ids": ["<UUID string of recommendation>"],
  "cited_forecast_ids": ["<UUID string of forecast>"],
  "cited_scenario_ids": ["<UUID string of scenario>"]
}}

Respond ONLY in valid JSON matching this schema."""
