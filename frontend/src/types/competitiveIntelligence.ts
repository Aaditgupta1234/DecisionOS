/**
 * Competitive Intelligence Suite – Typed response interfaces.
 *
 * Derived from verified OpenAPI schema at /api/v1/openapi.json:
 *   GET /api/v1/os/benchmarks/market-position  → CompetitiveSnapshotResponse
 *   GET /api/v1/os/benchmarks/comparisons      → CompetitiveBenchmarkResponse[]
 *   GET /api/v1/os/benchmarks/opportunities    → BenchmarkOpportunityResponse[]
 */

// ---------------------------------------------------------------------------
// Market Position Snapshot (Hero metrics + live SWOT quadrants)
// ---------------------------------------------------------------------------

export interface CompetitiveSnapshotResponse {
  id: string;
  portfolio_id: string;
  market_rank: number;
  total_tracked_competitors: number;
  percentile: number;
  swot_strengths: string[];
  swot_weaknesses: string[];
  swot_opportunities: string[];
  swot_threats: string[];
  snapshot_date: string;
}

// ---------------------------------------------------------------------------
// Benchmark Metric Comparisons (scorecard table rows)
// ---------------------------------------------------------------------------

export interface CompetitiveBenchmarkResponse {
  id: string;
  source_id: string;
  metric_name: string;
  our_value: number;
  industry_median: number;
  top_quartile: number;
  best_in_class: number;
  gap_to_median: number;
  gap_to_top_quartile: number;
  performance_tier: string;
}

// ---------------------------------------------------------------------------
// Benchmark Opportunities (drives "Generate Scenario" + ARR gain cards)
// ---------------------------------------------------------------------------

export interface BenchmarkOpportunityResponse {
  id: string;
  benchmark_id: string;
  opportunity_title: string;
  target_metric: string;
  potential_arr_gain: number;
  difficulty_tier: string;
  auto_scenario_id?: string | null;
  status: string;
  created_at: string;
}
