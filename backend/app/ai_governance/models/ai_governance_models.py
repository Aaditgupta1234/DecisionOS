"""
Phase 8.4: AI Usage & Prompt Governance Models
"""
from sqlalchemy import Column, String, Float, Integer, Boolean, JSON, DateTime, Text
from sqlalchemy.sql import func
from app.core.database import Base


class AIInteractionAudit(Base):
    __tablename__ = "ai_interaction_audits"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, nullable=False)
    user_role = Column(String, default="EXECUTIVE")
    prompt_text = Column(Text, nullable=False)
    response_text = Column(Text, nullable=False)
    grounded_urns = Column(JSON, default=list)
    model_name = Column(String, default="gemini-1.5-pro")
    prompt_tokens = Column(Integer, default=420)
    completion_tokens = Column(Integer, default=180)
    latency_ms = Column(Integer, default=240)
    cost_usd = Column(Float, default=0.002)
    hallucination_check = Column(String, default="PASSED")
    evidence_coverage_pct = Column(Float, default=96.4)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
