"""Deterministic factual scoring engine for Phase 9.3: Executive Insight Generator."""

from typing import Any, List, Optional, Union


def calculate_insight_confidence(
    narrative_confidence: Optional[float] = None,
    root_causes: Optional[List[Any]] = None,
    recommendations: Optional[List[Any]] = None,
    forecasts: Optional[List[Any]] = None,
    scenarios: Optional[List[Any]] = None,
) -> float:
    """
    Deterministically computes factual reliability confidence for Executive Insights (0.10 - 1.00).

    Components:
    1. Narrative Confidence (25%): Baseline factual narrative reliability.
    2. Root Cause Confidence (25%): Mean confidence and causal validity across RCAs.
    3. Recommendation Confidence (20%): Mean statistical confidence across actionable recommendations.
    4. Forecast Confidence (15%): Mean MAPE-derived accuracy across forecast models.
    5. Scenario Reliability (15%): Convergence and validity of simulated business scenarios.

    Returns:
        float: Bounded between 0.10 and 1.00, rounded to 2 decimal places.
    """
    # 1. Narrative Confidence Component
    c_narrative = float(narrative_confidence) if narrative_confidence is not None else 0.85

    # 2. Root Cause Component
    rca_list = root_causes or []
    if rca_list:
        scores = []
        for r in rca_list:
            if hasattr(r, "confidence_score") and r.confidence_score is not None:
                scores.append(float(r.confidence_score))
            elif isinstance(r, dict) and r.get("confidence_score") is not None:
                scores.append(float(r["confidence_score"]))
            else:
                scores.append(0.85)
        c_rca = sum(scores) / len(scores) if scores else 0.85
    else:
        c_rca = 0.80

    # 3. Recommendation Component
    rec_list = recommendations or []
    if rec_list:
        scores = []
        for rec in rec_list:
            if hasattr(rec, "confidence_score") and rec.confidence_score is not None:
                scores.append(float(rec.confidence_score))
            elif isinstance(rec, dict) and rec.get("confidence_score") is not None:
                scores.append(float(rec["confidence_score"]))
            else:
                scores.append(0.85)
        c_rec = sum(scores) / len(scores) if scores else 0.85
    else:
        c_rec = 0.80

    # 4. Forecast Component
    forecast_list = forecasts or []
    if forecast_list:
        scores = []
        for fc in forecast_list:
            if hasattr(fc, "evaluation_metrics") and isinstance(fc.evaluation_metrics, dict):
                mape = fc.evaluation_metrics.get("mape", 15.0)
                scores.append(max(0.5, min(1.0, 1.0 - (float(mape) / 100.0))))
            elif isinstance(fc, dict) and isinstance(fc.get("evaluation_metrics"), dict):
                mape = fc["evaluation_metrics"].get("mape", 15.0)
                scores.append(max(0.5, min(1.0, 1.0 - (float(mape) / 100.0))))
            else:
                scores.append(0.85)
        c_forecast = sum(scores) / len(scores) if scores else 0.85
    else:
        c_forecast = 0.85

    # 5. Scenario Component
    scenario_list = scenarios or []
    if scenario_list:
        scores = []
        for sc in scenario_list:
            if hasattr(sc, "status") and str(sc.status).upper() in ["COMPLETED", "READY"]:
                scores.append(0.90)
            elif isinstance(sc, dict) and str(sc.get("status", "")).upper() in ["COMPLETED", "READY"]:
                scores.append(0.90)
            else:
                scores.append(0.80)
        c_scenario = sum(scores) / len(scores) if scores else 0.85
    else:
        c_scenario = 0.85

    # Composite weighted confidence
    raw_confidence = (
        0.25 * c_narrative
        + 0.25 * c_rca
        + 0.20 * c_rec
        + 0.15 * c_forecast
        + 0.15 * c_scenario
    )

    bounded = max(0.10, min(1.00, raw_confidence))
    return round(bounded, 2)


def calculate_risk_ranking_score(
    severity: Union[str, Any],
    confidence: float = 0.85,
    impact_score: Optional[float] = None,
) -> float:
    """
    Computes deterministic ranking score (0.00 - 1.00) for risk prioritization.
    """
    sev_str = str(severity).upper()
    sev_weights = {
        "CRITICAL": 1.00,
        "HIGH": 0.80,
        "MEDIUM": 0.50,
        "LOW": 0.25,
    }
    sev_val = sev_weights.get(sev_str, 0.50)
    conf_val = max(0.0, min(1.0, float(confidence)))

    if impact_score is not None:
        raw_imp = float(impact_score)
        imp_val = raw_imp / 100.0 if raw_imp > 1.0 else raw_imp
        imp_val = max(0.0, min(1.0, imp_val))
    else:
        imp_val = sev_val

    ranking = 0.45 * sev_val + 0.35 * imp_val + 0.20 * conf_val
    return round(max(0.0, min(1.0, ranking)), 2)


def calculate_opportunity_ranking_score(
    impact: Union[str, float, Any],
    confidence: float = 0.85,
    effort_score: Optional[float] = None,
) -> float:
    """
    Computes deterministic ranking score (0.00 - 1.00) for opportunity prioritization.
    """
    if isinstance(impact, (int, float)):
        imp_val = float(impact)
        imp_val = imp_val / 100.0 if imp_val > 1.0 else imp_val
    else:
        imp_str = str(impact).upper()
        imp_weights = {
            "CRITICAL": 1.00,
            "HIGH": 0.85,
            "MEDIUM": 0.60,
            "LOW": 0.35,
        }
        imp_val = imp_weights.get(imp_str, 0.60)

    conf_val = max(0.0, min(1.0, float(confidence)))

    if effort_score is not None:
        raw_eff = float(effort_score)
        eff_val = raw_eff / 100.0 if raw_eff > 1.0 else raw_eff
        ease_factor = max(0.2, 1.0 - (eff_val * 0.5))
    else:
        ease_factor = 0.80

    ranking = 0.50 * imp_val + 0.30 * conf_val + 0.20 * ease_factor
    return round(max(0.0, min(1.0, ranking)), 2)


def calculate_action_ranking_score(
    priority: Union[str, Any],
    expected_impact: Optional[float] = None,
    difficulty: Optional[str] = None,
) -> float:
    """
    Computes deterministic priority action ranking score (0.00 - 1.00).
    """
    prio_str = str(priority).upper()
    prio_weights = {
        "CRITICAL": 1.00,
        "HIGH": 0.80,
        "MEDIUM": 0.55,
        "LOW": 0.30,
    }
    prio_val = prio_weights.get(prio_str, 0.60)

    if expected_impact is not None:
        raw_imp = float(expected_impact)
        imp_val = raw_imp / 100.0 if raw_imp > 1.0 else raw_imp
    else:
        imp_val = prio_val

    diff_str = str(difficulty or "MODERATE").upper()
    diff_factors = {
        "EASY": 0.95,
        "LOW": 0.95,
        "MODERATE": 0.75,
        "MEDIUM": 0.75,
        "DIFFICULT": 0.50,
        "HIGH": 0.50,
    }
    ease_val = diff_factors.get(diff_str, 0.75)

    ranking = 0.45 * prio_val + 0.35 * imp_val + 0.20 * ease_val
    return round(max(0.0, min(1.0, ranking)), 2)
