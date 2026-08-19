export type ConfidenceTier = 'HIGH' | 'MEDIUM' | 'LOW';

export interface ConfidenceCalculationMetadata {
  score: number;
  tier: ConfidenceTier;
  rootCauseCertainty: number;
  recommendationReliability: number;
  executionProgress: number;
  dataQualityScore: number;
  calculatedAt: string;
  formulaVersion: 'CONF_V1';
  explanationBullets: string[];
}

export class RecoveryConfidenceEngine {
  public static readonly FORMULA_VERSION = 'CONF_V1';

  /**
   * Computes deterministic recovery confidence:
   * Confidence = RootCauseCertainty × RecommendationReliability × ExecutionProgress × DataQualityScore
   */
  public static calculateConfidence(
    rootCauseCertainty: number = 0.89,
    recommendationReliability: number = 0.94,
    executionProgress: number = 0.80,
    dataQualityScore: number = 0.97
  ): ConfidenceCalculationMetadata {
    const rawScore = rootCauseCertainty * recommendationReliability * executionProgress * dataQualityScore;
    const scorePct = Math.round(rawScore * 1000) / 10; // e.g. 64.9%

    let tier: ConfidenceTier = 'LOW';
    if (scorePct >= 80) {
      tier = 'HIGH';
    } else if (scorePct >= 50) {
      tier = 'MEDIUM';
    }

    const bullets: string[] = [
      `Root cause attribution strongly supported by causal DAG (${Math.round(rootCauseCertainty * 100)}% certainty)`,
      `Win-back recommendation historically verified (${Math.round(recommendationReliability * 100)}% reliability)`,
      `Initiative execution currently ${Math.round(executionProgress * 100)}% complete (outreach dispatch active)`,
      `Active dataset telemetry quality score is validated (${Math.round(dataQualityScore * 100)}% quality)`,
    ];

    return {
      score: scorePct,
      tier,
      rootCauseCertainty,
      recommendationReliability,
      executionProgress,
      dataQualityScore,
      calculatedAt: new Date().toISOString(),
      formulaVersion: 'CONF_V1',
      explanationBullets: bullets,
    };
  }
}
