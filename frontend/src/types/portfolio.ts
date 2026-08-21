/**
 * Portfolio Intelligence Suite – Typed response interfaces.
 *
 * Derived from verified OpenAPI schema at /api/v1/openapi.json:
 *   GET /api/v1/portfolio/summary          → PortfolioSummaryResponse
 *   GET /api/v1/portfolio/executive/risk   → PortfolioRiskSummary
 */

// ---------------------------------------------------------------------------
// Enum-style string unions (mirrors backend Python enums)
// ---------------------------------------------------------------------------

export type PortfolioStatus = 'HEALTHY' | 'AT_RISK' | 'CRITICAL' | 'INSUFFICIENT_DATA';
export type TrendDirection = 'UP' | 'DOWN' | 'STABLE';
export type RiskLevel = 'LOW' | 'MODERATE' | 'HIGH' | 'CRITICAL';

// ---------------------------------------------------------------------------
// WorkspacePortfolioEntry — the core "portfolio row" returned by the backend
// ---------------------------------------------------------------------------

export interface WorkspacePortfolioEntry {
  workspace_id: string;
  workspace_name: string;
  health_score: number;
  rank: number;
  total_ranked: number;
  percentile: number;
  percentile_rank: number;
  benchmark_tier: string;
  benchmark_available: boolean;
  trend_direction: TrendDirection;
  finding_count: number;
  critical_finding_count: number;
  recommendation_count: number;
  last_snapshot_at?: string | null;
  snapshot_age_seconds?: number | null;
}

// ---------------------------------------------------------------------------
// Portfolio Summary (Capital Allocation + Portfolio Rollup)
// GET /api/v1/portfolio/summary
// ---------------------------------------------------------------------------

export interface PortfolioSummaryResponse {
  organization_id: string;
  portfolio_status: PortfolioStatus;
  workspace_count: number;
  analyzed_workspace_count: number;
  portfolio_health_score?: number | null;
  average_health_score?: number | null;
  median_health_score?: number | null;
  benchmark_available: boolean;
  best_workspace?: WorkspacePortfolioEntry | null;
  worst_workspace?: WorkspacePortfolioEntry | null;
  workspaces: WorkspacePortfolioEntry[];
  message?: string | null;
  portfolio_version?: string;
  generated_at: string;
}

// ---------------------------------------------------------------------------
// Portfolio Risk Summary (Risk Concentration Radar)
// GET /api/v1/portfolio/executive/risk
// ---------------------------------------------------------------------------

export interface PortfolioRiskSummary {
  total_at_risk_workspaces: number;
  total_critical_workspaces: number;
  risk_concentration_percent: number;
  risk_level: RiskLevel;
  portfolio_size: number;
  ranked_workspace_count: number;
  generated_at: string;
}
