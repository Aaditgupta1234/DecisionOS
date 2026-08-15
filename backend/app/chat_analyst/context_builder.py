"""Context Builder compiling sanitized, token-budgeted conversational context."""

import json
from typing import Any, Dict
from app.chat_analyst.constants import MAX_CONTEXT_TOKENS, QuestionType
from app.chat_analyst.context_compressor import ContextCompressor


class ChatContextBuilder:
    """
    Constructs compact, JSON-serializable analytical context payloads for prompt injection.
    """

    @classmethod
    def build_chat_context(
        cls,
        raw_bundle: Dict[str, Any],
        question_type: QuestionType,
    ) -> Dict[str, Any]:
        """
        Builds compressed, verified context for the LLM prompt.
        """
        compressed = ContextCompressor.compress(raw_bundle=raw_bundle, question_type=question_type)
        return compressed

    @classmethod
    def estimate_token_count(cls, text_or_dict: Any) -> int:
        """Rough token approximation (~4 characters per token)."""
        if isinstance(text_or_dict, dict):
            s = json.dumps(text_or_dict, default=str)
        else:
            s = str(text_or_dict)
        return max(1, len(s) // 4)
