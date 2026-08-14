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

                    rec = RecommendationBuilder.build(
                        template=tmpl,
                        finding=finding,
                        rule=rule,
                        rca=None,
                        source=source,
                    )
                    candidates.append(rec)

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
