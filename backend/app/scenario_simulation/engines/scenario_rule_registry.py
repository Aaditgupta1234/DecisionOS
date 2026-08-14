"""ScenarioRuleRegistry providing dependency-ordered, cycle-protected deterministic metric propagation."""

from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Set, Tuple


@dataclass
class ScenarioRule:
    """Explicit deterministic metric transformation rule."""
    rule_id: str
    input_metrics: Set[str]
    output_metrics: Set[str]
    priority: int  # 1 = highest priority (evaluates first)
    description: str
    version: str = "1.0"
    apply_fn: Optional[Callable[[Dict[str, float]], Dict[str, float]]] = None


class ScenarioRuleRegistry:
    """
    Registry and execution engine for explicit, deterministic cross-metric propagation rules.
    Enforces a strict Directed Acyclic Execution model to prevent circular propagation loops.
    """

    def __init__(self):
        self._rules: List[ScenarioRule] = []
        self._register_default_rules()

    def register_rule(self, rule: ScenarioRule) -> None:
        """Registers a propagation rule and maintains priority-sorted execution order."""
        self._rules.append(rule)
        self._rules.sort(key=lambda r: r.priority)

    def _register_default_rules(self) -> None:
        """Registers canonical DecisionOS deterministic propagation rules."""

        # 1. Churn -> Retention
        def _apply_churn_to_retention(metrics: Dict[str, float]) -> Dict[str, float]:
            churn = metrics["customer_churn_rate"]
            retention = max(0.0, min(100.0, round(100.0 - churn, 4)))
            return {"customer_retention_rate": retention}

        self.register_rule(
            ScenarioRule(
                rule_id="rule_churn_to_retention",
                input_metrics={"customer_churn_rate"},
                output_metrics={"customer_retention_rate"},
                priority=1,
                description="Derives customer retention rate from customer churn rate (100 - churn).",
                apply_fn=_apply_churn_to_retention,
            )
        )

        # 2. Retention -> Churn
        def _apply_retention_to_churn(metrics: Dict[str, float]) -> Dict[str, float]:
            retention = metrics["customer_retention_rate"]
            churn = max(0.0, min(100.0, round(100.0 - retention, 4)))
            return {"customer_churn_rate": churn}

        self.register_rule(
            ScenarioRule(
                rule_id="rule_retention_to_churn",
                input_metrics={"customer_retention_rate"},
                output_metrics={"customer_churn_rate"},
                priority=1,
                description="Derives customer churn rate from customer retention rate (100 - retention).",
                apply_fn=_apply_retention_to_churn,
            )
        )

        # 3. Total Orders + Completion Rate -> Completed Orders
        def _apply_orders_completion(metrics: Dict[str, float]) -> Dict[str, float]:
            total_orders = metrics["total_orders"]
            rate = metrics["completion_rate"]
            completed = round(total_orders * (rate / 100.0))
            return {"completed_orders": float(completed)}

        self.register_rule(
            ScenarioRule(
                rule_id="rule_orders_completion",
                input_metrics={"total_orders", "completion_rate"},
                output_metrics={"completed_orders"},
                priority=2,
                description="Calculates completed order count from total orders and completion rate.",
                apply_fn=_apply_orders_completion,
            )
        )

        # 4. Total Orders + Completed Orders -> Cancelled Orders
        def _apply_orders_cancellation(metrics: Dict[str, float]) -> Dict[str, float]:
            total_orders = metrics["total_orders"]
            completed = metrics["completed_orders"]
            cancelled = max(0.0, float(round(total_orders - completed)))
            return {"cancelled_orders": cancelled}

        self.register_rule(
            ScenarioRule(
                rule_id="rule_orders_cancellation",
                input_metrics={"total_orders", "completed_orders"},
                output_metrics={"cancelled_orders"},
                priority=3,
                description="Calculates cancelled orders as difference between total and completed orders.",
                apply_fn=_apply_orders_cancellation,
            )
        )

        # 5. Total Revenue + Total Orders -> Average Revenue
        def _apply_revenue_average(metrics: Dict[str, float]) -> Dict[str, float]:
            tot_rev = metrics["total_revenue"]
            orders = metrics["total_orders"]
            avg_rev = round(tot_rev / orders, 2) if orders > 0 else 0.0
            return {"average_revenue": avg_rev}

        self.register_rule(
            ScenarioRule(
                rule_id="rule_revenue_average",
                input_metrics={"total_revenue", "total_orders"},
                output_metrics={"average_revenue"},
                priority=4,
                description="Recalculates average revenue per order when revenue or orders change.",
                apply_fn=_apply_revenue_average,
            )
        )

        # 6. Total Revenue + Unique Customers -> Revenue Per Customer
        def _apply_revenue_per_customer(metrics: Dict[str, float]) -> Dict[str, float]:
            tot_rev = metrics["total_revenue"]
            custs = metrics["unique_customers"]
            rev_cust = round(tot_rev / custs, 2) if custs > 0 else 0.0
            return {"revenue_per_customer": rev_cust}

        self.register_rule(
            ScenarioRule(
                rule_id="rule_revenue_per_customer",
                input_metrics={"total_revenue", "unique_customers"},
                output_metrics={"revenue_per_customer"},
                priority=4,
                description="Recalculates revenue per customer when total revenue or customer count changes.",
                apply_fn=_apply_revenue_per_customer,
            )
        )

    def apply_propagation(
        self,
        current_metrics: Dict[str, float],
        directly_assumed_keys: Set[str],
    ) -> Tuple[Dict[str, float], Dict[str, str]]:
        """
        Executes registered rules in deterministic priority order.
        
        Guarantees:
            1. Directed Acyclic Execution (Single source of change).
            2. Directly assumed metrics are NEVER overwritten by derived rules.
            3. Already derived metrics are evaluated once and cannot back-propagate into root inputs.
            
        Returns:
            Tuple of (updated_metrics_dict, metric_key_to_source_rule_id_map).
        """
        working = dict(current_metrics)
        derived_sources: Dict[str, str] = {}
        evaluated_outputs: Set[str] = set(directly_assumed_keys)

        for rule in self._rules:
            # Check if all required inputs exist in working metrics
            if not rule.input_metrics.issubset(working.keys()):
                continue

            # Check if rule output targets can be derived without violating single source of change
            # Do NOT overwrite direct assumptions or already evaluated outputs
            targets_to_derive = [t for t in rule.output_metrics if t not in evaluated_outputs]
            if not targets_to_derive:
                continue

            # Only trigger propagation if at least one input metric was modified (direct or derived)
            inputs_modified = any(k in evaluated_outputs for k in rule.input_metrics)
            if not inputs_modified:
                continue

            # Execute deterministic rule
            if rule.apply_fn:
                new_values = rule.apply_fn(working)
                for out_key, out_val in new_values.items():
                    if out_key not in evaluated_outputs:
                        working[out_key] = out_val
                        derived_sources[out_key] = rule.rule_id
                        evaluated_outputs.add(out_key)

        return working, derived_sources
