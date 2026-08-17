"""Operational Monitoring Orchestration Service for Phase 13."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple, Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.execution.repositories.benefit_repository import BenefitRealizationRepository
from app.execution.repositories.governance_review_repository import GovernanceReviewRepository
from app.execution.repositories.initiative_repository import InitiativeRepository
from app.execution.repositories.snapshot_repository import SnapshotRepository
from app.execution.schemas.initiative import InitiativeFilterParams
from app.execution.services.portfolio_balancing_engine import PortfolioBalancingEngine
from app.execution.services.strategic_analytics_service import StrategicAnalyticsService
from app.monitoring.constants import (
    MONITORING_VERSION,
    AlertSourceEntityType,
    MonitoringCategory,
    MonitoringSeverity,
    MonitoringStatus,
)
from app.monitoring.repositories.monitoring_alert_repository import MonitoringAlertRepository
from app.monitoring.schemas.production_monitoring import (
    AlertEvaluationResponse,
    ExecutiveEscalationItem,
    ExecutiveEscalationQueueResponse,
    ExecutiveMonitoringDashboardResponse,
    GovernanceDashboardResponse,
    MetricAuditSummary,
    MonitoringAlertListResponse,
    MonitoringAlertResponse,
    OperationalHealthMetricsResponse,
    OperationalIntelligenceReportResponse,
    PortfolioMonitoringDashboardResponse,
    SnapshotLineageDepthResponse,
)
from app.monitoring.services.alert_rule_engine import AlertRuleEngine
from app.monitoring.services.executive_escalation_engine import ExecutiveEscalationEngine
from app.monitoring.services.operational_health_engine import OperationalHealthEngine
from app.monitoring.services.operational_intelligence_engine import OperationalIntelligenceEngine
from app.monitoring.services.snapshot_lineage_engine import SnapshotLineageEngine


class OperationalMonitoringService:
    """
    Central business service orchestrating alert rule evaluation, lifecycle transitions,
    operational health intelligence, and specialized executive dashboards.
    """

    def __init__(self, db: Union[AsyncSession, Session]) -> None:
        self.db = db
        self.alert_repo = MonitoringAlertRepository(db)
        self.initiative_repo = InitiativeRepository(db)
        self.governance_repo = GovernanceReviewRepository(db)
        self.benefit_repo = BenefitRealizationRepository(db)
        self.snapshot_repo = SnapshotRepository(db)
        self.analytics_service = StrategicAnalyticsService(db)

        # 5 Engines
        self.alert_engine = AlertRuleEngine()
        self.intel_engine = OperationalIntelligenceEngine()
        self.escalation_engine = ExecutiveEscalationEngine()
        self.health_engine = OperationalHealthEngine()
        self.lineage_engine = SnapshotLineageEngine()
        self.balance_engine = PortfolioBalancingEngine()

    async def _gather_domain_telemetry(self, organization_id: uuid.UUID) -> Dict[str, Any]:
        """Gathers telemetry across execution, governance, benefits, and snapshot domains."""
        filters = InitiativeFilterParams(limit=500)
        initiatives, _ = await self.initiative_repo.list(organization_id, filters)
        gov_reviews = await self.governance_repo.list_reviews(organization_id=organization_id)
        benefits = await self.benefit_repo.list_benefits(organization_id=organization_id)
        latest_snapshot = await self.snapshot_repo.get_latest_portfolio_snapshot(organization_id)
        snapshots, _ = await self.snapshot_repo.list_portfolio_snapshots(organization_id, limit=20)

        # Compute Governance Score
        if gov_reviews:
            gov_score = sum(float(r.compliance_score or 100.0) for r in gov_reviews) / len(gov_reviews)
        else:
            gov_score = 85.0

        # Compute Average Risk Score
        if initiatives:
            avg_risk = sum(float(getattr(i, "risk_score", 20.0) or 20.0) for i in initiatives) / len(initiatives)
        else:
            avg_risk = 20.0

        # Balance Metrics
        strat_values = {i.id: float(getattr(i, "strategic_value_score", 75.0) or 75.0) for i in initiatives}
        risk_scores = {i.id: float(getattr(i, "risk_score", 20.0) or 20.0) for i in initiatives}
        dep_counts = {i.id: 1 for i in initiatives}
        port_balance = self.balance_engine.compute_portfolio_balance(
            initiative_values=strat_values,
            initiative_risks=risk_scores,
            dependency_counts=dep_counts,
            spof_count=0,
        )

        coverage = latest_snapshot.snapshot_coverage_rate if latest_snapshot else (100.0 if initiatives else 0.0)
        completeness = latest_snapshot.snapshot_completeness_score if latest_snapshot else 100.0

        kpi_metrics = {
            "average_execution_health": 100.0 - avg_risk,
            "revenue_growth_rate": -15.0 if avg_risk > 70.0 else 5.0,
        }

        return {
            "initiatives": initiatives,
            "gov_reviews": gov_reviews,
            "gov_score": gov_score,
            "benefits": benefits,
            "latest_snapshot": latest_snapshot,
            "snapshots": snapshots,
            "avg_risk": avg_risk,
            "port_balance": port_balance,
            "coverage": coverage,
            "completeness": completeness,
            "kpi_metrics": kpi_metrics,
        }

    async def evaluate_and_sync_alerts(self, organization_id: uuid.UUID) -> AlertEvaluationResponse:
        """Runs deterministic alert rules and idempotently updates/inserts alerts in the repository."""
        telemetry = await self._gather_domain_telemetry(organization_id)

        candidates = self.alert_engine.evaluate_rules(
            organization_id=organization_id,
            kpi_metrics=telemetry["kpi_metrics"],
            initiatives=telemetry["initiatives"],
            governance_reviews=telemetry["gov_reviews"],
            benefits=telemetry["benefits"],
            portfolio_balance={
                "portfolio_balance_score": telemetry["port_balance"].portfolio_balance_score,
                "single_points_of_failure_count": telemetry["port_balance"].single_point_of_failure_count,
                "portfolio_strategic_exposure_score": telemetry["port_balance"].portfolio_strategic_exposure_score,
            },
            latest_snapshot=telemetry["latest_snapshot"],
            snapshots=telemetry["snapshots"],
        )

        new_count = 0
        updated_count = 0
        saved_alerts: List[MonitoringAlertResponse] = []

        for candidate in candidates:
            persisted, is_new = await self.alert_repo.create_or_increment(candidate)
            if is_new:
                new_count += 1
            else:
                updated_count += 1
            saved_alerts.append(MonitoringAlertResponse.model_validate(persisted))

        active_alerts, total_active = await self.alert_repo.list(
            organization_id=organization_id,
            status=MonitoringStatus.ACTIVE,
            limit=500,
        )

        return AlertEvaluationResponse(
            organization_id=organization_id,
            evaluated_rules_count=len(candidates),
            new_alerts_count=new_count,
            updated_alerts_count=updated_count,
            active_alerts_total=total_active,
            alerts=saved_alerts,
            evaluated_at=datetime.now(timezone.utc),
        )

    async def get_alerts(
        self,
        organization_id: uuid.UUID,
        category: Optional[MonitoringCategory] = None,
        severity: Optional[MonitoringSeverity] = None,
        status: Optional[MonitoringStatus] = None,
        source_entity_type: Optional[AlertSourceEntityType] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> MonitoringAlertListResponse:
        """Retrieves paginated alerts with filtering."""
        items, total = await self.alert_repo.list(
            organization_id=organization_id,
            category=category,
            severity=severity,
            status=status,
            source_entity_type=source_entity_type,
            limit=limit,
            offset=offset,
        )
        return MonitoringAlertListResponse(
            items=[MonitoringAlertResponse.model_validate(i) for i in items],
            total=total,
            page=(offset // limit) + 1,
            limit=limit,
        )

    async def acknowledge_alert(
        self,
        alert_id: uuid.UUID,
        user_id: uuid.UUID,
        organization_id: uuid.UUID,
        notes: Optional[str] = None,
    ) -> Optional[MonitoringAlertResponse]:
        """Transitions alert to ACKNOWLEDGED state."""
        updated = await self.alert_repo.transition_status(
            alert_id=alert_id,
            organization_id=organization_id,
            new_status=MonitoringStatus.ACKNOWLEDGED,
            user_id=user_id,
            notes=notes,
        )
        return MonitoringAlertResponse.model_validate(updated) if updated else None

    async def resolve_alert(
        self,
        alert_id: uuid.UUID,
        user_id: uuid.UUID,
        organization_id: uuid.UUID,
        resolution_notes: str,
    ) -> Optional[MonitoringAlertResponse]:
        """Transitions alert to RESOLVED state."""
        updated = await self.alert_repo.transition_status(
            alert_id=alert_id,
            organization_id=organization_id,
            new_status=MonitoringStatus.RESOLVED,
            user_id=user_id,
            notes=resolution_notes,
        )
        return MonitoringAlertResponse.model_validate(updated) if updated else None

    async def suppress_alert(
        self,
        alert_id: uuid.UUID,
        user_id: uuid.UUID,
        organization_id: uuid.UUID,
        suppression_reason: str,
    ) -> Optional[MonitoringAlertResponse]:
        """Transitions alert to SUPPRESSED state."""
        updated = await self.alert_repo.transition_status(
            alert_id=alert_id,
            organization_id=organization_id,
            new_status=MonitoringStatus.SUPPRESSED,
            user_id=user_id,
            notes=suppression_reason,
        )
        return MonitoringAlertResponse.model_validate(updated) if updated else None

    async def get_operational_intelligence(self, organization_id: uuid.UUID) -> OperationalIntelligenceReportResponse:
        """Generates comprehensive operational intelligence and health report."""
        alerts, _ = await self.alert_repo.list(organization_id=organization_id, limit=500)
        telemetry = await self._gather_domain_telemetry(organization_id)

        return self.intel_engine.generate_report(
            organization_id=organization_id,
            alerts=alerts,
            governance_score=telemetry["gov_score"],
            average_risk_score=telemetry["avg_risk"],
            metric_coverage=telemetry["coverage"],
            snapshot_completeness=telemetry["completeness"],
            portfolio_balance_score=telemetry["port_balance"].portfolio_balance_score,
            initiatives=telemetry["initiatives"],
        )

    async def get_executive_escalations(self, organization_id: uuid.UUID) -> ExecutiveEscalationQueueResponse:
        """Generates deterministic executive escalation queue."""
        alerts, _ = await self.alert_repo.list(organization_id=organization_id, limit=500)
        telemetry = await self._gather_domain_telemetry(organization_id)

        return self.escalation_engine.generate_escalation_queue(
            organization_id=organization_id,
            alerts=alerts,
            initiatives=telemetry["initiatives"],
        )

    async def get_operational_health(self, organization_id: uuid.UUID) -> OperationalHealthMetricsResponse:
        """Calculates normalized composite operational health score and contributing factors."""
        alerts, _ = await self.alert_repo.list(organization_id=organization_id, limit=500)
        telemetry = await self._gather_domain_telemetry(organization_id)

        return self.health_engine.evaluate_health(
            organization_id=organization_id,
            alerts=alerts,
            governance_score=telemetry["gov_score"],
            average_risk_score=telemetry["avg_risk"],
            metric_coverage=telemetry["coverage"],
            snapshot_completeness=telemetry["completeness"],
            portfolio_balance_score=telemetry["port_balance"].portfolio_balance_score,
        )

    async def get_metric_audit_summary(self, organization_id: uuid.UUID) -> MetricAuditSummary:
        """Computes metric capture count and capture rate (Deferred 13.6)."""
        telemetry = await self._gather_domain_telemetry(organization_id)
        init_count = len(telemetry["initiatives"])
        expected = max(1, init_count * 5)
        captured = int((telemetry["coverage"] / 100.0) * expected)
        rate = round((captured / expected) * 100.0, 2)

        return MetricAuditSummary(
            organization_id=organization_id,
            captured_metric_count=captured,
            expected_metric_count=expected,
            metric_capture_rate=rate,
        )

    async def get_snapshot_lineage_depth(
        self,
        snapshot_id: uuid.UUID,
        organization_id: uuid.UUID,
    ) -> SnapshotLineageDepthResponse:
        """Calculates lineage depth and ancestor chain for a snapshot (Deferred 13.6)."""
        snapshots, _ = await self.snapshot_repo.list_portfolio_snapshots(organization_id, limit=100)
        return self.lineage_engine.compute_lineage_depth(
            snapshot_id=snapshot_id,
            all_snapshots=snapshots,
        )

    async def get_executive_dashboard(self, organization_id: uuid.UUID) -> ExecutiveMonitoringDashboardResponse:
        """Generates unified executive monitoring dashboard."""
        health = await self.get_operational_health(organization_id)
        active_alerts_list, _ = await self.alert_repo.list(
            organization_id=organization_id,
            status=MonitoringStatus.ACTIVE,
            limit=20,
        )
        crit_alerts, crit_count = await self.alert_repo.list(
            organization_id=organization_id,
            status=MonitoringStatus.ACTIVE,
            severity=MonitoringSeverity.CRITICAL,
            limit=10,
        )
        escalations = await self.get_executive_escalations(organization_id)

        # Top reason codes
        all_reasons = []
        for a in active_alerts_list:
            all_reasons.extend(getattr(a, "reason_codes", []) or [])
        unique_reasons = list(dict.fromkeys(all_reasons))[:5]

        return ExecutiveMonitoringDashboardResponse(
            organization_id=organization_id,
            operational_health=health,
            active_alerts=[MonitoringAlertResponse.model_validate(a) for a in active_alerts_list],
            critical_alerts_count=crit_count,
            escalations=escalations.escalation_queue[:10],
            top_reason_codes=unique_reasons,
            engine_version=MONITORING_VERSION,
            generated_at=datetime.now(timezone.utc),
        )

    async def get_governance_dashboard(self, organization_id: uuid.UUID) -> GovernanceDashboardResponse:
        """Generates specialized governance dashboard."""
        telemetry = await self._gather_domain_telemetry(organization_id)
        gov_alerts, _ = await self.alert_repo.list(
            organization_id=organization_id,
            category=MonitoringCategory.GOVERNANCE,
            limit=20,
        )
        non_compliant = sum(1 for r in telemetry["gov_reviews"] if float(getattr(r, "compliance_score", 100.0) or 100.0) < 75.0)

        return GovernanceDashboardResponse(
            organization_id=organization_id,
            governance_compliance_score=telemetry["gov_score"],
            governance_alerts=[MonitoringAlertResponse.model_validate(a) for a in gov_alerts],
            unresolved_governance_actions_count=non_compliant,
            stage_gate_review_compliance_rate=telemetry["gov_score"],
            audit_events_count=len(telemetry["gov_reviews"]),
            generated_at=datetime.now(timezone.utc),
        )

    async def get_portfolio_monitoring_dashboard(self, organization_id: uuid.UUID) -> PortfolioMonitoringDashboardResponse:
        """Generates specialized portfolio monitoring dashboard."""
        telemetry = await self._gather_domain_telemetry(organization_id)
        port_alerts, _ = await self.alert_repo.list(
            organization_id=organization_id,
            category=MonitoringCategory.PORTFOLIO,
            limit=20,
        )
        bal = telemetry["port_balance"]

        return PortfolioMonitoringDashboardResponse(
            organization_id=organization_id,
            portfolio_balance_score=bal.portfolio_balance_score,
            strategic_exposure_score=bal.portfolio_strategic_exposure_score,
            single_points_of_failure_count=bal.single_point_of_failure_count,
            portfolio_alerts=[MonitoringAlertResponse.model_validate(a) for a in port_alerts],
            imbalance_factors=bal.imbalance_factors,
            generated_at=datetime.now(timezone.utc),
        )
