"""Pydantic v2 schemas for Phase 10.5: Operational Monitoring & Health Center."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.monitoring.constants import (
    AlertSeverity,
    AlertSource,
    ComponentCategory,
    ComponentStatus,
    MONITORING_VERSION,
    SystemHealthStatus,
)


class ComponentHealth(BaseModel):
    """Health diagnostic status for an individual platform subsystem."""
    component_name: str
    component_category: str = ComponentCategory.OPERATIONAL.value
    status: ComponentStatus
    component_version: Optional[str] = None
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    latency_ms: Optional[float] = None
    last_activity_at: Optional[datetime] = None
    sample_size: int = 0
    telemetry_available: bool = True
    message: str
    diagnostics: Dict[str, Any] = Field(default_factory=dict)


class SystemHealthSummary(BaseModel):
    """Aggregated platform health summary."""
    overall_status: SystemHealthStatus
    components: List[ComponentHealth]
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    evaluation_duration_ms: float = 0.0
    monitoring_version: str = MONITORING_VERSION
    organization_id: UUID


class JobOperationalSummary(BaseModel):
    """Telemetry summary for Background Job subsystem (Phase 10.1)."""
    total_jobs: int = 0
    running_jobs: int = 0
    completed_jobs: int = 0
    failed_jobs: int = 0
    cancelled_jobs: int = 0
    consecutive_failures: int = 0
    success_rate_percent: float = 100.0
    last_activity_at: Optional[datetime] = None
    avg_duration_seconds: Optional[float] = None
    p50_duration_seconds: Optional[float] = None
    p95_duration_seconds: Optional[float] = None
    p99_duration_seconds: Optional[float] = None


class ScheduleOperationalSummary(BaseModel):
    """Telemetry summary for Scheduled Intelligence subsystem (Phase 10.4)."""
    total_schedules: int = 0
    active_schedules: int = 0
    paused_schedules: int = 0
    total_runs: int = 0
    successful_runs: int = 0
    failed_runs: int = 0
    consecutive_failures: int = 0
    success_rate_percent: float = 100.0
    last_activity_at: Optional[datetime] = None
    p50_duration_ms: Optional[float] = None
    p95_duration_ms: Optional[float] = None
    p99_duration_ms: Optional[float] = None


class NotificationOperationalSummary(BaseModel):
    """Telemetry summary for Notification Framework (Phase 10.2)."""
    total_notifications: int = 0
    unread_count: int = 0
    read_count: int = 0
    archived_count: int = 0
    delivery_failure_count: int = 0
    last_activity_at: Optional[datetime] = None


class AuditOperationalSummary(BaseModel):
    """Telemetry summary for Audit Center (Phase 10.3)."""
    total_events: int = 0
    event_distribution: Dict[str, int] = Field(default_factory=dict)
    failed_actions_count: int = 0
    recent_activity_count: int = 0
    last_activity_at: Optional[datetime] = None


class OperationalAlertItem(BaseModel):
    """Deduplicated operational alert item with deterministic fingerprint."""
    alert_key: str
    severity: AlertSeverity
    source: AlertSource
    message: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = Field(default_factory=dict)


class OperationalDashboardResponse(BaseModel):
    """Unified operations and monitoring dashboard response."""
    organization_id: UUID
    system_health: SystemHealthSummary
    jobs: JobOperationalSummary
    schedules: ScheduleOperationalSummary
    notifications: NotificationOperationalSummary
    audit: AuditOperationalSummary
    alerts: List[OperationalAlertItem] = Field(default_factory=list)
    active_alert_count: int = 0
    lookback_hours: int = 24
    cached: bool = False
    monitoring_version: str = MONITORING_VERSION
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
