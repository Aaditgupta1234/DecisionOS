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
  metric_key?: string;
  confidence_score: number;
  affected_metrics?: string[];
  evidence_data?: Record<string, any>;
  created_at: string;
}

export interface RootCause {
  id: string;
  root_cause_key?: string;
  title: string;
  category: string;
  probability_score?: number;
  confidence_score: number;
  impact_score?: number;
  supporting_evidence?: string | Record<string, any>;
  affected_finding_ids?: string[];
  created_at?: string;
}

export interface CausalGraphNode {
  id: string;
  title: string;
  category: string;
  subtype: string;
  severity: FindingSeverity | string;
  confidence_score: number;
}

export interface CausalGraphEdge {
  source_id: string;
  target_id: string;
  relationship_type: string;
  relationship_strength: string;
  confidence_score: number;
  impact_score: number;
}

export interface CausalGraphData {
  nodes: CausalGraphNode[];
  edges: CausalGraphEdge[];
}

export interface RootCauseAnalysisRecord {
  id: string;
  dataset_id: string;
  primary_finding_id: string;
  root_cause_finding_id: string;
  relationship_type: string;
  relationship_strength: string;
  confidence_score: number;
  impact_score: number;
  explanation: string;
  supporting_evidence?: Record<string, any>;
  created_at: string;
  primary_finding?: DiagnosticFinding;
  root_cause_finding?: DiagnosticFinding;
}

export interface RootCauseSummaryItem {
  finding_id: string;
  title: string;
  category: string;
  subtype: string;
  severity: string;
  relationship_type: string;
  relationship_strength: string;
  confidence_score: number;
  impact_score: number;
  explanation: string;
}

export interface RootCauseSummaryGroup {
  primary_issue: string;
  primary_finding_id: string;
  primary_severity: string;
  root_causes: RootCauseSummaryItem[];
  overall_confidence: number;
  highest_impact: number;
  causal_chains: string[][];
}

export interface DatasetRootCausesResponse {
  dataset_id: string;
  total_root_causes: number;
  analyses: RootCauseAnalysisRecord[];
  summaries: RootCauseSummaryGroup[];
  graph: CausalGraphData;
}

export interface Recommendation {
  id: string;
  recommendation_key?: string;
  title: string;
  action_summary?: string;
  description?: string;
  why_recommended?: string;
  priority: RecommendationPriority;
  expected_impact?: string;
  estimated_effort?: string;
  estimated_effort_score?: number;
  confidence_score?: number;
  time_to_value?: string;
  expected_time_to_value?: string;
  status: RecommendationStatus;
  affected_metric_keys?: string[];
  action_plan?: string[];
  success_metrics?: string[];
  evidence?: Record<string, any>;
  outcomes?: Record<string, any>;
  created_at?: string;
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
  id?: string;
  title: string;
  description: string;
  time_horizon: string;
  owner_role?: string;
  is_completed?: boolean;
}

export interface StrategicMilestone {
  horizon?: string;
  theme?: string;
  title?: string;
  target_metrics?: string[];
  actions?: StrategicAction[];
}

export interface StrategicPriorityItem {
  title: string;
  priority: RecommendationPriority | string;
  source_recommendation_ids?: string[];
  rationale?: string;
}

export interface StrategyActionItem {
  title: string;
  description: string;
  time_horizon: string;
  source_recommendation_id?: string;
  dependencies?: string[];
}

export interface StrategyMilestoneItem {
  title: string;
  time_horizon: string;
  focus_area?: string;
  key_deliverables?: string[];
  success_criteria?: string[];
}

export interface SuccessCriterionItem {
  metric_key: string;
  target_direction: string;
  source?: string;
  rationale?: string;
}

export interface StrategyPlan {
  id: string;
  dataset_id: string;
  plan_version: string;
  status: StrategyPlanStatus | string;
  title?: string;
  objective?: string;
  executive_summary: string;
  strategic_priorities?: StrategicPriorityItem[];
  action_items?: StrategyActionItem[];
  milestones?: StrategyMilestoneItem[];
  strategic_milestones?: StrategicMilestone[];
  success_criteria?: SuccessCriterionItem[];
  model_name?: string;
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

export interface ReportSectionConfig {
  includeExecutiveSummary: boolean;
  includeMetrics: boolean;
  includeDiagnostics: boolean;
  includeRootCauses: boolean;
  includeRecommendations: boolean;
  includeAIInsights: boolean;
  includeStrategyPlan: boolean;
  includeScenarios: boolean;
  includeForecasts: boolean;
}

export interface ExecutiveReportData {
  reportId: string;
  datasetId: string;
  generatedAt: string;
  generatedBy: string;
  reportVersion: string;
  dataset: Dataset;
  health: BusinessHealthResponse;
  executiveSummary: ExecutiveSummaryResponse;
  intelligenceReport: IntelligenceReportResponse;
  rootCausesResponse?: DatasetRootCausesResponse | null;
  aiInsight?: AIInsight | null;
  strategyPlan?: StrategyPlan | null;
  scenarios?: Scenario[];
  forecasts?: Forecast[];
}

export type OrgRole = 'OWNER' | 'ADMIN' | 'ANALYST' | 'VIEWER';

export interface OrganizationMember {
  id: string;
  organization_id: string;
  user_id: string;
  role: OrgRole;
  email?: string;
  full_name?: string;
  created_at: string;
}

export interface Organization {
  id: string;
  name: string;
  slug: string;
  created_by?: string;
  logo_url?: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  current_user_role?: OrgRole;
  member_count?: number;
}

export interface OrganizationDetail extends Organization {
  members: OrganizationMember[];
}
