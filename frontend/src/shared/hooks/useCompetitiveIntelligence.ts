/**
 * Competitive Intelligence shared React Query hooks.
 *
 * Three separate hooks — one per endpoint — sharing distinct cache keys so that
 * React Query can independently cache and refetch each data slice.
 *
 * All three are consumed by CompetitiveIntelligenceCenterView.
 * staleTime: 60_000ms — competitive benchmarks are org-level aggregates.
 */

import { useQuery } from '@tanstack/react-query';
import { queryKeys } from '../api/queryKeys';
import { competitiveIntelligenceApi } from '../../api';
import { useBackendHealth } from './useBackendHealth';

/**
 * Market position snapshot: market_rank, percentile, SWOT quadrants.
 * Maps to GET /api/v1/os/benchmarks/market-position
 */
export function useMarketPosition() {
  const { status } = useBackendHealth();

  return useQuery({
    queryKey: queryKeys.competitiveIntelligence.marketPosition(),
    queryFn: competitiveIntelligenceApi.getMarketPosition,
    enabled: status === 'connected',
    staleTime: 60_000,
  });
}

/**
 * Metric-by-metric benchmark comparisons (gap to median, top quartile, best-in-class).
 * Maps to GET /api/v1/os/benchmarks/comparisons
 */
export function useBenchmarkComparisons() {
  const { status } = useBackendHealth();

  return useQuery({
    queryKey: queryKeys.competitiveIntelligence.comparisons(),
    queryFn: competitiveIntelligenceApi.getComparisons,
    enabled: status === 'connected',
    staleTime: 60_000,
  });
}

/**
 * ARR opportunity candidates derived from benchmark gaps, with optional auto_scenario_id.
 * Maps to GET /api/v1/os/benchmarks/opportunities
 */
export function useBenchmarkOpportunities() {
  const { status } = useBackendHealth();

  return useQuery({
    queryKey: queryKeys.competitiveIntelligence.opportunities(),
    queryFn: competitiveIntelligenceApi.getOpportunities,
    enabled: status === 'connected',
    staleTime: 60_000,
  });
}
