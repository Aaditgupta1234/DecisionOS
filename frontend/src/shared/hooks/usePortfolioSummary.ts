/**
 * usePortfolioSummary — Shared React Query hook for portfolio summary data.
 *
 * All three portfolio views (Capital Allocation, Risk Radar, Portfolio Rollup)
 * consume GET /api/v1/portfolio/summary. By centralizing the hook, React Query
 * serves all three from the same cached result — preventing duplicate network
 * requests when navigating between portfolio screens.
 *
 * staleTime: 60_000ms — portfolio summaries are org-level aggregates that change
 * slowly; a 1-minute cache window is appropriate.
 */

import { useQuery } from '@tanstack/react-query';
import { queryKeys } from '../api/queryKeys';
import { portfolioApi } from '../../api';
import { useBackendHealth } from './useBackendHealth';

export function usePortfolioSummary() {
  const { status } = useBackendHealth();

  return useQuery({
    queryKey: queryKeys.portfolio.summary(),
    queryFn: portfolioApi.getSummary,
    enabled: status === 'connected',
    staleTime: 60_000,
  });
}

export function usePortfolioRisk() {
  const { status } = useBackendHealth();

  return useQuery({
    queryKey: queryKeys.portfolio.riskSummary(),
    queryFn: portfolioApi.getExecutiveRisk,
    enabled: status === 'connected',
    staleTime: 60_000,
  });
}
