"""Standardized evidence payload builder ensuring consistent JSON structure for diagnostic findings."""

from typing import Any, Dict, Optional


class EvidenceBuilder:
    """
    Constructs uniform diagnostic evidence dictionaries conforming to the DecisionOS common schema:
    {
        "category": "...",
        "subtype": "...",
        "metric_name": "...",
        "observed": ...,
        "threshold": ...,
        "confidence": ...,
        "sample_size": ...,
        "recommendation": "...",
        "context": {}
    }
    """

    @staticmethod
    def build_evidence(
        category: str,
        subtype: str,
        metric_name: str,
        observed: Any,
        threshold: Any,
        confidence: float,
        sample_size: int,
        recommendation: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Creates a standardized evidence dictionary matching the platform-wide contract.
        
        Args:
            category: Top-level diagnostic domain (REVENUE, CUSTOMER, OPERATIONAL, PRODUCT).
            subtype: Specific business anomaly or opportunity classification.
            metric_name: Primary KPI or metric key associated with the finding.
            observed: The measured numerical value or formatted rate.
            threshold: The benchmark trigger boundary compared against.
            confidence: Statistical confidence score [0.0 - 1.0].
            sample_size: Total records, periods, or entity count analyzed.
            recommendation: Actionable remediation or strategic recommendation.
            context: Additional key-value metadata (e.g. historical values, entity names).
            
        Returns:
            Normalized dictionary for storage in DiagnosticFinding.supporting_data.
        """
        return {
            "category": category,
            "subtype": subtype,
            "metric_name": metric_name,
            "observed": observed,
            "threshold": threshold,
            "confidence": confidence,
            "sample_size": sample_size,
            "recommendation": recommendation,
            "context": context if context is not None else {},
        }

    @classmethod
    def build_metric_evidence(
        cls,
        category: str,
        subtype: str,
        metric_name: str,
        observed: Any,
        threshold: Any,
        confidence: float,
        sample_size: int,
        recommendation: str,
        change_percent: Optional[float] = None,
        trend: Optional[str] = None,
        extra_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Helper for standard single-metric aggregate findings."""
        ctx = extra_context.copy() if extra_context else {}
        if change_percent is not None:
            ctx["change_percent"] = change_percent
        if trend is not None:
            ctx["trend"] = trend

        return cls.build_evidence(
            category=category,
            subtype=subtype,
            metric_name=metric_name,
            observed=observed,
            threshold=threshold,
            confidence=confidence,
            sample_size=sample_size,
            recommendation=recommendation,
            context=ctx,
        )

    @classmethod
    def build_time_series_evidence(
        cls,
        category: str,
        subtype: str,
        metric_name: str,
        current_value: float,
        previous_value: float,
        change_percent: float,
        threshold: float,
        confidence: float,
        period_count: int,
        trend: str,
        recommendation: str,
        volatility: Optional[float] = None,
        extra_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Helper for time-series and period-over-period trend findings."""
        ctx = extra_context.copy() if extra_context else {}
        ctx["current_period_value"] = current_value
        ctx["previous_period_value"] = previous_value
        ctx["change_percent"] = change_percent
        ctx["trend"] = trend
        if volatility is not None:
            ctx["volatility_cv"] = volatility

        return cls.build_evidence(
            category=category,
            subtype=subtype,
            metric_name=metric_name,
            observed=change_percent,
            threshold=threshold,
            confidence=confidence,
            sample_size=period_count,
            recommendation=recommendation,
            context=ctx,
        )

    @classmethod
    def build_distribution_evidence(
        cls,
        category: str,
        subtype: str,
        dimension_name: str,
        top_entity: str,
        concentration_ratio: float,
        threshold: float,
        confidence: float,
        total_entities: int,
        recommendation: str,
        extra_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Helper for entity or category concentration/distribution findings."""
        ctx = extra_context.copy() if extra_context else {}
        ctx["top_entity"] = top_entity
        ctx["concentration_ratio"] = concentration_ratio
        ctx["total_entities"] = total_entities

        return cls.build_evidence(
            category=category,
            subtype=subtype,
            metric_name=dimension_name,
            observed=concentration_ratio,
            threshold=threshold,
            confidence=confidence,
            sample_size=total_entities,
            recommendation=recommendation,
            context=ctx,
        )
