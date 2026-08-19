"""
Phase 8.5: Scheduled Delivery Models
"""
from sqlalchemy import Column, String, Float, Integer, Boolean, JSON, DateTime, Text
from sqlalchemy.sql import func
from app.core.database import Base


class ScheduledDelivery(Base):
    __tablename__ = "scheduled_deliveries"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    cadence = Column(String, nullable=False)  # DAILY, WEEKLY_MONDAY, MONTHLY_FIRST, POST_BOARD_REVIEW
    channel = Column(String, nullable=False)  # EMAIL, SLACK, MS_TEAMS, PDF_BUNDLE
    target_recipients = Column(JSON, default=list)
    format = Column(String, default="EXECUTIVE_PDF_AND_SLACK")
    status = Column(String, default="ACTIVE")
    last_dispatched_at = Column(DateTime(timezone=True), server_default=func.now())
