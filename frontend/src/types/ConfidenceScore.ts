/**
 * Global 4-Tier Confidence Framework
 * Standardized across all intelligence, root cause, and forecasting engines.
 */
export type ConfidenceTier = 'LOW' | 'MEDIUM' | 'HIGH' | 'VERY_HIGH';

export interface ConfidenceScore {
  value: number; // 0 to 100
  tier: ConfidenceTier;
  label: string;
  color: string;
}

export const getConfidenceScore = (value: number): ConfidenceScore => {
  if (value >= 90) {
    return { value, tier: 'VERY_HIGH', label: 'Very High Confidence', color: '#10B981' };
  } else if (value >= 70) {
    return { value, tier: 'HIGH', label: 'High Confidence', color: '#38BDF8' };
  } else if (value >= 40) {
    return { value, tier: 'MEDIUM', label: 'Medium Confidence', color: '#F59E0B' };
  } else {
    return { value, tier: 'LOW', label: 'Low Confidence', color: '#EF4444' };
  }
};
