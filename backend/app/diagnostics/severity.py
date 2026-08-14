"""Centralized calculation utilities for diagnostic finding severity tiers and statistical confidence scores."""

import math
from app.core.constants import FindingSeverity


def calculate_severity(
    observed_deviation: float,
    base_threshold: float,
    high_multiplier: float = 2.0,
    critical_multiplier: float = 3.0,
    is_positive_opportunity: bool = False,
) -> FindingSeverity:
    """
    Computes a standardized FindingSeverity tier based on the magnitude of deviation from a baseline threshold.
    
    Args:
        observed_deviation: The measured percentage or absolute deviation (e.g. 0.35 for a 35% decline).
        base_threshold: The minimum threshold triggering the finding (e.g. 0.15 for 15%).
        high_multiplier: Multiplier on base_threshold for escalating to HIGH severity (default: 2.0x).
        critical_multiplier: Multiplier on base_threshold for escalating to CRITICAL severity (default: 3.0x).
        is_positive_opportunity: True if the finding is a positive business gain (e.g., Growth Acceleration).
        
    Returns:
        FindingSeverity enum value (LOW, MEDIUM, HIGH, or CRITICAL).
    """
    # Positive business growth and opportunity indicators are classified as LOW severity
    if is_positive_opportunity:
        return FindingSeverity.LOW

    abs_deviation = abs(observed_deviation)
    abs_base = abs(base_threshold)

    # If deviation is below the base threshold, assign LOW severity
    if abs_base <= 0 or abs_deviation < abs_base:
        return FindingSeverity.LOW

    # Critical tier: deviation exceeds critical multiplier (e.g. >= 3x base threshold)
    if abs_deviation >= critical_multiplier * abs_base:
        return FindingSeverity.CRITICAL

    # High tier: deviation exceeds high multiplier (e.g. >= 2x base threshold)
    if abs_deviation >= high_multiplier * abs_base:
        return FindingSeverity.HIGH

    # Medium tier: deviation meets or exceeds base threshold
    return FindingSeverity.MEDIUM


def calculate_confidence(
    sample_size: int,
    variance: float | None = None,
    min_samples: int = 5,
    target_samples: int = 50,
) -> float:
    """
    Calculates a standardized statistical confidence score bounded between [0.50, 1.00].
    
    Args:
        sample_size: Number of records, periods, or entities evaluated.
        variance: Optional variance or coefficient of variation in the observed data.
        min_samples: Minimum count below which base baseline confidence (0.50) is used.
        target_samples: Sample count at which full statistical power (1.00 base) is achieved.
        
    Returns:
        Confidence score float rounded to 2 decimal places in range [0.50, 1.00].
    """
    if sample_size <= 0:
        return 0.50

    if sample_size <= min_samples:
        score = 0.50 + (sample_size / min_samples) * 0.15
    else:
        # Scale between 0.65 and 1.00 based on progress towards target_samples
        progress = min(1.0, (sample_size - min_samples) / max(1, (target_samples - min_samples)))
        score = 0.65 + progress * 0.35

    # Variance penalty: if variance or CV is exceptionally high, apply minor dampening
    if variance is not None and not math.isnan(variance) and variance > 1.0:
        penalty = min(0.15, (variance - 1.0) * 0.05)
        score = max(0.50, score - penalty)

    # Ensure bounds [0.50, 1.00]
    score = max(0.50, min(1.00, score))
    return round(score, 2)
