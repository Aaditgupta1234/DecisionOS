"""RecommendationRuleRegistry managing domain recommendation rules and multi-action template lookups."""

from typing import List, Optional, Tuple

from app.core.constants import ExpectedTimeToValue, FindingSubtype, RecommendationType
from app.recommendations.rule_model import RecommendationRule
from app.recommendations.template_model import RecommendationTemplate


class RecommendationRuleRegistry:
    """
    Central registry for domain-validated recommendation rules.
    
    Maps diagnostic finding and root cause causal driver combinations to
    multi-action RecommendationTemplate strategies.
    """

    def __init__(self, use_defaults: bool = True):
        self._rules: List[RecommendationRule] = []
        if use_defaults:
            self._register_default_rules()

    def register(self, rule: RecommendationRule) -> None:
        """Registers a new recommendation rule into the registry."""
        # Prevent exact duplicate registrations
        for existing in self._rules:
            if (
                existing.finding_subtype == rule.finding_subtype
                and existing.root_cause_subtype == rule.root_cause_subtype
                and existing.recommendation_type == rule.recommendation_type
            ):
                return
        self._rules.append(rule)

    def find_matching_rules(
        self,
        finding_subtype: FindingSubtype | str,
        root_cause_subtype: Optional[FindingSubtype | str] = None,
    ) -> List[RecommendationRule]:
        """Returns all registered recommendation rules that match the candidate pair."""
        return [rule for rule in self._rules if rule.matches(finding_subtype, root_cause_subtype)]

    def find_templates(
        self,
        finding_subtype: FindingSubtype | str,
        root_cause_subtype: Optional[FindingSubtype | str] = None,
    ) -> List[Tuple[RecommendationTemplate, RecommendationRule]]:
        """
        Returns a flattened list of (template, parent_rule) tuples matching the finding/RCA pair.
        Specific root-cause matches are prioritized over generic finding-only matches.
        """
        matching_rules = self.find_matching_rules(finding_subtype, root_cause_subtype)
        
        # If specific root-cause rules matched, filter to specific rules only to prevent template dilution
        specific_rules = [r for r in matching_rules if r.root_cause_subtype is not None]
        rules_to_use = specific_rules if specific_rules else matching_rules

        rules_to_use.sort(
            key=lambda r: (r.root_cause_subtype is not None, r.priority_weight),
            reverse=True,
        )

        results: List[Tuple[RecommendationTemplate, RecommendationRule]] = []
        seen_titles = set()

        for rule in rules_to_use:
            for tmpl in rule.templates:
                if tmpl.title not in seen_titles:
                    seen_titles.add(tmpl.title)
                    results.append((tmpl, rule))

        return results


    def list_rules(self) -> List[RecommendationRule]:
        """Returns a copy of all registered rules."""
        return list(self._rules)

    def clear(self) -> None:
        """Clears all registered rules (useful for test isolation)."""
        self._rules.clear()

    def _register_default_rules(self) -> None:
        """Registers enterprise cross-domain recommendation rules and multi-action templates."""
        # 1. CANONICAL BLUEPRINT: Revenue Decline <- Customer Churn Increase
        churn_to_rev_templates = [
            RecommendationTemplate(
                title="Launch Retention Campaign",
                description="Deploy segmented email, SMS, and proactive outreach campaigns to stabilize at-risk subscriber cohorts.",
                actions=[
                    "Analyze churn cohorts by tenure, purchase frequency, and product engagement.",
                    "Launch targeted retention email and SMS campaigns with personalized incentives.",
                    "Deploy outbound customer success interventions for high-value enterprise accounts.",
                    "Monitor weekly retention improvements to measure cohort recovery rate.",
                ],
                success_metrics=[
                    "Customer Retention Rate",
                    "Repeat Purchase Rate",
                    "Revenue Recovery %",
                ],
                expected_time_to_value=ExpectedTimeToValue.SHORT_TERM,
                default_impact=0.85,
                default_effort=0.50,
                recommendation_type=RecommendationType.CUSTOMER_RETENTION,
                target_metric_name="Customer Retention Rate",
                target_improvement_ratio=0.15,
                measurement_period="90 days",
            ),
            RecommendationTemplate(
                title="Introduce Loyalty Program",
                description="Implement a structured tiered rewards program to incentivize repeat purchases and increase customer lifetime value.",
                actions=[
                    "Design tiered points and rewards structure tailored to top-velocity product categories.",
                    "Integrate automated loyalty point notifications at checkout and in account portal.",
                    "Offer introductory bonus points to incentivize instant enrollment.",
                    "Track repeat transaction frequency and loyalty member spend velocity.",
                ],
                success_metrics=[
                    "Repeat Purchase Rate",
                    "Loyalty Member GMV Share",
                    "Net Customer Retention",
                ],
                expected_time_to_value=ExpectedTimeToValue.SHORT_TERM,
                default_impact=0.65,
                default_effort=0.30,
                recommendation_type=RecommendationType.CUSTOMER_RETENTION,
                target_metric_name="Repeat Purchase Rate",
                target_improvement_ratio=0.12,
                measurement_period="60 days",
            ),
            RecommendationTemplate(
                title="Win-back Inactive Customers",
                description="Reactivate lapsed customers through personalized reactivation discounts and targeted exit feedback workflows.",
                actions=[
                    "Segment lapsed accounts inactive between 60 and 180 days.",
                    "Deploy win-back email sequence offering tailored product recommendations and exclusive discounts.",
                    "Conduct automated exit surveys to capture core cancellation drivers.",
                    "Measure reactivation conversion rate and 90-day post-reactivation retention.",
                ],
                success_metrics=[
                    "Win-back Conversion Rate",
                    "Reactivated Customer LTV",
                    "Revenue Recovery %",
                ],
                expected_time_to_value=ExpectedTimeToValue.SHORT_TERM,
                default_impact=0.80,
                default_effort=0.50,
                recommendation_type=RecommendationType.CUSTOMER_RETENTION,
                target_metric_name="Win-back Conversion Rate",
                target_improvement_ratio=0.10,
                measurement_period="45 days",
            ),
        ]
        self.register(
            RecommendationRule(
                finding_subtype=FindingSubtype.DECLINE,
                root_cause_subtype=FindingSubtype.CHURN_INCREASE,
                recommendation_type=RecommendationType.CUSTOMER_RETENTION,
                priority_weight=0.90,
                impact_weight=0.85,
                effort_weight=0.50,
                templates=churn_to_rev_templates,
                description="Customer churn spike directly drains recurring top-line revenue.",
            )
        )

        # 2. Margin Compression <- Cost Spike
        cost_to_margin_templates = [
            RecommendationTemplate(
                title="Supplier & Procurement Renegotiation",
                description="Renegotiate wholesale and logistics vendor contracts to lower unit procurement costs.",
                actions=[
                    "Benchmark unit purchase costs against prevailing market and volume tiers.",
                    "Initiate structured renegotiations with top 20% spending vendors.",
                    "Consolidate purchasing volumes across product categories for tier discounts.",
                    "Monitor gross margin recovery per product category.",
                ],
                success_metrics=[
                    "Gross Margin %",
                    "COGS Reduction %",
                    "Vendor Unit Cost Variance",
                ],
                expected_time_to_value=ExpectedTimeToValue.SHORT_TERM,
                default_impact=0.85,
                default_effort=0.50,
                recommendation_type=RecommendationType.COST_OPTIMIZATION,
                target_metric_name="Gross Margin %",
                target_improvement_ratio=0.08,
                measurement_period="60 days",
            ),
            RecommendationTemplate(
                title="Cost Reduction & Expense Rationalization",
                description="Audit operating expenditures and streamline non-essential operational overhead.",
                actions=[
                    "Conduct line-item audit of operational and fulfillment cost centers.",
                    "Eliminate redundant third-party tooling and optimize SaaS/service tiers.",
                    "Enforce strict approval thresholds on discretionary expenditures.",
                    "Review monthly operating profit margins against revised expense targets.",
                ],
                success_metrics=[
                    "Operating Margin %",
                    "Monthly OPEX Savings",
                    "EBITDA Margin",
                ],
                expected_time_to_value=ExpectedTimeToValue.MEDIUM_TERM,
                default_impact=0.80,
                default_effort=0.70,
                recommendation_type=RecommendationType.COST_OPTIMIZATION,
                target_metric_name="Operating Margin %",
                target_improvement_ratio=0.10,
                measurement_period="90 days",
            ),
            RecommendationTemplate(
                title="Process & Fulfillment Optimization",
                description="Automate order processing and optimize packaging to reduce direct fulfillment overhead.",
                actions=[
                    "Audit warehouse handling steps and transit routing inefficiencies.",
                    "Standardize package dimensional sizing to reduce dimensional freight surcharges.",
                    "Automate high-frequency picking and packing workflows.",
                    "Measure unit fulfillment cost reduction.",
                ],
                success_metrics=[
                    "Fulfillment Cost Per Order",
                    "Order Processing Cycle Time",
                    "Gross Margin %",
                ],
                expected_time_to_value=ExpectedTimeToValue.SHORT_TERM,
                default_impact=0.65,
                default_effort=0.35,
                recommendation_type=RecommendationType.PROCESS_IMPROVEMENT,
                target_metric_name="Fulfillment Cost Per Order",
                target_improvement_ratio=0.12,
                measurement_period="45 days",
            ),
        ]
        self.register(
            RecommendationRule(
                finding_subtype=FindingSubtype.MARGIN_COMPRESSION,
                root_cause_subtype=FindingSubtype.COST_SPIKE,
                recommendation_type=RecommendationType.COST_OPTIMIZATION,
                priority_weight=0.92,
                impact_weight=0.90,
                effort_weight=0.55,
                templates=cost_to_margin_templates,
                description="Cost surges directly compress profit margins across catalog sales.",
            )
        )

        # 3. Product Concentration Risk
        product_concentration_templates = [
            RecommendationTemplate(
                title="Diversify Product Portfolio",
                description="Expand and invest into high-growth secondary product lines to reduce top-line dependency.",
                actions=[
                    "Identify adjacent product categories with strong customer demand.",
                    "Allocate marketing and merchandising budget to secondary SKU groups.",
                    "Introduce new SKU variants in complementary price tiers.",
                    "Track revenue share distribution across product portfolio.",
                ],
                success_metrics=[
                    "Product Concentration Ratio",
                    "Secondary Category GMV Growth",
                    "Revenue Diversification Index",
                ],
                expected_time_to_value=ExpectedTimeToValue.MEDIUM_TERM,
                default_impact=0.85,
                default_effort=0.75,
                recommendation_type=RecommendationType.PRODUCT_OPTIMIZATION,
                target_metric_name="Product Concentration Ratio",
                target_improvement_ratio=0.15,
                measurement_period="120 days",
            ),
            RecommendationTemplate(
                title="Promote Secondary Product Categories",
                description="Implement cross-merchandising and on-site feature banners for under-exposed catalog items.",
                actions=[
                    "Feature high-margin secondary items on homepage and category landing pages.",
                    "Create cross-category bundles pairing hero products with secondary items.",
                    "A/B test promotional discounts on secondary product categories.",
                    "Monitor click-through and attach rate for promoted products.",
                ],
                success_metrics=[
                    "Secondary Category Sales Volume",
                    "Cross-Sell Attach Rate",
                    "Average Order Value",
                ],
                expected_time_to_value=ExpectedTimeToValue.SHORT_TERM,
                default_impact=0.65,
                default_effort=0.35,
                recommendation_type=RecommendationType.PRODUCT_OPTIMIZATION,
                target_metric_name="Cross-Sell Attach Rate",
                target_improvement_ratio=0.20,
                measurement_period="30 days",
            ),
            RecommendationTemplate(
                title="Reduce Concentration Exposure via Bundling",
                description="Bundle leading products with complementary catalog items to distribute volume demand.",
                actions=[
                    "Analyze frequent co-purchase product affinity matrices.",
                    "Launch bundle discounts pairing dominant SKUs with emerging products.",
                    "Optimize checkout recommendations for bundle upsells.",
                    "Evaluate basket size and blended margin expansion.",
                ],
                success_metrics=[
                    "Bundle Attach Rate",
                    "Blended Gross Margin",
                    "Concentration Risk Index",
                ],
                expected_time_to_value=ExpectedTimeToValue.SHORT_TERM,
                default_impact=0.75,
                default_effort=0.45,
                recommendation_type=RecommendationType.PRICING_STRATEGY,
                target_metric_name="Bundle Attach Rate",
                target_improvement_ratio=0.18,
                measurement_period="45 days",
            ),
        ]
        self.register(
            RecommendationRule(
                finding_subtype=FindingSubtype.PRODUCT_CONCENTRATION_RISK,
                root_cause_subtype=None,
                recommendation_type=RecommendationType.PRODUCT_OPTIMIZATION,
                priority_weight=0.80,
                impact_weight=0.80,
                effort_weight=0.50,
                templates=product_concentration_templates,
                description="Excessive revenue reliance on a single product creates vulnerability to market shifts.",
            )
        )

        # 4. Delivery Delay -> Customer Churn
        delivery_to_churn_templates = [
            RecommendationTemplate(
                title="Logistics Carrier Rebalancing & SLA Enforcement",
                description="Rebalance shipping volume to top-performing carrier partners and establish strict SLA penalties.",
                actions=[
                    "Audit on-time delivery rates across regional shipping providers.",
                    "Reallocate 30% of order volume away from underperforming logistics carriers.",
                    "Implement automated carrier performance scorecards and SLA clawbacks.",
                    "Monitor average transit days and delivery satisfaction ratings.",
                ],
                success_metrics=[
                    "Average Delivery Days",
                    "On-Time Delivery Rate",
                    "Delivery-Related Churn %",
                ],
                expected_time_to_value=ExpectedTimeToValue.SHORT_TERM,
                default_impact=0.85,
                default_effort=0.50,
                recommendation_type=RecommendationType.OPERATIONAL_EFFICIENCY,
                target_metric_name="On-Time Delivery Rate",
                target_improvement_ratio=0.15,
                measurement_period="45 days",
            ),
            RecommendationTemplate(
                title="Proactive Delivery Tracking & Delay Notifications",
                description="Deploy automated real-time SMS and email notifications with delivery compensation for transit delays.",
                actions=[
                    "Integrate webhook carrier tracking into customer communication portal.",
                    "Trigger proactive delay apology notifications with discount coupons.",
                    "Provide real-time map tracking links for shipped orders.",
                    "Measure customer support ticket volume regarding shipment inquiries.",
                ],
                success_metrics=[
                    "WISMO Support Ticket Volume",
                    "Customer CSAT / Review Score",
                    "Repeat Purchase Rate",
                ],
                expected_time_to_value=ExpectedTimeToValue.IMMEDIATE,
                default_impact=0.60,
                default_effort=0.25,
                recommendation_type=RecommendationType.CUSTOMER_RETENTION,
                target_metric_name="Customer CSAT / Review Score",
                target_improvement_ratio=0.20,
                measurement_period="30 days",
            ),
        ]
        self.register(
            RecommendationRule(
                finding_subtype=FindingSubtype.CHURN_INCREASE,
                root_cause_subtype=FindingSubtype.DELIVERY_DELAY,
                recommendation_type=RecommendationType.OPERATIONAL_EFFICIENCY,
                priority_weight=0.85,
                impact_weight=0.85,
                effort_weight=0.40,
                templates=delivery_to_churn_templates,
                description="Shipping delays cause customer dissatisfaction, accelerating churn.",
            )
        )

        # 5. Customer Growth Slowdown (General)
        growth_slowdown_templates = [
            RecommendationTemplate(
                title="Acquisition Channel Optimization",
                description="Reallocate paid acquisition budget toward high-converting channels and creative assets.",
                actions=[
                    "Audit Customer Acquisition Cost (CAC) and ROAS across all marketing channels.",
                    "Shift 25% ad spend to top-converting channels and search campaigns.",
                    "Launch new creative testing sprint for high-performing audience segments.",
                    "Monitor weekly new customer acquisition volume and blended CAC.",
                ],
                success_metrics=[
                    "New Customer Acquisitions",
                    "Customer Acquisition Cost (CAC)",
                    "Blended ROAS",
                ],
                expected_time_to_value=ExpectedTimeToValue.SHORT_TERM,
                default_impact=0.75,
                default_effort=0.45,
                recommendation_type=RecommendationType.CUSTOMER_ACQUISITION,
                target_metric_name="New Customer Acquisitions",
                target_improvement_ratio=0.15,
                measurement_period="60 days",
            ),
            RecommendationTemplate(
                title="Customer Referral Program Activation",
                description="Incentivize existing customers with two-sided referral credits to accelerate word-of-mouth acquisition.",
                actions=[
                    "Deploy two-sided referral rewards ($15 for referrer, $15 for referee).",
                    "Prompt satisfied buyers to share referral links post-delivery.",
                    "Feature referral program prominently in customer account dashboard.",
                    "Track organic referral viral coefficient and acquisition velocity.",
                ],
                success_metrics=[
                    "Referral Share Rate",
                    "Referral Acquisition Volume",
                    "Referral CAC",
                ],
                expected_time_to_value=ExpectedTimeToValue.IMMEDIATE,
                default_impact=0.65,
                default_effort=0.30,
                recommendation_type=RecommendationType.CUSTOMER_ACQUISITION,
                target_metric_name="Referral Acquisition Volume",
                target_improvement_ratio=0.25,
                measurement_period="30 days",
            ),
        ]
        self.register(
            RecommendationRule(
                finding_subtype=FindingSubtype.CUSTOMER_GROWTH_SLOWDOWN,
                root_cause_subtype=None,
                recommendation_type=RecommendationType.CUSTOMER_ACQUISITION,
                priority_weight=0.78,
                impact_weight=0.75,
                effort_weight=0.40,
                templates=growth_slowdown_templates,
                description="Deceleration in net new customers requires channel optimization and organic incentives.",
            )
        )

        # 6. Revenue Decline (General / Direct)
        revenue_decline_templates = [
            RecommendationTemplate(
                title="Revenue Recovery & Pipeline Optimization",
                description="Accelerate top-line revenue stabilization through sales pipeline optimization and conversion improvements.",
                actions=[
                    "Audit sales pipeline velocity and conversion drop-offs across funnel stages.",
                    "Implement targeted promotions for high-margin catalog offerings.",
                    "Engage core accounts with proactive account-review and expansion initiatives.",
                    "Track weekly booking and revenue run-rate recovery.",
                ],
                success_metrics=[
                    "Total Revenue",
                    "Pipeline Conversion Rate",
                    "Average Order Value",
                ],
                expected_time_to_value=ExpectedTimeToValue.SHORT_TERM,
                default_impact=0.80,
                default_effort=0.45,
                recommendation_type=RecommendationType.REVENUE_GROWTH,
                target_metric_name="Total Revenue",
                target_improvement_ratio=0.10,
                measurement_period="60 days",
            ),
            RecommendationTemplate(
                title="Pricing & Discounting Strategy Review",
                description="Realign pricing structures and promotional discounting to protect revenue yield.",
                actions=[
                    "Analyze price elasticity and discounting across customer segments.",
                    "Eliminate unprofitable promotional discounts.",
                    "Optimize dynamic pricing rules for high-demand periods.",
                    "Monitor revenue per customer and blended transaction margin.",
                ],
                success_metrics=[
                    "Revenue Per Customer",
                    "Gross Margin %",
                    "Discount Rate",
                ],
                expected_time_to_value=ExpectedTimeToValue.SHORT_TERM,
                default_impact=0.70,
                default_effort=0.35,
                recommendation_type=RecommendationType.PRICING_STRATEGY,
                target_metric_name="Revenue Per Customer",
                target_improvement_ratio=0.08,
                measurement_period="45 days",
            ),
        ]
        self.register(
            RecommendationRule(
                finding_subtype=FindingSubtype.DECLINE,
                root_cause_subtype=None,
                recommendation_type=RecommendationType.REVENUE_GROWTH,
                priority_weight=0.85,
                impact_weight=0.80,
                effort_weight=0.40,
                templates=revenue_decline_templates,
                description="Sustained revenue contraction requires immediate pipeline acceleration and pricing strategy review.",
            )
        )

        # 7. Operational Productivity Improvement (Positive Opportunity)
        productivity_templates = [
            RecommendationTemplate(
                title="Standardize Peak Fulfillment Protocols",
                description="Document and standardize high-efficiency order fulfillment workflows across all operating regions.",
                actions=[
                    "Benchmark operating procedures of top-performing fulfillment hubs.",
                    "Publish standard operating playbooks for picking, packing, and dispatch.",
                    "Train regional operations teams on best-practice fulfillment workflows.",
                    "Track regional fulfillment cycle times and maintain 95%+ completion rate.",
                ],
                success_metrics=[
                    "Order Completion Rate",
                    "Fulfillment Cycle Time",
                    "Customer CSAT",
                ],
                expected_time_to_value=ExpectedTimeToValue.IMMEDIATE,
                default_impact=0.60,
                default_effort=0.25,
                recommendation_type=RecommendationType.OPERATIONAL_EFFICIENCY,
                target_metric_name="Order Completion Rate",
                target_improvement_ratio=0.02,
                measurement_period="30 days",
            ),
        ]
        self.register(
            RecommendationRule(
                finding_subtype=FindingSubtype.PRODUCTIVITY_IMPROVEMENT,
                root_cause_subtype=None,
                recommendation_type=RecommendationType.OPERATIONAL_EFFICIENCY,
                priority_weight=0.60,
                impact_weight=0.60,
                effort_weight=0.25,
                templates=productivity_templates,
                description="High fulfillment productivity provides an opportunity to scale operational best practices across all hubs.",
            )
        )

