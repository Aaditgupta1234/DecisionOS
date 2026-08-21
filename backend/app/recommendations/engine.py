"""Recommendation Engine orchestrating rule-based business prescription synthesis, ranking, and deduplication."""

import logging
from collections import defaultdict
from typing import Dict, List, Optional
from uuid import UUID

from app.core.constants import RecommendationPriority, RecommendationSource
from app.models.diagnostic_finding import DiagnosticFinding
from app.models.recommendation import Recommendation
from app.models.root_cause_analysis import RootCauseAnalysis
from app.recommendations.builder import RecommendationBuilder
from app.recommendations.rule_registry import RecommendationRuleRegistry

logger = logging.getLogger(__name__)

# Priority ordinal weights for deterministic sorting
PRIORITY_ORDER = {
    RecommendationPriority.CRITICAL: 4,
    RecommendationPriority.HIGH: 3,
    RecommendationPriority.MEDIUM: 2,
    RecommendationPriority.LOW: 1,
}


class RecommendationEngine:
    """
    Core orchestrator generating prioritized, actionable business recommendations
    from diagnostic findings and root cause analyses.
    
    Responsibilities:
        1. Maps findings and causal drivers to domain action templates in RecommendationRuleRegistry.
        2. Evaluates multiple action strategies per problem.
        3. Eliminates duplicate or redundant recommendations.
        4. Applies deterministic multi-factor ranking (Priority DESC, Impact DESC, Confidence DESC, Effort ASC).
    """

    def __init__(self, rule_registry: Optional[RecommendationRuleRegistry] = None):
        self.rule_registry = rule_registry or RecommendationRuleRegistry(use_defaults=True)

    def generate_recommendations(
        self,
        findings: List[DiagnosticFinding],
        root_causes: Optional[List[RootCauseAnalysis]] = None,
        source: RecommendationSource = RecommendationSource.RULE_ENGINE,
        health_score: Optional[int] = None,
    ) -> List[Recommendation]:
        """
        Executes end-to-end recommendation generation over a collection of findings and RCAs.
        """
        if not findings:
            return []

        rcas = root_causes or []
        # Group root causes by primary_finding_id
        rca_by_finding: Dict[UUID, List[RootCauseAnalysis]] = defaultdict(list)
        for rca in rcas:
            rca_by_finding[rca.primary_finding_id].append(rca)

        candidates: List[Recommendation] = []
        seen_keys = set()
        covered_finding_ids = set()

        for finding in findings:
            finding_subtype = self._extract_subtype(finding)
            finding_rcas = rca_by_finding.get(finding.id, [])

            if finding_rcas:
                # Generate from root cause specific rules
                for rca in finding_rcas:
                    rc_subtype = (
                        self._extract_subtype(rca.root_cause_finding)
                        if rca.root_cause_finding
                        else None
                    )

                    templates_and_rules = self.rule_registry.find_templates(
                        finding_subtype=finding_subtype,
                        root_cause_subtype=rc_subtype,
                    )

                    for tmpl, rule in templates_and_rules:
                        dedup_key = (finding.id, tmpl.title)
                        if dedup_key in seen_keys:
                            continue
                        seen_keys.add(dedup_key)
                        covered_finding_ids.add(finding.id)
                        if rca.root_cause_finding_id:
                            covered_finding_ids.add(rca.root_cause_finding_id)
                        if rca.root_cause_finding:
                            covered_finding_ids.add(rca.root_cause_finding.id)

                        rec = RecommendationBuilder.build(
                            template=tmpl,
                            finding=finding,
                            rule=rule,
                            rca=rca,
                            source=source,
                        )
                        candidates.append(rec)
            else:
                # Generate from finding-only rules
                templates_and_rules = self.rule_registry.find_templates(
                    finding_subtype=finding_subtype,
                    root_cause_subtype=None,
                )

                for tmpl, rule in templates_and_rules:
                    dedup_key = (finding.id, tmpl.title)
                    if dedup_key in seen_keys:
                        continue
                    seen_keys.add(dedup_key)
                    covered_finding_ids.add(finding.id)

                    rec = RecommendationBuilder.build(
                        template=tmpl,
                        finding=finding,
                        rule=rule,
                        rca=None,
                        source=source,
                    )
                    candidates.append(rec)

        # Fallback synthesis for any findings that did not match a specific template
        from app.core.constants import (
            RecommendationType,
            RecommendationPriority,
            RecommendationStatus,
            ExpectedTimeToValue,
        )
        for finding in findings:
            finding_has_rec = finding.id in covered_finding_ids or any(r.finding_id == finding.id for r in candidates)
            if not finding_has_rec:
                title_clean = finding.title.replace("Excessive ", "Resolve ").replace("High ", "Optimize ").replace("Decline in ", "Reverse Decline in ")
                sev_val = finding.severity.value if hasattr(finding.severity, "value") else str(finding.severity)
                rec = Recommendation(
                    dataset_id=finding.dataset_id,
                    finding_id=finding.id,
                    title=f"Initiative: {title_clean}",
                    description=f"Actionable intervention to address: {finding.description}",
                    why_recommended=finding.business_impact or "Directly mitigates high-impact operational friction diagnosed in the telemetry.",
                    recommendation_type=RecommendationType.OPERATIONAL_EFFICIENCY,
                    priority=RecommendationPriority.HIGH if sev_val in ["CRITICAL", "HIGH"] else RecommendationPriority.MEDIUM,
                    status=RecommendationStatus.PENDING,
                    source=source,
                    confidence_score=finding.confidence_score or 0.85,
                    estimated_impact_score=0.85 if sev_val in ["CRITICAL", "HIGH"] else 0.65,
                    estimated_effort_score=0.40,
                    expected_time_to_value=ExpectedTimeToValue.SHORT_TERM,
                    action_plan=[
                        f"Triage underlying operational factors driving '{finding.title}'.",
                        "Deploy targeted process optimizations and workflow safeguards.",
                        "Establish automated alerting threshold to monitor leading recovery indicators.",
                        "Review 30-day post-implementation recovery impact on business unit KPIs.",
                    ],
                    success_metrics=[finding.metric_key or "operational_efficiency"],
                    evidence={"finding_title": finding.title, "severity": sev_val},
                    outcomes={
                        "primary_kpi_impact": f"Recovery in {finding.metric_key or 'core operations'}",
                        "estimated_improvement": "+12% to +20%",
                    },
                )
                candidates.append(rec)

        # Invariant: If health score <= 60 and no CRITICAL recommendations exist, synthesize Emergency Recovery Program
        if (health_score is not None and health_score <= 60) or (findings and not candidates):
            primary_finding = findings[0] if findings else None
            if primary_finding:
                has_emergency_rec = any(r.title == "Emergency Business Recovery Program" for r in candidates)
                if not has_emergency_rec:
                    emergency_rec = Recommendation(
                        dataset_id=primary_finding.dataset_id,
                        finding_id=primary_finding.id,
                        title="Emergency Business Recovery Program",
                        description="Comprehensive emergency stabilization intervention to triage multiple critical business indicators breaching allowable thresholds.",
                        why_recommended="Business health has breached critical stability levels (Score <= 60), requiring immediate executive intervention to arrest operational decline.",
                        recommendation_type=RecommendationType.OPERATIONAL_EFFICIENCY,
                        priority=RecommendationPriority.CRITICAL,
                        status=RecommendationStatus.PENDING,
                        source=source,
                        confidence_score=0.95,
                        estimated_impact_score=0.95,
                        estimated_effort_score=0.30,
                        expected_time_to_value=ExpectedTimeToValue.IMMEDIATE,
                        action_plan=[
                            "Convene emergency operational taskforce to triage core bottleneck drivers.",
                            "Enforce immediate containment protocols across affected business workflows.",
                            "Deploy daily telemetry monitoring on leading recovery indicators.",
                            "Establish 14-day rapid review checkpoint to evaluate stabilization progress.",
                        ],
                        success_metrics=["business_health_score", "order_completion_rate"],
                        evidence={"health_score": health_score, "finding_count": len(findings)},
                        outcomes={
                            "primary_kpi_impact": "Operational Stabilization",
                            "estimated_improvement": "+20% to +35% Recovery",
                        },
                    )
                    candidates.append(emergency_rec)

        # Deterministic Ranking:
        # Priority (DESC) -> Estimated Impact (DESC) -> Confidence (DESC) -> Estimated Effort (ASC)
        candidates.sort(
            key=lambda r: (
                PRIORITY_ORDER.get(r.priority, 1),
                r.estimated_impact_score,
                r.confidence_score,
                -r.estimated_effort_score,  # negative effort for ascending effort order
            ),
            reverse=True,
        )

        return candidates

    @staticmethod
    def _extract_subtype(finding: DiagnosticFinding) -> str:
        """Helper extracting subtype string from finding supporting_data or finding_type."""
        if finding.supporting_data and "subtype" in finding.supporting_data:
            return finding.supporting_data["subtype"]
        return finding.finding_type.value
