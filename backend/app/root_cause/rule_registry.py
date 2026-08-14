"""Root Cause Rule Registry managing enterprise causal rules and lookups."""

from typing import List, Optional

from app.core.constants import FindingSubtype, RelationshipType
from app.root_cause.rule_model import RootCauseRule


class RootCauseRuleRegistry:
    """
    Central repository for causal rules connecting business anomalies.
    
    Provides methods to register custom rules, query candidate pairs, and
    retrieve domain-validated causal linkages.
    """

    def __init__(self, use_defaults: bool = True):
        self._rules: List[RootCauseRule] = []
        if use_defaults:
            self._register_default_rules()

    def register(self, rule: RootCauseRule) -> None:
        """Registers a new causal rule into the registry."""
        # Prevent exact duplicate registrations
        for existing in self._rules:
            if (
                existing.cause_subtype == rule.cause_subtype
                and existing.effect_subtype == rule.effect_subtype
                and existing.relationship_type == rule.relationship_type
            ):
                return
        self._rules.append(rule)

    def find_rule(
        self,
        cause_subtype: FindingSubtype | str,
        effect_subtype: FindingSubtype | str,
    ) -> Optional[RootCauseRule]:
        """Finds the highest-strength matching causal rule between a cause and effect subtype."""
        matches = self.find_matching_rules(cause_subtype, effect_subtype)
        if not matches:
            return None
        # Return the rule with the highest causal strength
        return max(matches, key=lambda r: r.relationship_strength)

    def find_matching_rules(
        self,
        cause_subtype: FindingSubtype | str,
        effect_subtype: FindingSubtype | str,
    ) -> List[RootCauseRule]:
        """Returns all registered causal rules that match the candidate pair."""
        return [rule for rule in self._rules if rule.matches(cause_subtype, effect_subtype)]

    def list_rules(self) -> List[RootCauseRule]:
        """Returns a copy of all registered causal rules."""
        return list(self._rules)

    def clear(self) -> None:
        """Clears all registered rules (useful for isolated unit testing)."""
        self._rules.clear()

    def _register_default_rules(self) -> None:
        """Registers enterprise cross-domain causal rules."""
        defaults = [
            # 1. Customer Churn -> Revenue Decline
            RootCauseRule(
                cause_subtype=FindingSubtype.CHURN_INCREASE,
                effect_subtype=FindingSubtype.DECLINE,
                relationship_type=RelationshipType.CAUSES,
                relationship_strength=0.90,
                description="Customer churn spike directly decreases recurring and repeat revenue streams.",
                expected_correlation="NEGATIVE",
            ),
            # 2. Low Retention -> Revenue Decline
            RootCauseRule(
                cause_subtype=FindingSubtype.RETENTION_PROBLEM,
                effect_subtype=FindingSubtype.DECLINE,
                relationship_type=RelationshipType.CONTRIBUTES_TO,
                relationship_strength=0.80,
                description="Low customer retention reduces repeat purchase volume, depressing baseline top-line sales.",
                expected_correlation="POSITIVE",
            ),
            # 3. Product Performance Decline -> Revenue Decline
            RootCauseRule(
                cause_subtype=FindingSubtype.PRODUCT_PERFORMANCE_DECLINE,
                effect_subtype=FindingSubtype.DECLINE,
                relationship_type=RelationshipType.CAUSES,
                relationship_strength=0.85,
                description="Contraction in core product categories reduces total sales volume and revenue generation.",
                expected_correlation="POSITIVE",
            ),
            # 4. Operating Cost Spike -> Gross Margin Compression
            RootCauseRule(
                cause_subtype=FindingSubtype.COST_SPIKE,
                effect_subtype=FindingSubtype.MARGIN_COMPRESSION,
                relationship_type=RelationshipType.CAUSES,
                relationship_strength=0.95,
                description="Surges in fulfillment, procurement, or operating expenses directly compress gross profit margins.",
                expected_correlation="NEGATIVE",
            ),
            # 5. Low Retention -> Customer Growth Slowdown
            RootCauseRule(
                cause_subtype=FindingSubtype.RETENTION_PROBLEM,
                effect_subtype=FindingSubtype.CUSTOMER_GROWTH_SLOWDOWN,
                relationship_type=RelationshipType.CONTRIBUTES_TO,
                relationship_strength=0.75,
                description="High customer attrition outpaces new customer acquisitions, slowing net active customer growth.",
                expected_correlation="POSITIVE",
            ),
            # 6. Delivery Delay -> Customer Churn Spike
            RootCauseRule(
                cause_subtype=FindingSubtype.DELIVERY_DELAY,
                effect_subtype=FindingSubtype.CHURN_INCREASE,
                relationship_type=RelationshipType.AMPLIFIES,
                relationship_strength=0.80,
                description="Extended fulfillment lead times and shipping delays increase customer dissatisfaction, amplifying churn.",
                expected_correlation="POSITIVE",
            ),
            # 7. Delivery Delay -> Operational Inefficiency
            RootCauseRule(
                cause_subtype=FindingSubtype.DELIVERY_DELAY,
                effect_subtype=FindingSubtype.OPERATIONAL_INEFFICIENCY,
                relationship_type=RelationshipType.CAUSES,
                relationship_strength=0.85,
                description="Fulfillment transit bottlenecks increase order cancellation rates and operational backlogs.",
                expected_correlation="POSITIVE",
            ),
            # 8. Product Concentration Risk -> Revenue Volatility
            RootCauseRule(
                cause_subtype=FindingSubtype.PRODUCT_CONCENTRATION_RISK,
                effect_subtype=FindingSubtype.VOLATILITY,
                relationship_type=RelationshipType.AMPLIFIES,
                relationship_strength=0.80,
                description="Heavy revenue concentration in few products amplifies overall business revenue volatility.",
                expected_correlation="POSITIVE",
            ),
            # 9. Underperforming Products -> Margin Compression
            RootCauseRule(
                cause_subtype=FindingSubtype.UNDERPERFORMING_PRODUCT,
                effect_subtype=FindingSubtype.MARGIN_COMPRESSION,
                relationship_type=RelationshipType.CONTRIBUTES_TO,
                relationship_strength=0.65,
                description="Low-velocity or deeply discounted product inventory drags down blended gross margin margins.",
                expected_correlation="POSITIVE",
            ),
            # 10. Customer Growth Slowdown -> Revenue Stagnation
            RootCauseRule(
                cause_subtype=FindingSubtype.CUSTOMER_GROWTH_SLOWDOWN,
                effect_subtype=FindingSubtype.STAGNATION,
                relationship_type=RelationshipType.CAUSES,
                relationship_strength=0.80,
                description="Deceleration in new customer acquisition leads directly to stagnant top-line revenue growth.",
                expected_correlation="POSITIVE",
            ),
        ]
        for r in defaults:
            self.register(r)
