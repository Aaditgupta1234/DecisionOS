"""Governance Intelligence Engine for Phase 12.5.

Computes deterministic review readiness scoring, multi-tier escalation recommendations,
escalation aging tracking, and executive governance operational postures.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Sequence

from app.execution.constants import (
    GOVERNANCE_ENGINE_VERSION,
    EscalationLevel,
    GovernanceActionStatus,
    GovernanceReviewStatus,
    GovernanceStatus,
    GovernanceTrend,
    ReviewReadinessLevel,
    calculate_review_readiness_level,
)


class GovernanceIntelligenceEngine:
    """
    Deterministic governance intelligence calculation engine.
    Auditable, pure mathematical evaluation for enterprise PMO stage-gate decisioning.
    """

    ENGINE_VERSION = GOVERNANCE_ENGINE_VERSION

    @classmethod
    def calculate_review_readiness(
        cls,
        health_score: float,
        risk_score: float,
        milestones: Optional[Sequence[Any]] = None,
        actions: Optional[Sequence[Any]] = None,
    ) -> Dict[str, Any]:
        """
        Calculates review readiness score (0-100) and maps to a ReviewReadinessLevel.
        Formula: 35% Health + 35% (100 - Risk) + 15% Milestone Quality + 15% Action Compliance.
        """
        # Clamp inputs
        h_score = max(0.0, min(100.0, float(health_score)))
        r_score = max(0.0, min(100.0, float(risk_score)))
        inv_risk = max(0.0, 100.0 - r_score)

        # Milestone Quality factor
        milestone_quality = 100.0
        if milestones:
            total_m = len(milestones)
            blocked_or_delayed = 0
            for m in milestones:
                m_status = getattr(m, "status", None)
                status_str = getattr(m_status, "value", str(m_status)) if m_status else ""
                if status_str in ("BLOCKED", "DELAYED", "CRITICAL_DELAY"):
                    blocked_or_delayed += 1
            milestone_quality = max(0.0, 100.0 - ((blocked_or_delayed / max(1, total_m)) * 100.0))

        # Action Compliance factor
        action_compliance = 100.0
        if actions:
            total_act = len(actions)
            overdue_act = 0
            for a in actions:
                a_status = getattr(a, "status", None)
                status_str = getattr(a_status, "value", str(a_status)) if a_status else ""
                if status_str == "OVERDUE":
                    overdue_act += 1
            action_compliance = max(0.0, 100.0 - ((overdue_act / max(1, total_act)) * 100.0))

        readiness_score = round(
            (0.35 * h_score)
            + (0.35 * inv_risk)
            + (0.15 * milestone_quality)
            + (0.15 * action_compliance),
            2,
        )
        readiness_score = max(0.0, min(100.0, readiness_score))
        readiness_level = calculate_review_readiness_level(readiness_score)

        return {
            "review_readiness_score": readiness_score,
            "review_readiness_level": readiness_level,
            "health_component": round(0.35 * h_score, 2),
            "risk_mitigation_component": round(0.35 * inv_risk, 2),
            "milestone_quality_component": round(0.15 * milestone_quality, 2),
            "action_compliance_component": round(0.15 * action_compliance, 2),
        }

    @classmethod
    def recommend_escalation_level(
        cls,
        risk_score: float,
        health_score: float,
        critical_blockers_count: int = 0,
        critical_path_delay_days: int = 0,
        schedule_variance_pct: float = 0.0,
    ) -> EscalationLevel:
        """
        Deterministically evaluates multi-tier escalation thresholds.
        """
        r_score = float(risk_score)
        h_score = float(health_score)

        # EXECUTIVE Tier: Extreme risk, critical blocker with health collapse, or severe CP delay
        if (
            r_score >= 80.0
            or (h_score < 30.0 and critical_blockers_count > 0)
            or critical_path_delay_days >= 21
        ):
            return EscalationLevel.EXECUTIVE

        # LEVEL_2 Tier: High risk, low health, active critical blocker, or 2+ week CP delay
        if (
            r_score >= 60.0
            or h_score < 50.0
            or critical_blockers_count > 0
            or critical_path_delay_days >= 14
        ):
            return EscalationLevel.LEVEL_2

        # LEVEL_1 Tier: Moderate risk or schedule variance > 10% behind
        if r_score >= 30.0 or schedule_variance_pct <= -10.0:
            return EscalationLevel.LEVEL_1

        return EscalationLevel.NONE

    @classmethod
    def calculate_escalation_aging(
        cls,
        reviews: Optional[Sequence[Any]] = None,
        current_time: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Calculates average and oldest open escalation age in elapsed days.
        """
        now = current_time or datetime.now(timezone.utc)
        if not reviews:
            return {
                "average_escalation_age_days": 0.0,
                "oldest_open_escalation_days": 0,
                "active_escalations_count": 0,
            }

        open_ages: List[float] = []
        for r in reviews:
            esc_level = getattr(r, "escalation_level", None)
            level_str = getattr(esc_level, "value", str(esc_level)) if esc_level else "NONE"
            r_status = getattr(r, "review_status", None)
            status_str = getattr(r_status, "value", str(r_status)) if r_status else ""

            # Check if review has an active escalation and is not completed/cancelled
            if level_str in ("LEVEL_1", "LEVEL_2", "EXECUTIVE") and status_str not in ("COMPLETED", "CANCELLED"):
                created_at = getattr(r, "created_at", None) or getattr(r, "scheduled_at", None)
                if created_at:
                    if created_at.tzinfo is None:
                        created_at = created_at.replace(tzinfo=timezone.utc)
                    age_days = max(0.0, (now - created_at).total_seconds() / 86400.0)
                    open_ages.append(age_days)

        if not open_ages:
            return {
                "average_escalation_age_days": 0.0,
                "oldest_open_escalation_days": 0,
                "active_escalations_count": 0,
            }

        avg_age = round(sum(open_ages) / len(open_ages), 1)
        oldest_age = int(max(open_ages))

        return {
            "average_escalation_age_days": avg_age,
            "oldest_open_escalation_days": oldest_age,
            "active_escalations_count": len(open_ages),
        }

    @classmethod
    def evaluate_governance_status(
        cls,
        recommended_escalation: EscalationLevel,
        readiness_level: ReviewReadinessLevel,
        overdue_reviews_count: int = 0,
        health_grade: str = "EXCELLENT",
        risk_severity: str = "LOW",
    ) -> GovernanceStatus:
        """
        Deterministically assigns enterprise governance status.
        """
        if recommended_escalation == EscalationLevel.EXECUTIVE or readiness_level == ReviewReadinessLevel.EXECUTIVE_ATTENTION:
            return GovernanceStatus.EXECUTIVE_ATTENTION

        if (
            recommended_escalation == EscalationLevel.LEVEL_2
            or overdue_reviews_count > 0
            or readiness_level == ReviewReadinessLevel.ESCALATION_REQUIRED
        ):
            return GovernanceStatus.ESCALATION_REQUIRED

        if (
            readiness_level == ReviewReadinessLevel.REVIEW_REQUIRED
            or health_grade in ("AT_RISK", "CRITICAL")
            or risk_severity in ("HIGH", "CRITICAL")
        ):
            return GovernanceStatus.REVIEW_REQUIRED

        return GovernanceStatus.HEALTHY
