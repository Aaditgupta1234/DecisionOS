/**
 * TypeScript definitions for Phase 9.6 Executive Dashboard & Intelligence Workspace.
 */

export type SnapshotStatus = 'PENDING' | 'BUILDING' | 'READY' | 'FAILED';
export type SnapshotTrigger = 'MANUAL' | 'AUTOMATIC' | 'DATASET_UPDATED' | 'REPORT_GENERATED' | 'INSIGHTS_UPDATED' | 'FORECAST_UPDATED';

export interface HealthDimensions {
  overall_score: number;
  financial_score: number;
  operational_score: number;
  customer_score: number;
  growth_score: number;
  status: string;
  status_color: string;
  previous_score?: number;
  delta: number;
  trend: 'UP' | 'DOWN' | 'STABLE';
}

export interface ExecutiveScorecard {
  business_health_score: number;
  revenue_health_score: number;
  operational_health_score: number;
  customer_health_score: number;
  forecast_confidence: number;
  risk_exposure_score: number;
  health_status: string;
}

export interface WorkspaceStatistics {
  findings_count: number;
  root_causes_count: number;
  recommendations_count: number;
  forecasts_count: number;
  scenarios_count: number;
  reports_count: number;
  metrics_count: number;
}

export interface TopRiskItem {
  id?: string;
  title: string;
  severity: string;
  category: string;
  impact: string;
  confidence: number;
}

export interface TopOpportunityItem {
  id?: string;
  title: string;
  impact_type: string;
  potential_value: string;
  effort: string;
  lever: string;
}

export interface AlertItem {
  id: string;
  severity: string;
  title: string;
  description: string;
  source_type: string;
  created_at: string;
  status: string;
  target_section?: string;
}

export interface WatchlistMetricItem {
  metric_key: string;
  metric_name: string;
  current_value: string;
  trend: 'UP' | 'DOWN' | 'STABLE';
  trend_percentage: number;
  status: string;
  priority: string;
}

export interface OverviewPayload {
  health_dimensions: HealthDimensions;
  scorecard: ExecutiveScorecard;
  statistics: WorkspaceStatistics;
  top_risks: TopRiskItem[];
  top_opportunities: TopOpportunityItem[];
  active_alerts: AlertItem[];
  watchlist_metrics: WatchlistMetricItem[];
  executive_summary_brief: string;
}

export interface KPIMetricItem {
  metric_id?: string;
  metric_name: string;
  metric_key: string;
  category: string;
  current_value: number;
  formatted_value: string;
  unit: string;
  target_value?: number;
  historical_trend: Array<Record<string, any>>;
  trend: 'UP' | 'DOWN' | 'STABLE';
  trend_percentage: number;
  confidence_score: number;
  status: string;
}

export interface FindingItem {
  finding_id: string;
  title: string;
  finding_type: string;
  severity: string;
  category: string;
  description: string;
  business_impact?: string;
  impact_score: number;
  confidence_score: number;
  primary_metric_key?: string;
  evidence_points: string[];
}

export interface CausalStep {
  step_order: number;
  title: string;
  description: string;
  node_type: 'ANOMALY' | 'SYMPTOM' | 'ROOT_CAUSE' | 'ACTION';
}

export interface RootCauseItem {
  root_cause_id: string;
  title: string;
  primary_symptom: string;
  causal_explanation: string;
  impact_score: number;
  attribution_percentage: number;
  confidence_score: number;
  relationship_strength: string;
  causal_chain: CausalStep[];
  linked_finding_ids: string[];
  linked_recommendation_ids: string[];
}

export interface RecommendationMatrixItem {
  recommendation_id: string;
  title: string;
  action_type: string;
  priority: string;
  quadrant: 'QUICK_WIN' | 'MAJOR_PROJECT' | 'FILL_IN' | 'DEPRIORITIZED';
  impact_score: number;
  effort_score: number;
  estimated_time_to_value: string;
  expected_benefit: string;
  action_plan: string[];
  status: string;
  source: string;
  linked_root_cause_id?: string;
}

export interface ForecastHorizonPoint {
  horizon_label: string;
  expected_value: number;
  upper_bound: number;
  lower_bound: number;
  confidence_interval: number;
}

