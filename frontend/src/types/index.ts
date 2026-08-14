/**
 * DecisionOS TypeScript Interface Definitions
 * Derived directly from Backend Pydantic Schemas (Phases 1 - 6.4)
 */

export type BusinessHealthStatus = 'EXCELLENT' | 'HEALTHY' | 'WATCH_LIST' | 'AT_RISK' | 'CRITICAL';
export type FindingSeverity = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | 'INFO';
export type FindingType = 'ANOMALY' | 'BOTTLENECK' | 'TREND_CHANGE' | 'VARIANCE' | 'INVENTORY_RISK' | 'CUSTOMER_ATTRITION' | 'MARGIN_EROSION';
export type RecommendationPriority = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
export type RecommendationStatus = 'PROPOSED' | 'PLANNED' | 'IN_PROGRESS' | 'COMPLETED' | 'DISMISSED';
export type ForecastHorizon = '30_DAYS' | '90_DAYS' | '180_DAYS' | '365_DAYS';
export type ForecastFrequency = 'DAILY' | 'WEEKLY' | 'MONTHLY';
export type ForecastTrend = 'INCREASING' | 'DECREASING' | 'STABLE' | 'VOLATILE' | 'INSUFFICIENT_DATA';
export type ScenarioAdjustmentType = 'RELATIVE_PERCENT' | 'PERCENTAGE_POINTS' | 'ABSOLUTE_VALUE';
export type StrategyPlanStatus = 'ACTIVE' | 'ARCHIVED' | 'SUPERSEDED';

export interface Dataset {
  id: string;
  name: string;
  original_filename: string;
  status: string;
  file_size: number;
  row_count?: number;
  created_at: string;
  updated_at: string;
  columns?: DatasetColumn[];
}

export interface DatasetColumn {
  id: string;
  original_name: string;
  normalized_name: string;
  mapped_field?: string;
  data_type: string;
}

export interface BusinessHealthResponse {
  dataset_id: string;
  score: number;
  status: BusinessHealthStatus;
  description: string;
}

export interface ExecutiveSummaryResponse {
  dataset_id: string;
  generated_at: string;
  primary_issue: string;
  severity: string;
  top_root_cause?: string;
  top_recommendation?: string;
  key_risks: string[];
  overall_confidence: number;
  confidence_breakdown: Record<string, number>;
  business_health_score: number;
  business_health_status: BusinessHealthStatus;
  expected_business_impact: string;
}

export interface DatasetMetric {
  id: string;
  metric_key: string;
  metric_name: string;
  metric_category: string;
  metric_value: number;
  unit?: string;
  trend_direction?: string;
  period_start?: string;
  period_end?: string;
  calculated_at: string;
}

export interface DiagnosticFinding {
  id: string;
  finding_type: FindingType;
  severity: FindingSeverity;
  title: string;
  description: string;
  business_impact: string;
  confidence_score: number;
  affected_metrics?: string[];
  evidence_data?: Record<string, any>;
  created_at: string;
}

export interface RootCause {
  id: string;
  root_cause_key: string;
  title: string;
  category: string;
  probability_score: number;
  confidence_score: number;
  supporting_evidence?: string;
  affected_finding_ids?: string[];
  created_at: string;
}

export interface Recommendation {
  id: string;
  recommendation_key: string;
  title: string;
  action_summary: string;
  priority: RecommendationPriority;
  expected_impact: string;
  estimated_effort: string;
  time_to_value: string;
  status: RecommendationStatus;
  affected_metric_keys?: string[];
  created_at: string;
}

export interface IntelligenceReportResponse {
  report_version: string;
  dataset_id: string;
  dataset_name: string;
  generated_at: string;
  dataset_last_updated_at?: string;
  artifact_counts: Record<string, number>;
  metrics: DatasetMetric[];
  findings: DiagnosticFinding[];
  root_causes: RootCause[];
  recommendations: Recommendation[];
  executive_summary: ExecutiveSummaryResponse;
}

export interface AIInsight {
  id: string;
  dataset_id: string;
  executive_narrative: string;
  key_takeaways: string[];
  business_assessment: string;
  risk_analysis: string[];
  strategic_priorities: string[];
  action_plan_90_day: string[];
  model_name: string;
  insight_version: string;
  created_at: string;
}

export interface StrategicAction {
  id: string;
  title: string;
  description: string;
  time_horizon: string;
  owner_role?: string;
  is_completed: boolean;
}

export interface StrategicMilestone {
  horizon: string;
  theme: string;
  target_metrics: string[];
  actions: StrategicAction[];
}

export interface StrategyPlan {
  id: string;
  dataset_id: string;
  plan_version: string;
  status: StrategyPlanStatus;
  executive_summary: string;
  strategic_milestones: StrategicMilestone[];
  model_name: string;
  created_at: string;
}

export interface ScenarioAssumption {
  metric_key: string;
  adjustment_type: ScenarioAdjustmentType;
  adjustment_value: number;
}

export interface Scenario {
  id: string;
  dataset_id: string;
  scenario_version: string;
  name: string;
  description?: string;
  status: string;
  assumptions: ScenarioAssumption[];
  baseline_snapshot: Record<string, any>;
  projected_metrics: Record<string, any>;
  projected_health_score: number;
  projected_health_status: BusinessHealthStatus;
  created_at: string;
}

export interface ScenarioComparisonResponse {
  dataset_id: string;
  baseline: Record<string, any>;
  scenarios: Array<{
    scenario_id: string;
    name: string;
    projected_health_score: number;
    projected_health_status: BusinessHealthStatus;
    metric_deltas: Record<string, { baseline: number; projected: number; delta_pct: number }>;
  }>;
}

export interface ForecastPoint {
  period: string;
  predicted_value: number;
  lower_bound?: number;
  upper_bound?: number;
}

export interface ModelMetrics {
  mae: number;
  rmse: number;
  mape?: number;
}

export interface Forecast {
  id: string;
  dataset_id: string;
  forecast_version: string;
  metric_key: string;
  horizon: ForecastHorizon;
  frequency: ForecastFrequency;
  model_name: string;
  model_version: string;
  confidence_level: number;
  status: string;
  historical_observation_count: number;
  forecast_points: ForecastPoint[];
  model_metrics: ModelMetrics;
  trend: ForecastTrend;
  limitations: string[];
  baseline_snapshot: Record<string, any>;
  created_at: string;
}

export interface ChatSession {
  id: string;
  dataset_id: string;
  title: string;
  created_at: string;
}

export interface ChatMessage {
  id: string;
  session_id: string;
  role: 'USER' | 'ASSISTANT' | 'SYSTEM';
  content: string;
  created_at: string;
  citations?: Array<{ type: string; title: string; ref_id?: string }>;
}
