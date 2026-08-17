"""Deterministic Alert Rule Engine for Phase 13: Production Governance & Alert Monitoring."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.monitoring.constants import (
    ALERT_RULE_ENGINE_VERSION,
    AlertConfidenceLevel,
    AlertSourceEntityType,
    MonitoringCategory,
    MonitoringSeverity,
    REASON_BENEFIT_REALIZATION_LAG,
    REASON_COMPLIANCE_FAILURE_DETECTED,
    REASON_CRITICAL_BLOCKER_PRESENT,
    REASON_HEALTH_SCORE_DEGRADATION,
    REASON_METRIC_COVERAGE_DEFICIT,
    REASON_PORTFOLIO_IMBALANCE_DETECTED,
    REASON_REVENUE_DROP_THRESHOLD_EXCEEDED,
    REASON_RISK_POSTURE_ESCALATION,
    REASON_SNAPSHOT_RECENCY_BREACH,
    REASON_SPOF_CLUSTER_DETECTED,
    REASON_TIMELINE_SLIPPAGE_DETECTED,
    calculate_alert_confidence,
    generate_alert_fingerprint,
)
from app.models.monitoring_alert import MonitoringAlert


class AlertRuleEngine:
    """
    Evaluates multi-domain deterministic alert rules across KPI thresholds,
    governance compliance, risk escalation, benefits realization, and portfolio structural exposure.
    """

    @classmethod
    def evaluate_rules(
        cls,
        organization_id: uuid.UUID,
        kpi_metrics: Optional[Dict[str, Any]] = None,
        initiatives: Optional[List[Any]] = None,
        governance_reviews: Optional[List[Any]] = None,
        benefits: Optional[List[Any]] = None,
        portfolio_balance: Optional[Dict[str, Any]] = None,
        latest_snapshot: Optional[Any] = None,
        snapshots: Optional[List[Any]] = None,
    ) -> List[MonitoringAlert]:
        """Runs all deterministic alert rule checks and returns candidate MonitoringAlert instances."""
        candidate_alerts: List[MonitoringAlert] = []
        now = datetime.now(timezone.utc)

        # Baseline Data Quality for Confidence Scoring
        coverage_rate = 100.0
        snapshot_comp = 100.0
        data_quality = 90.0

        if latest_snapshot:
            coverage_rate = float(getattr(latest_snapshot, "snapshot_coverage_rate", 100.0) or 100.0)
            snapshot_comp = float(getattr(latest_snapshot, "snapshot_completeness_score", 100.0) or 100.0)
        elif initiatives and len(initiatives) > 0:
            coverage_rate = 85.0

        conf_score, conf_level = calculate_alert_confidence(
            metric_coverage=coverage_rate,
            snapshot_completeness=snapshot_comp,
            data_quality_score=data_quality,
        )

        # ----------------------------------------------------------------------
        # 1. KPI THRESHOLD RULES
        # ----------------------------------------------------------------------
        if kpi_metrics:
            # Revenue Drop Rule (> 10% decline)
            rev_growth = float(kpi_metrics.get("revenue_growth_rate", 0.0) or 0.0)
            if rev_growth <= -10.0:
                sev = MonitoringSeverity.CRITICAL if rev_growth <= -20.0 else MonitoringSeverity.HIGH
                fp = generate_alert_fingerprint(organization_id, "RULE_KPI_REVENUE_DROP", "SYSTEM", None)
                candidate_alerts.append(
                    MonitoringAlert(
                        organization_id=str(organization_id),
                        alert_fingerprint=fp,
                        category=MonitoringCategory.KPI,
                        severity=sev,
                        title=f"Severe Revenue Contraction Detected ({rev_growth:.1f}%)",
                        description=f"Revenue trajectory declined by {abs(rev_growth):.1f}%, exceeding the deterministic threshold of -10.0%.",
                        rule_name="RULE_KPI_REVENUE_DROP",
                        rule_version=ALERT_RULE_ENGINE_VERSION,
                        alert_confidence_score=conf_score,
                        alert_confidence_level=conf_level,
                        reason_codes=[REASON_REVENUE_DROP_THRESHOLD_EXCEEDED],
                        source_entity_type=AlertSourceEntityType.SYSTEM,
                        source_entity_id=None,
                        occurrence_count=1,
                        first_triggered_at=now,
                        last_triggered_at=now,
                        alert_payload={"revenue_growth_rate": rev_growth, "threshold": -10.0},
                    )
                )

            # Execution Health Degradation Rule (< 60.0)
            avg_health = float(kpi_metrics.get("average_execution_health", 80.0) or 80.0)
            if avg_health < 60.0:
                sev = MonitoringSeverity.CRITICAL if avg_health < 45.0 else MonitoringSeverity.HIGH
                fp = generate_alert_fingerprint(organization_id, "RULE_KPI_HEALTH_DEGRADATION", "SYSTEM", None)
                candidate_alerts.append(
                    MonitoringAlert(
                        organization_id=str(organization_id),
                        alert_fingerprint=fp,
                        category=MonitoringCategory.KPI,
                        severity=sev,
                        title=f"Portfolio Execution Health Degradation ({avg_health:.1f})",
                        description=f"Average execution health dropped to {avg_health:.1f}, below the deterministic stability threshold of 60.0.",
                        rule_name="RULE_KPI_HEALTH_DEGRADATION",
                        rule_version=ALERT_RULE_ENGINE_VERSION,
                        alert_confidence_score=conf_score,
                        alert_confidence_level=conf_level,
                        reason_codes=[REASON_HEALTH_SCORE_DEGRADATION],
                        source_entity_type=AlertSourceEntityType.SYSTEM,
                        source_entity_id=None,
                        occurrence_count=1,
                        first_triggered_at=now,
                        last_triggered_at=now,
                        alert_payload={"average_execution_health": avg_health, "threshold": 60.0},
                    )
                )

        # ----------------------------------------------------------------------
        # 2. INITIATIVE & RISK RULES
        # ----------------------------------------------------------------------
        if initiatives:
            for init in initiatives:
                init_id = getattr(init, "id", None)
                init_title = getattr(init, "title", "Strategic Initiative")
                health_val = float(getattr(init, "execution_health_score", getattr(init, "health_score", 80.0)) or 80.0)
                risk_val = float(getattr(init, "risk_score", max(0.0, 100.0 - health_val)) or (100.0 - health_val))
                has_crit_blockers = getattr(init, "has_critical_blockers", False)

                # Critical Blocker Alert
                if has_crit_blockers:
                    fp = generate_alert_fingerprint(organization_id, "RULE_RISK_CRITICAL_BLOCKER", "INITIATIVE", init_id)
                    candidate_alerts.append(
                        MonitoringAlert(
                            organization_id=str(organization_id),
                            alert_fingerprint=fp,
                            category=MonitoringCategory.RISK,
                            severity=MonitoringSeverity.CRITICAL,
                            title=f"Critical Blocker Detected: {init_title}",
                            description=f"Initiative '{init_title}' has one or more unresolved critical path blockers.",
                            rule_name="RULE_RISK_CRITICAL_BLOCKER",
                            rule_version=ALERT_RULE_ENGINE_VERSION,
                            alert_confidence_score=conf_score,
                            alert_confidence_level=conf_level,
                            reason_codes=[REASON_CRITICAL_BLOCKER_PRESENT],
                            source_entity_type=AlertSourceEntityType.INITIATIVE,
                            source_entity_id=str(init_id) if init_id else None,
                            occurrence_count=1,
                            first_triggered_at=now,
                            last_triggered_at=now,
                            alert_payload={"initiative_id": str(init_id), "risk_score": risk_val, "health_score": health_val},
                        )
                    )

                # High Risk Posture Alert
                if risk_val >= 75.0 and not has_crit_blockers:
                    fp = generate_alert_fingerprint(organization_id, "RULE_RISK_HIGH_EXPOSURE", "INITIATIVE", init_id)
                    candidate_alerts.append(
                        MonitoringAlert(
                            organization_id=str(organization_id),
                            alert_fingerprint=fp,
                            category=MonitoringCategory.RISK,
                            severity=MonitoringSeverity.HIGH,
                            title=f"Elevated Risk Posture: {init_title} ({risk_val:.1f})",
                            description=f"Initiative '{init_title}' risk score elevated to {risk_val:.1f}, exceeding the 75.0 threshold.",
                            rule_name="RULE_RISK_HIGH_EXPOSURE",
                            rule_version=ALERT_RULE_ENGINE_VERSION,
                            alert_confidence_score=conf_score,
                            alert_confidence_level=conf_level,
                            reason_codes=[REASON_RISK_POSTURE_ESCALATION],
                            source_entity_type=AlertSourceEntityType.INITIATIVE,
                            source_entity_id=str(init_id) if init_id else None,
                            occurrence_count=1,
                            first_triggered_at=now,
                            last_triggered_at=now,
                            alert_payload={"initiative_id": str(init_id), "risk_score": risk_val},
                        )
                    )

        # ----------------------------------------------------------------------
        # 3. GOVERNANCE RULES
        # ----------------------------------------------------------------------
        if governance_reviews:
            non_compliant_count = sum(
                1 for r in governance_reviews if float(getattr(r, "compliance_score", 100.0) or 100.0) < 75.0
            )
            if non_compliant_count > 0:
                sev = MonitoringSeverity.CRITICAL if non_compliant_count >= 3 else MonitoringSeverity.HIGH
                fp = generate_alert_fingerprint(organization_id, "RULE_GOV_NON_COMPLIANCE", "SYSTEM", None)
                candidate_alerts.append(
                    MonitoringAlert(
                        organization_id=str(organization_id),
                        alert_fingerprint=fp,
                        category=MonitoringCategory.GOVERNANCE,
                        severity=sev,
                        title=f"Governance Compliance Failures Detected ({non_compliant_count} Reviews)",
                        description=f"{non_compliant_count} stage-gate governance review(s) scored below the required 75.0% compliance threshold.",
                        rule_name="RULE_GOV_NON_COMPLIANCE",
                        rule_version=ALERT_RULE_ENGINE_VERSION,
                        alert_confidence_score=conf_score,
                        alert_confidence_level=conf_level,
                        reason_codes=[REASON_COMPLIANCE_FAILURE_DETECTED],
                        source_entity_type=AlertSourceEntityType.GOVERNANCE_REVIEW,
                        source_entity_id=None,
                        occurrence_count=1,
                        first_triggered_at=now,
                        last_triggered_at=now,
                        alert_payload={"non_compliant_review_count": non_compliant_count, "threshold": 75.0},
                    )
                )

        # ----------------------------------------------------------------------
        # 4. BENEFITS REALIZATION RULES
        # ----------------------------------------------------------------------
        if benefits:
            total_expected = sum(float(getattr(b, "expected_value", 0.0) or 0.0) for b in benefits)
            total_realized = sum(float(getattr(b, "realized_value", 0.0) or 0.0) for b in benefits)
            if total_expected > 0:
                realization_rate = (total_realized / total_expected) * 100.0
                if realization_rate < 60.0:
                    sev = MonitoringSeverity.HIGH if realization_rate < 40.0 else MonitoringSeverity.MEDIUM
                    fp = generate_alert_fingerprint(organization_id, "RULE_BENEFITS_LAG", "SYSTEM", None)
                    candidate_alerts.append(
                        MonitoringAlert(
                            organization_id=str(organization_id),
                            alert_fingerprint=fp,
                            category=MonitoringCategory.BENEFITS,
                            severity=sev,
                            title=f"Benefits Realization Deficit ({realization_rate:.1f}%)",
                            description=f"Total benefits realization of {realization_rate:.1f}% lags behind expected projections (< 60.0%).",
                            rule_name="RULE_BENEFITS_LAG",
                            rule_version=ALERT_RULE_ENGINE_VERSION,
                            alert_confidence_score=conf_score,
                            alert_confidence_level=conf_level,
                            reason_codes=[REASON_BENEFIT_REALIZATION_LAG],
                            source_entity_type=AlertSourceEntityType.BENEFIT,
                            source_entity_id=None,
                            occurrence_count=1,
                            first_triggered_at=now,
                            last_triggered_at=now,
                            alert_payload={"realization_rate": round(realization_rate, 2), "threshold": 60.0},
                        )
                    )

        # ----------------------------------------------------------------------
        # 5. PORTFOLIO BALANCE & STRUCTURAL EXPOSURE RULES
        # ----------------------------------------------------------------------
        if portfolio_balance:
            bal_score = float(portfolio_balance.get("portfolio_balance_score", 100.0) or 100.0)
            spof_count = int(portfolio_balance.get("single_points_of_failure_count", 0) or 0)
            exposure_score = float(portfolio_balance.get("portfolio_strategic_exposure_score", 0.0) or 0.0)

            # Imbalance Alert
            if bal_score < 60.0:
                sev = MonitoringSeverity.HIGH if bal_score < 45.0 else MonitoringSeverity.MEDIUM
                fp = generate_alert_fingerprint(organization_id, "RULE_PORTFOLIO_IMBALANCE", "SYSTEM", None)
                candidate_alerts.append(
                    MonitoringAlert(
                        organization_id=str(organization_id),
                        alert_fingerprint=fp,
                        category=MonitoringCategory.PORTFOLIO,
                        severity=sev,
                        title=f"Structural Portfolio Imbalance ({bal_score:.1f})",
                        description=f"Portfolio structural balance score dropped to {bal_score:.1f}, indicating high concentration risk.",
                        rule_name="RULE_PORTFOLIO_IMBALANCE",
                        rule_version=ALERT_RULE_ENGINE_VERSION,
                        alert_confidence_score=conf_score,
                        alert_confidence_level=conf_level,
                        reason_codes=[REASON_PORTFOLIO_IMBALANCE_DETECTED],
                        source_entity_type=AlertSourceEntityType.SYSTEM,
                        source_entity_id=None,
                        occurrence_count=1,
                        first_triggered_at=now,
                        last_triggered_at=now,
                        alert_payload={"portfolio_balance_score": bal_score, "threshold": 60.0},
                    )
                )

            # Single Point of Failure (SPOF) Cluster Alert
            if spof_count >= 2:
                sev = MonitoringSeverity.CRITICAL if spof_count >= 4 else MonitoringSeverity.HIGH
                fp = generate_alert_fingerprint(organization_id, "RULE_PORTFOLIO_SPOF_CLUSTER", "SYSTEM", None)
                candidate_alerts.append(
                    MonitoringAlert(
                        organization_id=str(organization_id),
                        alert_fingerprint=fp,
                        category=MonitoringCategory.PORTFOLIO,
                        severity=sev,
                        title=f"Dependency Cluster Bottleneck ({spof_count} SPOFs)",
                        description=f"Detected {spof_count} single points of failure across initiative dependency graph.",
                        rule_name="RULE_PORTFOLIO_SPOF_CLUSTER",
                        rule_version=ALERT_RULE_ENGINE_VERSION,
                        alert_confidence_score=conf_score,
                        alert_confidence_level=conf_level,
                        reason_codes=[REASON_SPOF_CLUSTER_DETECTED],
                        source_entity_type=AlertSourceEntityType.SYSTEM,
                        source_entity_id=None,
                        occurrence_count=1,
                        first_triggered_at=now,
                        last_triggered_at=now,
                        alert_payload={"single_points_of_failure_count": spof_count},
                    )
                )

        # ----------------------------------------------------------------------
        # 6. DATA QUALITY & SNAPSHOT RULES
        # ----------------------------------------------------------------------
        if coverage_rate < 80.0:
            fp = generate_alert_fingerprint(organization_id, "RULE_DATA_QUALITY_COVERAGE", "SYSTEM", None)
            candidate_alerts.append(
                MonitoringAlert(
                    organization_id=str(organization_id),
                    alert_fingerprint=fp,
                    category=MonitoringCategory.DATA_QUALITY,
                    severity=MonitoringSeverity.MEDIUM,
                    title=f"Telemetry Coverage Deficit ({coverage_rate:.1f}%)",
                    description=f"Metric coverage rate of {coverage_rate:.1f}% is below the 80.0% data quality threshold.",
                    rule_name="RULE_DATA_QUALITY_COVERAGE",
                    rule_version=ALERT_RULE_ENGINE_VERSION,
                    alert_confidence_score=conf_score,
                    alert_confidence_level=conf_level,
                    reason_codes=[REASON_METRIC_COVERAGE_DEFICIT],
                    source_entity_type=AlertSourceEntityType.SYSTEM,
                    source_entity_id=None,
                    occurrence_count=1,
                    first_triggered_at=now,
                    last_triggered_at=now,
                    alert_payload={"metric_coverage_rate": coverage_rate, "threshold": 80.0},
                )
            )

        if latest_snapshot:
            snap_date = getattr(latest_snapshot, "snapshot_date", None)
            if snap_date:
                snap_age_days = (now.date() - snap_date).days
                if snap_age_days >= 60:
                    sev = MonitoringSeverity.HIGH if snap_age_days >= 90 else MonitoringSeverity.MEDIUM
                    fp = generate_alert_fingerprint(organization_id, "RULE_SNAPSHOT_RECENCY_BREACH", "SNAPSHOT", getattr(latest_snapshot, "id", None))
                    candidate_alerts.append(
                        MonitoringAlert(
                            organization_id=str(organization_id),
                            alert_fingerprint=fp,
                            category=MonitoringCategory.SNAPSHOT,
                            severity=sev,
                            title=f"Snapshot Recency Staleness ({snap_age_days} Days)",
                            description=f"Latest snapshot was captured {snap_age_days} days ago (> 60 days standard lookback).",
                            rule_name="RULE_SNAPSHOT_RECENCY_BREACH",
                            rule_version=ALERT_RULE_ENGINE_VERSION,
                            alert_confidence_score=conf_score,
                            alert_confidence_level=conf_level,
                            reason_codes=[REASON_SNAPSHOT_RECENCY_BREACH],
                            source_entity_type=AlertSourceEntityType.SNAPSHOT,
                            source_entity_id=str(getattr(latest_snapshot, "id", None)),
                            occurrence_count=1,
                            first_triggered_at=now,
                            last_triggered_at=now,
                            alert_payload={"snapshot_age_days": snap_age_days, "threshold": 60},
                        )
                    )

        return candidate_alerts
