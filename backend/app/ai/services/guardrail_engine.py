"""AI Safety Guardrail Engine for Phase 6.0."""

import re
from app.ai.schemas.ai_schemas import GuardrailEvaluationResponse


class GuardrailEngine:
    """Evaluates query boundaries to prevent the AI from speculating outside verified data."""

    UNSUPPORTED_PATTERNS = [
        r"stock market",
        r"share price",
        r"interest rate in 203\d",
        r"revenue in 203\d",
        r"weather",
        r"crypto",
        r"bitcoin",
        r"lottery",
    ]

    @classmethod
    def evaluate_query(cls, query: str) -> GuardrailEvaluationResponse:
        """
        Classifies query into: SUPPORTED, PARTIALLY_SUPPORTED, INSUFFICIENT_EVIDENCE, OUT_OF_SCOPE.
        """
        normalized = query.lower()

        # Check for out of scope queries
        for pat in cls.UNSUPPORTED_PATTERNS:
            if re.search(pat, normalized):
                return GuardrailEvaluationResponse(
                    query_text=query,
                    guardrail_status="OUT_OF_SCOPE",
                    is_safe_to_execute=False,
                    rationale="Query requires unverified external forecasting or speculative market data outside DecisionOS deterministic models.",
                )

        # Check for non-existent historical horizon
        if "2035" in normalized or "2040" in normalized:
            return GuardrailEvaluationResponse(
                query_text=query,
                guardrail_status="INSUFFICIENT_EVIDENCE",
                is_safe_to_execute=False,
                rationale="DecisionOS causal knowledge graph does not contain verified forecasts beyond available snapshot horizons.",
            )

        return GuardrailEvaluationResponse(
            query_text=query,
            guardrail_status="SUPPORTED",
            is_safe_to_execute=True,
            rationale="Query is grounded in verified DecisionOS telemetry, causal DAGs, and optimization runs.",
        )
