"""Isolated narrative and explanation generator for Root Cause Analysis."""

from typing import Optional

from app.models.diagnostic_finding import DiagnosticFinding
from app.root_cause.correlation_analyzer import CorrelationResult
from app.root_cause.rule_model import RootCauseRule


class RootCauseExplanationBuilder:
    """
    Synthesizes human-readable narrative explanations detailing why and how
    a root cause finding triggered the primary business issue.
    
    ISOLATION DESIGN:
    Kept separate from the core engine so that Phase 6 LLM Insights can seamlessly
    enhance, customize, or replace the synthesis logic without refactoring.
    """

    @classmethod
    def build_explanation(
        cls,
        cause_finding: DiagnosticFinding,
        effect_finding: DiagnosticFinding,
        rule: RootCauseRule,
        correlation_result: Optional[CorrelationResult] = None,
    ) -> str:
        """
        Builds a comprehensive explanation paragraph detailing the causal mechanism,
        observed data points, and empirical backing.
        """
        cause_title = cause_finding.title
        effect_title = effect_finding.title

        cause_sev = cause_finding.severity.value if hasattr(cause_finding.severity, "value") else str(cause_finding.severity)
        effect_sev = effect_finding.severity.value if hasattr(effect_finding.severity, "value") else str(effect_finding.severity)

        # 1. Core mechanism from rule
        mechanism = rule.description

        # 2. Relational qualifier
        rel_type = rule.relationship_type.value
        strength_name = rule.strength_enum.value

        # 3. Empirical corroboration statement
        corroboration = ""
        if correlation_result is not None and correlation_result.coefficient is not None:
            r_val = correlation_result.coefficient
            direction = correlation_result.correlation_direction.lower()
            if correlation_result.supports_rule:
                corroboration = (
                    f" Statistical trend analysis confirms strong {direction} correlation "
                    f"(r = {r_val:+.2f}, sample size = {correlation_result.sample_size}), "
                    f"substantiating that {cause_title.lower()} is a primary driver."
                )
            else:
                corroboration = (
                    f" Observed trend correlation (r = {r_val:+.2f}) indicates complex or lagging dynamics, "
                    f"though the structural domain link remains validated."
                )
        else:
            corroboration = (
                f" Domain rule validation confirms this {strength_name.lower()} {rel_type.lower()} linkage "
                f"across observed operating metrics."
            )

        explanation = (
            f"Primary Issue: '{effect_title}' ({effect_sev} severity) is driven by "
            f"'{cause_title}' ({cause_sev} severity). {mechanism}{corroboration}"
        )

        return explanation.strip()
