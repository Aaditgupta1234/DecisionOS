"""
Phase 8.2: Enterprise Integration Models
"""
from sqlalchemy import Column, String, Float, Integer, Boolean, JSON, DateTime, Text
from sqlalchemy.sql import func
from app.core.database import Base


class EnterpriseConnector(Base):
    __tablename__ = "enterprise_connectors"

    id = Column(String, primary_key=True, index=True)
    connector_type = Column(String, nullable=False)  # SALESFORCE, HUBSPOT, SAP, ORACLE, JIRA, SERVICENOW, SLACK, TEAMS
    name = Column(String, nullable=False)
    status = Column(String, default="CONNECTED")  # CONNECTED, SYNCING, ERROR, DISCONNECTED
    auth_type = Column(String, default="OAUTH2")
    sync_frequency = Column(String, default="HOURLY")
    records_synced = Column(Integer, default=0)
    last_sync_at = Column(DateTime(timezone=True), server_default=func.now())
    config_metadata = Column(JSON, default=dict)
    health_rating = Column(Float, default=99.8)


class IntegrationSyncLog(Base):
    __tablename__ = "integration_sync_logs"

    id = Column(String, primary_key=True, index=True)
    connector_id = Column(String, nullable=False)
    sync_status = Column(String, default="SUCCESS")
    records_processed = Column(Integer, default=0)
    duration_ms = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
