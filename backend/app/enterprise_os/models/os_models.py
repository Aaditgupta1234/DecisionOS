"""SQLAlchemy Models for Phase 6.7–6.9 Unified Enterprise Governance, Competitive Intelligence & OS Platform."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.base import TimestampMixin


# ==============================================================================
# PHASE 6.7: ENTERPRISE DECISION REGISTRY, GOVERNANCE & COMPLIANCE
# ==============================================================================

class EnterpriseDecision(TimestampMixin, Base):
    """Permanent corporate decision memory recording every strategic and financial decision."""

    __tablename__ = "enterprise_decisions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    portfolio_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )

    decision_code: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    decision_type: Mapped[str] = mapped_column(
        String(50),
        default="STRATEGIC",
        nullable=False,  # STRATEGIC, FINANCIAL, OPERATIONAL, BOARD
    )

    decision_owner: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )

    owner_role: Mapped[str] = mapped_column(
        String(50),
        default="CFO",
        nullable=False,
    )

    business_case: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    expected_value: Mapped[float] = mapped_column(
        Float,
        default=340000.0,
        nullable=False,
    )

    approved_value: Mapped[Optional[float]] = mapped_column(
        Float,
        default=340000.0,
        nullable=True,
    )

    actual_value: Mapped[Optional[float]] = mapped_column(
        Float,
        default=312000.0,
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="APPROVED",
        nullable=False,  # DRAFT, UNDER_REVIEW, APPROVED, BLOCKED, IMPLEMENTED
    )


class DecisionOutcomeAttribution(TimestampMixin, Base):
    """Attribution connecting realized business value back to the originating executive decision."""

    __tablename__ = "decision_outcome_attributions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    decision_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("enterprise_decisions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    initiative_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )

    expected_arr: Mapped[float] = mapped_column(
        Float,
        default=340000.0,
        nullable=False,
    )

    realized_arr: Mapped[float] = mapped_column(
        Float,
        default=312000.0,
        nullable=False,
    )

    decision_accuracy_pct: Mapped[float] = mapped_column(
        Float,
        default=91.8,
        nullable=False,
    )

    attribution_confidence: Mapped[float] = mapped_column(
        Float,
        default=95.4,
        nullable=False,
    )

    strategic_alignment_score: Mapped[float] = mapped_column(
        Float,
        default=96.0,
        nullable=False,
    )

    attributed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )


class DecisionApproval(TimestampMixin, Base):
    """Governance decision compliance gate evaluation and risk status."""

    __tablename__ = "decision_approvals"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    decision_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("enterprise_decisions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    approval_status: Mapped[str] = mapped_column(
        String(50),
        default="APPROVED",
        nullable=False,  # APPROVED, BLOCKED, UNDER_REVIEW
    )

    risk_score: Mapped[float] = mapped_column(
        Float,
        default=24.0,
        nullable=False,
    )

    compliance_status: Mapped[str] = mapped_column(
        String(50),
        default="COMPLIANT",
        nullable=False,  # COMPLIANT, VIOLATION_BLOCKED
    )

    approved_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )

    approved_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )


class PolicyRule(TimestampMixin, Base):
    """Enforceable governance constraint rule (e.g. risk envelope or financial authority)."""

    __tablename__ = "policy_rules"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    rule_code: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    rule_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    rule_type: Mapped[str] = mapped_column(
        String(50),
        default="FINANCIAL",
        nullable=False,  # FINANCIAL, RISK, COMPLIANCE, BOARD_DIRECTIVE
    )

    condition_expression: Mapped[str] = mapped_column(
        String(255),
        default="risk_score < 75.0 AND budget <= 500000",
        nullable=False,
    )

    enforcement_level: Mapped[str] = mapped_column(
        String(50),
        default="HARD_BLOCK",
        nullable=False,  # HARD_BLOCK, SOFT_WARNING
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )


class ComplianceViolation(TimestampMixin, Base):
    """Violation record logged when a proposed decision breaches active policy rules."""

    __tablename__ = "compliance_violations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    decision_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("enterprise_decisions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    policy_rule_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("policy_rules.id", ondelete="CASCADE"),
        nullable=False,
    )

    violation_severity: Mapped[str] = mapped_column(
        String(50),
        default="HIGH",
        nullable=False,  # CRITICAL, HIGH, MEDIUM
    )

    violation_reason: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    remediation_required: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    is_resolved: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    detected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )


class HumanOverrideRecord(TimestampMixin, Base):
    """Audit log recorded when executive leadership overrides AI recommendations."""

    __tablename__ = "human_override_records"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    decision_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("enterprise_decisions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    ai_recommendation: Mapped[str] = mapped_column(
        String(100),
        default="REJECT / HEDGE",
        nullable=False,
    )

    human_decision: Mapped[str] = mapped_column(
        String(100),
        default="APPROVED",
        nullable=False,
    )

    overridden_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )

    override_role: Mapped[str] = mapped_column(
        String(50),
        default="CEO",
        nullable=False,
    )

    override_rationale: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )


class DecisionAuditRecord(TimestampMixin, Base):
    """Formal audit trail verifying governance, compliance, and realized value."""

    __tablename__ = "decision_audit_records"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    decision_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("enterprise_decisions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    approver_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )

    approver_role: Mapped[str] = mapped_column(
        String(50),
        default="Board Chair / CEO",
        nullable=False,
    )

    rationale: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    expected_value_arr: Mapped[float] = mapped_column(
        Float,
        default=340000.0,
        nullable=False,
    )

    realized_value_arr: Mapped[Optional[float]] = mapped_column(
        Float,
        default=312000.0,
        nullable=True,
    )

    forecast_accuracy_pct: Mapped[float] = mapped_column(
        Float,
        default=95.2,
        nullable=False,
    )

    compliance_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )


# ==============================================================================
# PHASE 6.8: BENCHMARKING, COMPETITIVE INTELLIGENCE & SCENARIOS
# ==============================================================================

class BenchmarkSource(TimestampMixin, Base):
    """External or industry data source verifying benchmark provenance and freshness."""

    __tablename__ = "benchmark_sources"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    source_name: Mapped[str] = mapped_column(
        String(100),
        default="SaaS Capital Benchmark Index / Gartner Peer Insights",
        nullable=False,
    )

    source_type: Mapped[str] = mapped_column(
        String(50),
        default="INDUSTRY",
        nullable=False,  # INTERNAL, INDUSTRY, THIRD_PARTY
    )

    published_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    freshness_score: Mapped[float] = mapped_column(
        Float,
        default=98.0,
        nullable=False,
    )

    confidence_score: Mapped[float] = mapped_column(
        Float,
        default=96.0,
        nullable=False,
    )


class CompetitiveBenchmark(TimestampMixin, Base):
    """Competitive metric benchmark against Industry Median, Top Quartile, and Best-In-Class."""

    __tablename__ = "competitive_benchmarks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    source_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("benchmark_sources.id", ondelete="CASCADE"),
        nullable=False,
    )

    metric_name: Mapped[str] = mapped_column(
        String(100),
        default="Customer Retention Rate",
        nullable=False,
    )

    our_value: Mapped[float] = mapped_column(
        Float,
        default=84.2,
        nullable=False,
    )

    industry_median: Mapped[float] = mapped_column(
        Float,
        default=91.0,
        nullable=False,
    )

    top_quartile: Mapped[float] = mapped_column(
        Float,
        default=94.5,
        nullable=False,
    )

    best_in_class: Mapped[float] = mapped_column(
        Float,
        default=97.0,
        nullable=False,
    )

    gap_to_median: Mapped[float] = mapped_column(
        Float,
        default=-6.8,
        nullable=False,
    )

    gap_to_top_quartile: Mapped[float] = mapped_column(
        Float,
        default=-10.3,
        nullable=False,
    )

    performance_tier: Mapped[str] = mapped_column(
        String(50),
        default="MEDIAN_LAGGING",
        nullable=False,  # TOP_QUARTILE, MEDIAN_LEADER, MEDIAN_LAGGING
    )


class BenchmarkOpportunity(TimestampMixin, Base):
    """High-leverage revenue opportunity discovered from competitive gaps, feeding Digital Twin."""

    __tablename__ = "benchmark_opportunities"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    benchmark_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("competitive_benchmarks.id", ondelete="CASCADE"),
        nullable=False,
    )

    opportunity_title: Mapped[str] = mapped_column(
        String(255),
        default="Close Retention Gap to Industry Median",
        nullable=False,
    )

    target_metric: Mapped[str] = mapped_column(
        String(100),
        default="Customer Retention Rate: 84% -> 91%",
        nullable=False,
    )

    potential_arr_gain: Mapped[float] = mapped_column(
        Float,
        default=340000.0,
        nullable=False,
    )

    difficulty_tier: Mapped[str] = mapped_column(
        String(50),
        default="MODERATE",
        nullable=False,  # LOW, MODERATE, HIGH
    )

    auto_scenario_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="SCENARIO_GENERATED",
        nullable=False,  # DISCOVERED, SCENARIO_GENERATED, INITIATIVE_CREATED
    )


class CompetitiveSnapshot(TimestampMixin, Base):
    """Autonomous competitive positioning snapshot with SWOT intelligence."""

    __tablename__ = "competitive_snapshots"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    portfolio_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )

    market_rank: Mapped[int] = mapped_column(
        Integer,
        default=4,
        nullable=False,
    )

    total_tracked_competitors: Mapped[int] = mapped_column(
        Integer,
        default=28,
        nullable=False,
    )

    percentile: Mapped[float] = mapped_column(
        Float,
        default=85.7,
        nullable=False,
    )

    swot_strengths: Mapped[List[str]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=list,
        nullable=False,
    )

    swot_weaknesses: Mapped[List[str]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=list,
        nullable=False,
    )

    swot_opportunities: Mapped[List[str]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=list,
        nullable=False,
    )

    swot_threats: Mapped[List[str]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=list,
        nullable=False,
    )

    snapshot_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )


# ==============================================================================
# PHASE 6.9: ENTERPRISE OS ORCHESTRATION & INSTITUTIONAL MEMORY
# ==============================================================================

class EnterpriseMemoryRecord(TimestampMixin, Base):
    """Permanent corporate knowledge memory indexing decisions, postmortems, overrides, and outcomes."""

    __tablename__ = "enterprise_memory_records"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    portfolio_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )

    record_type: Mapped[str] = mapped_column(
        String(50),
        default="DECISION",
        nullable=False,  # DECISION, POSTMORTEM, OVERRIDE, LESSON_LEARNED, INITIATIVE_OUTCOME
    )

    source_entity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    summary: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    causal_context: Mapped[Dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=dict,
        nullable=False,
    )

    outcome_rating: Mapped[str] = mapped_column(
        String(50),
        default="HIGHLY_SUCCESSFUL",
        nullable=False,  # HIGHLY_SUCCESSFUL, PARTIAL, FAILED
    )

    tags: Mapped[List[str]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=list,
        nullable=False,
    )


class PlaybookTemplate(TimestampMixin, Base):
    """Reusable enterprise autonomous playbook template definition."""

    __tablename__ = "playbook_templates"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    template_code: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    template_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    trigger_source: Mapped[str] = mapped_column(
        String(50),
        default="MONITORING_ALERT",
        nullable=False,  # MONITORING_ALERT, FORECAST_DRIFT, BENCHMARK_GAP
    )

    trigger_condition: Mapped[Dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=dict,
        nullable=False,
    )

    is_autonomous: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )


class PlaybookStep(TimestampMixin, Base):
    """Declarative execution step in a playbook template graph."""

    __tablename__ = "playbook_steps"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    template_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("playbook_templates.id", ondelete="CASCADE"),
        nullable=False,
    )

    step_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    step_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    action_type: Mapped[str] = mapped_column(
        String(50),
        default="DIAGNOSE",
        nullable=False,  # DIAGNOSE, SIMULATE, CREATE_INITIATIVE, GOVERNANCE_REVIEW, NOTIFY
    )

    approval_required: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    approval_tier: Mapped[str] = mapped_column(
        String(50),
        default="AUTO",
        nullable=False,  # AUTO, MANAGER, EXECUTIVE, BOARD
    )


class PlaybookExecution(TimestampMixin, Base):
    """Quarterly or event-triggered execution run of a PlaybookTemplate."""

    __tablename__ = "playbook_executions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    template_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("playbook_templates.id", ondelete="CASCADE"),
        nullable=False,
    )

    execution_code: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    trigger_event_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )

    execution_status: Mapped[str] = mapped_column(
        String(50),
        default="SUCCESS",
        nullable=False,  # SUCCESS, RUNNING, RETRYING, PARTIAL_SUCCESS, ROLLED_BACK, FAILED
    )

    executed_steps: Mapped[List[Dict[str, Any]]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=list,
        nullable=False,
    )

    execution_cost: Mapped[float] = mapped_column(
        Float,
        default=0.14,
        nullable=False,
    )

    duration_ms: Mapped[int] = mapped_column(
        Integer,
        default=240,
        nullable=False,
    )

    failure_reason: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    executed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )


class AutonomousActionRecord(TimestampMixin, Base):
    """Audit record for individual autonomous actions with compensation rollback state."""

    __tablename__ = "autonomous_action_records"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    execution_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("playbook_executions.id", ondelete="CASCADE"),
        nullable=False,
    )

    action_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    approval_tier: Mapped[str] = mapped_column(
        String(50),
        default="AUTO",
        nullable=False,  # AUTO, MANAGER, EXECUTIVE, BOARD
    )

    execution_status: Mapped[str] = mapped_column(
        String(50),
        default="SUCCESS",
        nullable=False,  # SUCCESS, COMPENSATED, ROLLED_BACK
    )

    rollback_available: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
