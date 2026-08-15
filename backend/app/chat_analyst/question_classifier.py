"""Question Classifier categorizing user queries to optimize targeted retrieval."""

import re
from typing import Tuple
from app.chat_analyst.constants import QuestionType, ResponseType


class QuestionClassifier:
    """
    Deterministic rule-based intent classifier analyzing user queries to guide
    targeted intelligence retrieval and token-efficient context compression.
    """

    # Keyword patterns mapped to QuestionType & ResponseType
    FORECAST_PATTERNS = [
        r"\bforecast\b",
        r"\bproject\b",
        r"\bprojection\b",
        r"\boutlook\b",
        r"\bnext month\b",
        r"\bnext quarter\b",
        r"\bfuture\b",
        r"\btrend\b",
        r"\bpredict\b",
        r"\bprediction\b",
    ]

    ROOT_CAUSE_PATTERNS = [
        r"\bwhy\b",
        r"\bcause\b",
        r"\broot cause\b",
        r"\bdriver\b",
        r"\breason\b",
        r"\battribution\b",
        r"\bdecline\b",
        r"\bdrop\b",
        r"\bdecrease\b",
        r"\bcontraction\b",
        r"\bvariance\b",
        r"\bchurn\b",
    ]

    RECOMMENDATION_PATTERNS = [
        r"\brecommend\b",
        r"\brecommendation\b",
        r"\baction\b",
        r"\binitiative\b",
        r"\bwhat should we do\b",
        r"\bhow to fix\b",
        r"\bmitigat\w*\b",
        r"\bpriorit\w*\b",
        r"\bopportunit\w*\b",
        r"\bquick win\b",
    ]

    SCENARIO_PATTERNS = [
        r"\bscenario\b",
        r"\bsimulat\w*\b",
        r"\bwhat if\b",
        r"\bestimate impact\b",
        r"\bif we increase\b",
        r"\bif we decrease\b",
        r"\bif we change\b",
    ]

    HEALTH_SCORE_PATTERNS = [
        r"\bhealth\b",
        r"\bhealth score\b",
        r"\bbusiness health\b",
        r"\boverall status\b",
        r"\bhow are we doing\b",
        r"\bhealth index\b",
        r"\bperformance index\b",
    ]

    @classmethod
    def classify(cls, question: str) -> Tuple[QuestionType, ResponseType]:
        """
        Classifies a user question string into QuestionType and corresponding default ResponseType.
        """
        q_lower = (question or "").lower().strip()

        # Check in priority order
        if any(re.search(pat, q_lower) for pat in cls.SCENARIO_PATTERNS):
            return QuestionType.SCENARIO_QUESTION, ResponseType.SCENARIO

        if any(re.search(pat, q_lower) for pat in cls.FORECAST_PATTERNS):
            return QuestionType.FORECAST_QUESTION, ResponseType.FORECAST

        if any(re.search(pat, q_lower) for pat in cls.RECOMMENDATION_PATTERNS):
            return QuestionType.RECOMMENDATION_QUESTION, ResponseType.RECOMMENDATION

        if any(re.search(pat, q_lower) for pat in cls.HEALTH_SCORE_PATTERNS):
            return QuestionType.HEALTH_SCORE_QUESTION, ResponseType.HEALTH_SCORE

        if any(re.search(pat, q_lower) for pat in cls.ROOT_CAUSE_PATTERNS):
            return QuestionType.ROOT_CAUSE_QUESTION, ResponseType.ROOT_CAUSE

        return QuestionType.GENERAL_BUSINESS_QUESTION, ResponseType.GENERAL
