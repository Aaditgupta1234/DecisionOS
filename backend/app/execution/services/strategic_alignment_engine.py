"""Strategic Alignment Engine for Phase 12.7."""

import math
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.execution.constants import (
    STRATEGIC_ALIGNMENT_ENGINE_VERSION,
    STRATEGIC_SNAPSHOT_METRIC_VERSION,
)


class StrategicAlignmentEngine:
    """
    Deterministic calculation engine for strategic, execution, governance,
    and outcome alignment scores. Strictly descriptive and non-causal.
    """

    ENGINE_VERSION = STRATEGIC_ALIGNMENT_ENGINE_VERSION
    SNAPSHOT_METRIC_VERSION = STRATEGIC_SNAPSHOT_METRIC_VERSION

    @classmethod
    def calculate_alignment(
        cls,
        governance_score: float = 100.0,
        compliance_score: float = 100.0,
        velocity_score: float = 100.0,
        schedule_score: float = 100.0,
        budget_score: float = 100.0,
        outcome_score: float = 100.0,
        benefit_score: float = 100.0,
    ) -> Dict[str, Any]:
        """
        Calculates descriptive multi-dimensional alignment scores.
        """
        now = datetime.now(timezone.utc)
        warnings: List[str] = []

        # 1. Governance Alignment Score (0-100)
        gov_align = 0.50 * governance_score + 0.50 * compliance_score
        governance_alignment = round(max(0.0, min(100.0, gov_align)), 2)

        # 2. Execution Alignment Score (0-100)
        exec_align = 0.40 * schedule_score + 0.35 * velocity_score + 0.25 * budget_score
        execution_alignment = round(max(0.0, min(100.0, exec_align)), 2)

        # 3. Outcome Alignment Score (0-100)
        out_align = 0.55 * outcome_score + 0.45 * benefit_score
        outcome_alignment = round(max(0.0, min(100.0, out_align)), 2)

        # 4. Composite Strategic Alignment Score (0-100)
        composite = 0.35 * governance_alignment + 0.35 * execution_alignment + 0.30 * outcome_alignment
        strategic_alignment = round(max(0.0, min(100.0, composite)), 2)

        # 5. Alignment Spread / Variance
        dims = [governance_alignment, execution_alignment, outcome_alignment]
        mean_dim = sum(dims) / 3.0
        variance = sum((d - mean_dim) ** 2 for d in dims) / 3.0
        std_dev = math.sqrt(variance)
        alignment_variance = round(std_dev, 2)

        if alignment_variance > 25.0:
            warnings.append(f"High divergence across strategic dimensions (std dev = {alignment_variance:.1f}). Governance, execution, or outcome delivery is uneven.")

        return {
            "governance_alignment_score": governance_alignment,
            "execution_alignment_score": execution_alignment,
            "outcome_alignment_score": outcome_alignment,
            "strategic_alignment_score": strategic_alignment,
            "alignment_variance": alignment_variance,
            "data_quality_warnings": warnings,
            "calculated_at": now,
        }
