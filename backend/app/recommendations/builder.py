"""RecommendationBuilder synthesizing complete Recommendation database entities."""

from typing import Any, Dict, Optional

from app.core.constants import RecommendationSource, RecommendationStatus
from app.models.diagnostic_finding import DiagnosticFinding
from app.models.recommendation import Recommendation
from app.models.root_cause_analysis import RootCauseAnalysis
from app.recommendations.effort_estimator import EffortEstimator
from app.recommendations.impact_estimator import ImpactEstimator
from app.recommendations.priority_engine import PriorityEngine
from app.recommendations.rule_model import RecommendationRule
from app.recommendations.template_model import RecommendationTemplate


class RecommendationBuilder:
    """
    Factory builder transforming findings, root causes, and action templates
    into fully populated, validated Recommendation model instances.
    """

    @classmethod
    def build(
        cls,
        template: RecommendationTemplate,
        finding: DiagnosticFinding,
        rule: RecommendationRule,
        rca: Optional[RootCauseAnalysis] = None,
        source: RecommendationSource = RecommendationSource.RULE_ENGINE,
    ) -> Recommendation:
        """
        Synthesizes a Recommendation entity with complete action plans,
        evidence payloads, outcomes schema, and explainability narratives.
        """
        # 1. Calculate Scores
        impact_score = ImpactEstimator.estimate(
            template=template,
            finding=finding,
            rule=rule,
            rca=rca,
        )
        effort_score = EffortEstimator.estimate(
            template=template,
            rule=rule,
            finding=finding,
        )

        finding_conf = getattr(finding, "confidence_score", 0.90)
        rca_conf = getattr(rca, "confidence_score", 1.00) if rca else 1.00
        combined_conf = round(max(0.10, min(1.00, finding_conf * rca_conf)), 4)

        priority, priority_numeric = PriorityEngine.evaluate_priority(
            impact_score=impact_score,
            confidence_score=combined_conf,
            effort_score=effort_score,
            finding=finding,
        )

        # 2. Build Explainability Narrative (why_recommended)
        why_recommended = cls._build_why_recommended(finding, rca, rule, template)

        # 3. Build Evidence Payload
        evidence = cls._build_evidence(finding, rca, rule, combined_conf)

        # 4. Build Outcomes Payload
        outcomes = cls._build_outcomes(finding, template)

        # 5. Determine Recommendation Type
        rec_type = template.recommendation_type or rule.recommendation_type

        return Recommendation(
            dataset_id=finding.dataset_id,
            finding_id=finding.id,
            root_cause_analysis_id=rca.id if rca else None,
            recommendation_type=rec_type,
            priority=priority,
            status=RecommendationStatus.PENDING,
            source=source,
            title=template.title,
            description=template.description,
            why_recommended=why_recommended,
            confidence_score=combined_conf,
            estimated_impact_score=impact_score,
            estimated_effort_score=effort_score,
            expected_time_to_value=template.expected_time_to_value,
            action_plan=list(template.actions),
            success_metrics=list(template.success_metrics),
            evidence=evidence,
            outcomes=outcomes,
        )

    @classmethod
    def _build_why_recommended(
        cls,
        finding: DiagnosticFinding,
        rca: Optional[RootCauseAnalysis],
        rule: RecommendationRule,
        template: RecommendationTemplate,
    ) -> str:
        """Constructs human-readable explainability paragraph."""
        finding_title = finding.title
        finding_sev = finding.severity.value if hasattr(finding.severity, "value") else str(finding.severity)

        if rca is not None:
            cause_title = rca.root_cause_finding.title if rca.root_cause_finding else "Identified root cause"
            cause_sev = (
                rca.root_cause_finding.severity.value
                if rca.root_cause_finding and hasattr(rca.root_cause_finding.severity, "value")
                else "HIGH"
            )
            narrative = (
                f"Primary issue '{finding_title}' ({finding_sev} severity) is linked to '{cause_title}' ({cause_sev} severity). "
                f"{rule.description} Initiating '{template.title}' will directly address the driver and recover business performance."
            )
        else:
            narrative = (
                f"Detected diagnostic finding '{finding_title}' ({finding_sev} severity) requires operational intervention. "
                f"{rule.description} Implementing '{template.title}' is recommended to mitigate ongoing risk."
            )

        return narrative.strip()

    @classmethod
    def _build_evidence(
        cls,
        finding: DiagnosticFinding,
        rca: Optional[RootCauseAnalysis],
        rule: RecommendationRule,
        confidence: float,
    ) -> Dict[str, Any]:
        """Constructs structured evidence metadata."""
        root_cause_title = None
        root_cause_id = None
        if rca is not None and rca.root_cause_finding:
            root_cause_title = rca.root_cause_finding.title
            root_cause_id = str(rca.root_cause_finding.id)

        return {
            "finding": finding.title,
            "finding_id": str(finding.id),
            "finding_severity": finding.severity.value if hasattr(finding.severity, "value") else str(finding.severity),
            "root_cause": root_cause_title,
            "root_cause_id": root_cause_id,
            "rule": rule.description,
            "confidence": confidence,
        }

    @classmethod
    def _build_outcomes(
        cls,
        finding: DiagnosticFinding,
        template: RecommendationTemplate,
    ) -> Dict[str, Any]:
        """Constructs structured outcome measurement targets."""
        metric_name = template.target_metric_name or (
            template.success_metrics[0] if template.success_metrics else "Business Performance KPI"
        )

        # Extract baseline observed value if available
        observed = None
        if finding.supporting_data:
            observed = finding.supporting_data.get("observed")

        baseline_val = float(observed) if observed is not None and isinstance(observed, (int, float)) else 0.68
        target_val = round(baseline_val * (1.0 + template.target_improvement_ratio), 2)

        return {
            "expected_metric": metric_name,
            "baseline": baseline_val,
            "target": target_val,
            "measurement_period": template.measurement_period,
        }
