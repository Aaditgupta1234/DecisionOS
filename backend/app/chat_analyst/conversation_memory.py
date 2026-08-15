"""Conversation Memory managing recent interaction turns and token budgeting."""

from typing import Any, Dict, List
from app.chat_analyst.constants import MAX_HISTORY_MESSAGES
from app.chat_analyst.models.chat_message import ChatMessage
from app.core.constants import ChatMessageRole


class ConversationMemory:
    """
    Maintains rolling conversational memory window for contextual continuity
    without overflowing LLM prompt token limits.
    """

    @classmethod
    def format_history(cls, messages: List[ChatMessage]) -> List[Dict[str, str]]:
        """
        Formats recent chat messages into standard role/content dictionaries.
        """
        recent = messages[-MAX_HISTORY_MESSAGES:] if len(messages) > MAX_HISTORY_MESSAGES else messages
        formatted = []
        for m in recent:
            role_str = "user" if m.role == ChatMessageRole.USER or str(m.role).lower().endswith("user") else "assistant"
            formatted.append({
                "role": role_str,
                "content": m.content,
            })
        return formatted

    @classmethod
    def to_prompt_block(cls, formatted_history: List[Dict[str, str]]) -> str:
        """Renders formatted history into a human-readable prompt string."""
        if not formatted_history:
            return "No previous conversation history."

        lines = []
        for item in formatted_history:
            speaker = "User" if item["role"] == "user" else "Assistant"
            lines.append(f"{speaker}: {item['content']}")
        return "\n".join(lines)