export interface ForecastItem {
  forecast_id: string;
  target_metric: string;
  target_metric_name: string;
  horizon: string;
  model_used: string;
  model_name?: string;
  model_version?: string;
  forecast_horizon?: number;
  generated_at?: string;
  mape_score: number;
  accuracy_percentage: number;
  trend: string;
  historical_actuals: Array<Record<string, any>>;
  projections: ForecastHorizonPoint[];
  narrative_summary?: string;
}

export interface ScenarioImpactMetric {
  metric_name: string;
  metric_key: string;
  baseline_value: number;
  simulated_value: number;
  delta_value: number;
  delta_percentage: number;
  unit: string;
}

export interface ScenarioItem {
  scenario_id: string;
  name: string;
  description: string;
  scenario_type: string;
  status: string;
  impact_summary: string;
  confidence_score: number;
  impacted_metrics: ScenarioImpactMetric[];
  sensitivity_adjustments: Array<Record<string, any>>;
}

export interface NarrativeReportItem {
  report_id: string;
  title: string;
  narrative_type: string;
  audience_level: string;
  content_html: string;
  generated_at: string;
}

export interface StrategicThemeItem {
  theme_title: string;
  impact_level: string;
  summary: string;
  confidence_score: number;
}

export interface StrategicInsightsPayload {
  executive_summary_html: string;
  strategic_themes: StrategicThemeItem[];
  risk_assessment: Array<Record<string, any>>;
  growth_opportunities: Array<Record<string, any>>;
  board_commentary: string;
}

export interface ReportsSummaryItem {
  total_count: number;
  latest_report_id?: string;
  latest_report_title?: string;
  latest_report_type?: string;
  latest_export_format?: string;
  latest_generated_at?: string;
  reports: Array<{
    report_id: string;
    title: string;
    report_type: string;
    export_format: string;
    status: string;
    file_size_bytes: number;
    generated_at: string;
  }>;
}

export interface CategorizedSuggestedQuestion {
  category: 'FORECAST' | 'ROOT_CAUSE' | 'RECOMMENDATION' | 'HEALTH_SCORE' | 'GENERAL';
  question: string;
}

export interface ChatSummaryPayload {
  session_count: number;
  last_message_at?: string;
  suggested_questions: Array<CategorizedSuggestedQuestion | string>;
}

export interface DashboardWorkspacePayload {
  overview: OverviewPayload;
  kpis: KPIMetricItem[];
  findings: FindingItem[];
  root_causes: RootCauseItem[];
  recommendations: RecommendationMatrixItem[];
  forecasts: ForecastItem[];
  scenarios: ScenarioItem[];
  narratives: NarrativeReportItem[];
  insights: StrategicInsightsPayload;
  reports: ReportsSummaryItem;
  chat: ChatSummaryPayload;
}

export interface DashboardHealthIndicator {
  status: 'HEALTHY' | 'PARTIAL' | 'DEGRADED';
  warnings_count: number;
  stale: boolean;
}

export interface ForecastEngineMetadata {
  engine: string;
  version: string;
}

export interface WorkspaceMetadata {
  api_version: string;
  workspace_version: string;
  snapshot_version: string;
  question_generation_version: string;
  workspace_generation_id: string;
  snapshot_hash: string;
  build_time_ms: number;
  snapshot_size_bytes: number;
  artifact_count: number;
  status: SnapshotStatus;
  dataset_id: string;
  dataset_name: string;
  generated_at: string;
  age_seconds: number;
  cache_hit: boolean;
  forecast_engine?: ForecastEngineMetadata;
  available_sections: Record<string, boolean>;
  available_exports: string[];
}

export interface WorkspaceResponse {
  workspace: DashboardWorkspacePayload | null;
  dashboard_health: DashboardHealthIndicator;
  warnings: string[];
  metadata: WorkspaceMetadata;
}

export interface DashboardStatusResponse {
  dataset_id: string;
  snapshot_status: SnapshotStatus;
  workspace_generation_id?: string;
  generated_at?: string;
  age_seconds: number;
  dashboard_health: DashboardHealthIndicator;
  warnings: string[];
}

export interface RefreshResponse {
  dataset_id: string;
  snapshot_id?: string;
  status: SnapshotStatus;
  trigger: SnapshotTrigger;
  message: string;
  retry_after_seconds?: number;
}

export interface TelemetryEvent {
  section: string;
  viewed_at?: string;
  event_metadata?: Record<string, any>;
}
