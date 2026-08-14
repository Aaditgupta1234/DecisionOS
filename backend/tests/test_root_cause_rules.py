"""Unit tests for RootCauseRule model and RootCauseRuleRegistry."""

import pytest

from app.core.constants import FindingSubtype, RelationshipStrength, RelationshipType
from app.root_cause.rule_model import RootCauseRule
from app.root_cause.rule_registry import RootCauseRuleRegistry


def test_root_cause_rule_dataclass():
    """Verifies RootCauseRule properties, strength enum mapping, and matching logic."""
    rule = RootCauseRule(
        cause_subtype=FindingSubtype.CHURN_INCREASE,
        effect_subtype=FindingSubtype.DECLINE,
        relationship_type=RelationshipType.CAUSES,
        relationship_strength=0.90,
        description="Customer churn spike drives revenue decline.",
        expected_correlation="NEGATIVE",
    )

    assert rule.cause_subtype == FindingSubtype.CHURN_INCREASE
    assert rule.effect_subtype == FindingSubtype.DECLINE
    assert rule.relationship_type == RelationshipType.CAUSES
    assert rule.relationship_strength == 0.90
    assert rule.strength_enum == RelationshipStrength.VERY_STRONG
    assert rule.matches(FindingSubtype.CHURN_INCREASE, FindingSubtype.DECLINE) is True
    assert rule.matches("CHURN_INCREASE", "DECLINE") is True
    assert rule.matches("RETENTION_PROBLEM", "DECLINE") is False


def test_rule_registry_default_rules():
    """Verifies default enterprise causal rules are pre-seeded in the registry."""
    registry = RootCauseRuleRegistry(use_defaults=True)
    rules = registry.list_rules()

    assert len(rules) >= 10

    # 1. Churn -> Revenue Decline
    rule1 = registry.find_rule(FindingSubtype.CHURN_INCREASE, FindingSubtype.DECLINE)
    assert rule1 is not None
    assert rule1.relationship_type == RelationshipType.CAUSES
    assert rule1.relationship_strength == 0.90

    # 2. Cost Spike -> Margin Compression
    rule2 = registry.find_rule(FindingSubtype.COST_SPIKE, FindingSubtype.MARGIN_COMPRESSION)
    assert rule2 is not None
    assert rule2.relationship_type == RelationshipType.CAUSES
    assert rule2.relationship_strength == 0.95

    # 3. Delivery Delay -> Churn Increase
    rule3 = registry.find_rule(FindingSubtype.DELIVERY_DELAY, FindingSubtype.CHURN_INCREASE)
    assert rule3 is not None
    assert rule3.relationship_type == RelationshipType.AMPLIFIES


def test_rule_registry_custom_registration_and_override():
    """Verifies custom rule registration and highest-strength selection."""
    registry = RootCauseRuleRegistry(use_defaults=False)
    assert len(registry.list_rules()) == 0

    rule_weak = RootCauseRule(
        cause_subtype=FindingSubtype.RETENTION_PROBLEM,
        effect_subtype=FindingSubtype.DECLINE,
        relationship_type=RelationshipType.CONTRIBUTES_TO,
        relationship_strength=0.50,
        description="Weak retention impact.",
    )
    rule_strong = RootCauseRule(
        cause_subtype=FindingSubtype.RETENTION_PROBLEM,
        effect_subtype=FindingSubtype.DECLINE,
        relationship_type=RelationshipType.CAUSES,
        relationship_strength=0.85,
        description="Strong retention impact.",
    )

    registry.register(rule_weak)
    registry.register(rule_strong)

    # find_rule should return the rule with highest strength (0.85)
    matched = registry.find_rule("RETENTION_PROBLEM", "DECLINE")
    assert matched is not None
    assert matched.relationship_strength == 0.85
    assert matched.relationship_type == RelationshipType.CAUSES

    all_matches = registry.find_matching_rules("RETENTION_PROBLEM", "DECLINE")
    assert len(all_matches) == 2
