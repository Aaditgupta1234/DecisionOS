"""
Phase 8.1: Boardroom Intelligence Domain Models
"""
from sqlalchemy import Column, String, Float, Integer, Boolean, JSON, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from app.core.database import Base


class ExecutiveBriefing(Base):
    __tablename__ = "executive_briefings"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    briefing_type = Column(String, nullable=False)  # MONTHLY_PACK, QBR, RISK_REVIEW, STRATEGY_UPDATE
    period = Column(String, nullable=False)  # "Q1 2026", "April 2026"
    status = Column(String, default="APPROVED")  # DRAFT, IN_REVIEW, APPROVED, PUBLISHED
    executive_summary = Column(Text, nullable=False)
    key_takeaways = Column(JSON, default=list)
    kpi_highlights = Column(JSON, default=dict)
    confidence_score = Column(Float, default=95.4)
    author_role = Column(String, default="Chief Decision Officer (AI-Synthesized)")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class BoardReport(Base):
    __tablename__ = "board_reports"

    id = Column(String, primary_key=True, index=True)
    report_code = Column(String, unique=True, index=True)  # "BRP-2026-Q1"
    title = Column(String, nullable=False)
    quarter = Column(String, nullable=False)  # "Q1 2026"
    composite_health_score = Column(Float, default=85.0)
    realized_arr_growth = Column(Float, default=312000.0)
    decision_accuracy = Column(Float, default=91.8)
    capital_allocation_roi = Column(Float, default=6.02)
    deck_slides = Column(JSON, default=list)
    published_at = Column(DateTime(timezone=True), server_default=func.now())


class BoardMeetingPackage(Base):
    __tablename__ = "board_meeting_packages"

    id = Column(String, primary_key=True, index=True)
    package_code = Column(String, unique=True, index=True)  # "BMP-2026-Q1-ANNUAL"
    meeting_date = Column(String, nullable=False)  # "2026-04-15"
    title = Column(String, nullable=False)
    agenda_items = Column(JSON, default=list)
    included_briefings = Column(JSON, default=list)
    signoff_status = Column(String, default="SIGNED_OFF_BY_CEO")  # PENDING, SIGNED_OFF_BY_CEO, BOARD_APPROVED
    signed_by = Column(String, default="Alexander Vance (CEO)")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
