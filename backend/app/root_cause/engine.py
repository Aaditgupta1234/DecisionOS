"""Root Cause Analysis Engine orchestrating causal inference, validation, and graph synthesis."""

import logging
from typing import Dict, List, Optional, Tuple
from uuid import UUID

from app.core.constants import FindingSubtype, RelationshipStrength, RelationshipType
from app.models.diagnostic_finding import DiagnosticFinding
from app.models.root_cause_analysis import RootCauseAnalysis
from app.root_cause.correlation_analyzer import CorrelationAnalyzer, CorrelationResult
from app.root_cause.explanation_builder import RootCauseExplanationBuilder
from app.root_cause.graph import RootCauseGraph
from app.root_cause.rule_model import RootCauseRule
from app.root_cause.rule_registry import RootCauseRuleRegistry
from app.root_cause.scoring import calculate_impact_score, calculate_root_cause_confidence

logger = logging.getLogger(__name__)


class RootCauseEngine:
    """
    Orchestrator for discovering and validating causal relationships among diagnostic findings.
    
    Responsibilities:
        1. Evaluates finding pairs against registered enterprise Causal Rules.
        2. Measures empirical trend correlation and directional alignment.
        3. Constructs a pure Python Causal DAG (RootCauseGraph).
        4. Calculates multi-factor confidence and business impact scores.
        5. Formulates human-readable explanations via RootCauseExplanationBuilder.
        6. Ranks and generates RootCauseAnalysis database entities.
    """

    def __init__(self, rule_registry: Optional[RootCauseRuleRegistry] = None):
        self.rule_registry = rule_registry or RootCauseRuleRegistry(use_defaults=True)

    def analyze(
        self,
        findings: List[DiagnosticFinding],
        dataset_id: Optional[UUID] = None,
    ) -> Tuple[List[RootCauseAnalysis], RootCauseGraph]:
        """
        Executes root cause discovery over a collection of diagnostic findings.
        
        Args:
            findings: List of DiagnosticFinding instances for a dataset.
            dataset_id: Optional UUID of the dataset (extracted from findings if omitted).
            
        Returns:
            Tuple of (list of persisted RootCauseAnalysis models, populated RootCauseGraph).
        """
        if not findings or len(findings) < 2:
            graph = RootCauseGraph()
            for f in (findings or []):
                graph.add_node(f)
            return [], graph

        target_dataset_id = dataset_id or findings[0].dataset_id
        graph = RootCauseGraph()
        analyses: List[RootCauseAnalysis] = []

        # 1. Populate all findings into graph vertices
        for f in findings:
            graph.add_node(f)

        # 2. Pairwise evaluation for causal links
        for cause_f in findings:
            cause_subtype = self._extract_subtype(cause_f)

            for effect_f in findings:
                if cause_f.id == effect_f.id:
                    continue

                effect_subtype = self._extract_subtype(effect_f)

                # Look up matching causal rule
                rule = self.rule_registry.find_rule(cause_subtype, effect_subtype)
                if rule is None:
                    continue

                # Ensure minimum finding confidence
                if cause_f.confidence_score < rule.min_confidence:
                    continue

                # 3. Analyze empirical correlation
                corr_result = CorrelationAnalyzer.analyze_finding_pair(cause_f, effect_f, rule)

                # 4. Calculate scores
                confidence = calculate_root_cause_confidence(
                    cause_finding=cause_f,
                    effect_finding=effect_f,
                    rule=rule,
                    correlation_result=corr_result,
                    evidence_count=2 if corr_result.sample_size > 0 else 1,
                )
                impact = calculate_impact_score(
                    effect_finding=effect_f,
                    cause_finding=cause_f,
                    rule=rule,
                )

                # 5. Add edge to DAG (guarantees acyclicity)
                added = graph.add_edge(
                    source_id=str(cause_f.id),
                    target_id=str(effect_f.id),
                    relationship_type=rule.relationship_type.value,
                    relationship_strength=rule.strength_enum.value,
                    confidence_score=confidence,
                    impact_score=impact,
                )

                if not added:
                    logger.debug(
                        f"Skipped edge {cause_f.id} -> {effect_f.id} to prevent graph cycle"
                    )
                    continue

                # 6. Generate narrative explanation
                explanation = RootCauseExplanationBuilder.build_explanation(
                    cause_finding=cause_f,
                    effect_finding=effect_f,
                    rule=rule,
                    correlation_result=corr_result,
                )

                # 7. Construct supporting evidence payload
                supporting_evidence = {
                    "rule": {
                        "cause_subtype": rule.cause_subtype.value,
                        "effect_subtype": rule.effect_subtype.value,
                        "relationship_type": rule.relationship_type.value,
                        "strength": rule.strength_enum.value,
                        "base_weight": rule.relationship_strength,
                        "description": rule.description,
                    },
                    "correlation": corr_result.to_dict(),
                    "cause_title": cause_f.title,
                    "effect_title": effect_f.title,
                    "cause_severity": cause_f.severity.value if hasattr(cause_f.severity, "value") else str(cause_f.severity),
                    "effect_severity": effect_f.severity.value if hasattr(effect_f.severity, "value") else str(effect_f.severity),
                }

                # 8. Instantiate model
                rca = RootCauseAnalysis(
                    dataset_id=target_dataset_id,
                    primary_finding_id=effect_f.id,
                    root_cause_finding_id=cause_f.id,
                    relationship_type=rule.relationship_type,
                    relationship_strength=rule.strength_enum,
                    confidence_score=confidence,
                    impact_score=impact,
                    explanation=explanation,
                    supporting_evidence=supporting_evidence,
                )
                analyses.append(rca)

        # 9. Deterministic ranking: Sort by Impact (descending), Confidence (descending)
        analyses.sort(key=lambda r: (r.impact_score, r.confidence_score), reverse=True)

        return analyses, graph

    @staticmethod
    def _extract_subtype(finding: DiagnosticFinding) -> str:
        """Helper to extract subtype from supporting_data or fallback to finding_type."""
        if finding.supporting_data and "subtype" in finding.supporting_data:
            return finding.supporting_data["subtype"]
        return finding.finding_type.value
