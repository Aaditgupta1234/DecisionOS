"""Intent Classification Engine for Phase 6.0."""

import re
from typing import Tuple


class IntentClassifier:
    """Classifies natural language executive queries into 10 deterministic intent categories."""

    INTENT_MAP = [
        (r"(stock|crypto|bitcoin|weather|2035|2040)", "UNSUPPORTED_QUERY"),
        (r"(compare|difference|changed?(\s+between)?|versus|vs\.?|diff|evolv)", "COMPARISON_QUERY"),
        (r"(arr|revenue|dollar|recovered|outcome|yield|roi)", "OUTCOME_QUERY"),
        (r"(why|cause|root\s*cause|reason|origin)", "ROOT_CAUSE_QUERY"),
        (r"(recommend|fix|address|action|suggest|solution)", "RECOMMENDATION_QUERY"),
        (r"(forecast|project|predict|q4|trajectory|quarter)", "FORECAST_QUERY"),
        (r"(simulate|what\s*if|monte\s*carlo|digital\s*twin|scenario)", "SIMULATION_QUERY"),
        (r"(alert|drift|warning|anomaly|critical)", "ALERT_QUERY"),
        (r"(initiative|init-|execution|kanban|task|progress)", "INITIATIVE_QUERY"),
    ]

    @classmethod
    def classify(cls, query: str) -> Tuple[str, float]:
        """
        Returns (intent_classification, confidence_score).
        """
        normalized = query.lower().strip()

        for pattern, intent in cls.INTENT_MAP:
            if re.search(pattern, normalized):
                return intent, 0.94

        return "GENERAL_EXPLAINABILITY_QUERY", 0.90
