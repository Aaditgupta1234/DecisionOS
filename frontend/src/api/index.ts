/**
 * Centralized API service functions mapping all DecisionOS Backend endpoints.
 */

import { apiClient } from './client';
import {
  AIInsight,
  BusinessHealthResponse,
  ChatMessage,
  ChatSession,
  Dataset,
  DatasetMetric,
  DatasetRootCausesResponse,
  ExecutiveSummaryResponse,
  Forecast,
  ForecastHorizon,
  IntelligenceReportResponse,
  Recommendation,
  RootCause,
  Scenario,
  ScenarioAssumption,
  ScenarioComparisonResponse,
  StrategyPlan,
} from '../types';
import {
  GovernanceScorecardResponse,
  AIGovernanceReportResponse,
  AIProvidersResponse,
  SecurityPostureResponse,
} from '../types/governance';
import {
  PortfolioSummaryResponse,
  PortfolioRiskSummary,
} from '../types/portfolio';
import {
  CompetitiveSnapshotResponse,
  CompetitiveBenchmarkResponse,
  BenchmarkOpportunityResponse,
} from '../types/competitiveIntelligence';

export const DecisionApi = {
  // ------------------------------------------------------------------------
  // Organizations & SaaS Tenancy
  // ------------------------------------------------------------------------
  listOrganizations: () => apiClient<any[]>('/organizations'),

  getCurrentOrganization: () => apiClient<any>('/organizations/current'),

  getOrganization: (orgId: string) => apiClient<any>(`/organizations/${orgId}`),

  createOrganization: (data: { name: string; slug?: string; logo_url?: string }) =>
    apiClient<any>('/organizations', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  updateOrganization: (orgId: string, data: { name?: string; slug?: string; logo_url?: string; is_active?: boolean }) =>
    apiClient<any>(`/organizations/${orgId}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),

  listOrganizationMembers: (orgId: string) =>
    apiClient<any[]>(`/organizations/${orgId}/members`),

  addOrganizationMember: (orgId: string, data: { email: string; role: string }) =>
    apiClient<any>(`/organizations/${orgId}/members`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  updateMemberRole: (orgId: string, memberId: string, role: string) =>
    apiClient<any>(`/organizations/${orgId}/members/${memberId}`, {
      method: 'PATCH',
      body: JSON.stringify({ role }),
    }),

  removeOrganizationMember: (orgId: string, memberId: string) =>
    apiClient<any>(`/organizations/${orgId}/members/${memberId}`, {
      method: 'DELETE',
    }),

  // ------------------------------------------------------------------------
  // Datasets
  // ------------------------------------------------------------------------
  listDatasets: (organizationId?: string) =>
    apiClient<Dataset[]>(`/datasets${organizationId ? `?organization_id=${organizationId}` : ''}`),
  
  getDataset: (datasetId: string) => apiClient<Dataset>(`/datasets/${datasetId}`),

  uploadDataset: (file: File, organizationId?: string) => {
    const formData = new FormData();
    formData.append('file', file);
    return apiClient<Dataset>(`/datasets/upload${organizationId ? `?organization_id=${organizationId}` : ''}`, {
      method: 'POST',
      body: formData,
    });
  },

  deleteDataset: (datasetId: string) =>
    apiClient<{ dataset_id: string; deleted: boolean }>(`/datasets/${datasetId}`, {
      method: 'DELETE',
    }),

  // ------------------------------------------------------------------------
  // Intelligence & Executive Briefings
  // ------------------------------------------------------------------------
  getHealthScore: (datasetId: string) =>
    apiClient<BusinessHealthResponse>(`/datasets/${datasetId}/health-score`),

  getExecutiveSummary: (datasetId: string) =>
    apiClient<ExecutiveSummaryResponse>(`/datasets/${datasetId}/executive-summary`),

  getIntelligenceReport: (datasetId: string) =>
    apiClient<IntelligenceReportResponse>(`/datasets/${datasetId}/intelligence-report`),

  generateIntelligence: (datasetId: string) =>
    apiClient<IntelligenceReportResponse>(`/datasets/${datasetId}/intelligence/generate`, {
      method: 'POST',
    }),

  // ------------------------------------------------------------------------
  // KPI Metrics & Diagnostics
  // ------------------------------------------------------------------------
  listMetrics: (datasetId: string) =>
    apiClient<DatasetMetric[]>(`/datasets/${datasetId}/metrics`),

  listDiagnostics: (datasetId: string) =>
    apiClient<any[]>(`/datasets/${datasetId}/diagnostics`),

  // ------------------------------------------------------------------------
  // Root Causes & Recommendations
  // ------------------------------------------------------------------------
  getRootCausesResponse: (datasetId: string) =>
    apiClient<DatasetRootCausesResponse>(`/datasets/${datasetId}/root-causes`),

  getKnowledgeGraph: (datasetId: string) =>
    apiClient<DatasetRootCausesResponse>(`/datasets/${datasetId}/root-causes`),

  listRootCauses: (datasetId: string) =>
    apiClient<DatasetRootCausesResponse>(`/datasets/${datasetId}/root-causes`),

  listRecommendations: (datasetId: string) =>
    apiClient<Recommendation[]>(`/datasets/${datasetId}/recommendations`),

  // ------------------------------------------------------------------------
  // AI Insights
  // ------------------------------------------------------------------------
  getLatestInsight: (datasetId: string) =>
    apiClient<AIInsight>(`/datasets/${datasetId}/insights/latest`),

  generateInsight: (datasetId: string) =>
    apiClient<AIInsight>(`/datasets/${datasetId}/insights/generate`, {
      method: 'POST',
    }),

  // ------------------------------------------------------------------------
  // Strategy Planner
  // ------------------------------------------------------------------------
  getLatestStrategy: (datasetId: string) =>
    apiClient<StrategyPlan>(`/datasets/${datasetId}/strategy-plan`),

  generateStrategy: (datasetId: string) =>
    apiClient<StrategyPlan>(`/datasets/${datasetId}/strategy-plan/regenerate`, {
      method: 'POST',
    }),

  updateActionStatus: (planId: string, actionId: string, isCompleted: boolean) =>
    apiClient<any>(`/strategy-plans/${planId}/status`, {
      method: 'PATCH',
      body: JSON.stringify({ is_completed: isCompleted }),
    }),

  // ------------------------------------------------------------------------
  // Scenario Simulation
  // ------------------------------------------------------------------------
  listScenarios: async (datasetId: string): Promise<Scenario[]> => {
    const res = await apiClient<any>(`/datasets/${datasetId}/scenarios`);
    if (Array.isArray(res)) return res as Scenario[];
    if (res && Array.isArray(res.scenarios)) return res.scenarios as Scenario[];
    return [] as Scenario[];
  },

  createScenario: (
    datasetId: string,
    payload: {
      name: string;
      description?: string;
      assumptions: ScenarioAssumption[];
    }
  ) =>
    apiClient<Scenario>(`/datasets/${datasetId}/scenarios`, {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  compareScenarios: (datasetId: string, scenarioIds?: string[]) => {
    let url = `/datasets/${datasetId}/scenarios/compare`;
    if (scenarioIds && scenarioIds.length > 0) {
      const params = scenarioIds.map((id) => `scenario_ids=${encodeURIComponent(id)}`).join('&');
      url += `?${params}`;
    }
    return apiClient<ScenarioComparisonResponse>(url);
  },

  // ------------------------------------------------------------------------
  // Forecasting Engine
  // ------------------------------------------------------------------------
  listForecasts: (datasetId: string, metricKey?: string) => {
    const url = metricKey
      ? `/datasets/${datasetId}/forecasts?metric_key=${encodeURIComponent(metricKey)}`
      : `/datasets/${datasetId}/forecasts`;
    return apiClient<{ total_count: number; forecasts: Forecast[] }>(url);
  },

  createForecast: (
    datasetId: string,
    payload: {
      metric_key: string;
      horizon: ForecastHorizon;
      confidence_level?: number;
      model_name?: string;
    }
  ) =>
    apiClient<Forecast>(`/datasets/${datasetId}/forecasts`, {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  compareForecasts: (datasetId: string, forecastIds?: string[], metricKey?: string) => {
    const params = new URLSearchParams();
    if (forecastIds) {
      forecastIds.forEach((id) => params.append('forecast_ids', id));
    }
    if (metricKey) {
      params.append('metric_key', metricKey);
    }
    const qs = params.toString();
    return apiClient<any>(`/datasets/${datasetId}/forecasts/compare${qs ? `?${qs}` : ''}`);
  },

  // ------------------------------------------------------------------------
  // AI Chat Analyst
  // ------------------------------------------------------------------------
  listChatSessions: (datasetId: string) =>
    apiClient<ChatSession[]>(`/datasets/${datasetId}/chat/sessions`),

  createChatSession: (datasetId: string, title?: string) =>
    apiClient<ChatSession>(`/datasets/${datasetId}/chat/sessions`, {
      method: 'POST',
      body: JSON.stringify({ title: title || 'New Analyst Session' }),
    }),

  listChatMessages: (sessionId: string) =>
    apiClient<ChatMessage[]>(`/chat/sessions/${sessionId}/messages`),

  sendChatMessage: (sessionId: string, message: string) =>
    apiClient<ChatMessage>(`/chat/sessions/${sessionId}/messages`, {
      method: 'POST',
      body: JSON.stringify({ message }),
    }),

  // ------------------------------------------------------------------------
  // AI Provider Layer (Phase 9.1 Ollama / Local LLM)
  // ------------------------------------------------------------------------
  getAIHealth: (provider?: string, model?: string) => {
    const params = new URLSearchParams();
    if (provider) params.append('provider', provider);
    if (model) params.append('model', model);
    const qs = params.toString();
    return apiClient<{
      provider: string;
      model: string;
      status: string;
      latency_ms: number;
      available_models: string[];
    }>(`/ai/health${qs ? `?${qs}` : ''}`);
  },

  listAIProviders: () =>
    apiClient<{
      active_provider: string;
      active_model: string;
      providers: Array<{
        name: string;
        description: string;
        is_active: boolean;
        default_model: string;
        supported_models: string[];
      }>;
    }>('/ai/providers'),

  testAIGeneration: (payload: {
    prompt: string;
    system_prompt?: string;
    temperature?: number;
    max_tokens?: number;
    provider?: string;
    model?: string;
  }) =>
    apiClient<{
      generated_text: string;
      provider: string;
      model: string;
      latency_ms: number;
    }>('/ai/test', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  // ------------------------------------------------------------------------
  // AI Narrative Engine (Phase 9.2)
  // ------------------------------------------------------------------------
  getExecutiveNarrative: (
    datasetId: string,
    options?: { provider?: string; model?: string; temperature?: number; focus_areas?: string[] }
  ) =>
    apiClient<any>(`/datasets/${datasetId}/narratives/executive-summary`, {
      method: 'POST',
      body: JSON.stringify(options || {}),
    }),

  getKPINarrative: (
    datasetId: string,
    options?: { provider?: string; model?: string; temperature?: number; focus_areas?: string[] }
  ) =>
    apiClient<any>(`/datasets/${datasetId}/narratives/kpis`, {
      method: 'POST',
      body: JSON.stringify(options || {}),
    }),

  getRootCauseNarrative: (
    datasetId: string,
    options?: { provider?: string; model?: string; temperature?: number; focus_areas?: string[] }
  ) =>
    apiClient<any>(`/datasets/${datasetId}/narratives/root-causes`, {
      method: 'POST',
      body: JSON.stringify(options || {}),
    }),

  getRecommendationNarrative: (
    datasetId: string,
    options?: { provider?: string; model?: string; temperature?: number; focus_areas?: string[] }
  ) =>
    apiClient<any>(`/datasets/${datasetId}/narratives/recommendations`, {
      method: 'POST',
      body: JSON.stringify(options || {}),
    }),

  getForecastNarrative: (
    datasetId: string,
    options?: { forecast_id?: string; metric_key?: string; provider?: string; model?: string; temperature?: number }
  ) =>
    apiClient<any>(`/datasets/${datasetId}/narratives/forecasts`, {
      method: 'POST',
      body: JSON.stringify(options || {}),
    }),

  getScenarioNarrative: (
    datasetId: string,
    options?: { scenario_id?: string; provider?: string; model?: string; temperature?: number }
  ) =>
    apiClient<any>(`/datasets/${datasetId}/narratives/scenarios`, {
      method: 'POST',
      body: JSON.stringify(options || {}),
    }),

  generateFullNarrativePackage: (
    datasetId: string,
    options?: { force_regenerate?: boolean; provider?: string; model?: string; temperature?: number }
  ) =>
    apiClient<any>(`/datasets/${datasetId}/narratives/full-package`, {
      method: 'POST',
      body: JSON.stringify(options || {}),
    }),

  getLatestPersistedNarrativeReport: (datasetId: string) =>
    apiClient<any>(`/datasets/${datasetId}/narratives/latest`),

  listPersistedNarrativeHistory: (datasetId: string, limit = 10, offset = 0) =>
    apiClient<any[]>(`/datasets/${datasetId}/narratives/history?limit=${limit}&offset=${offset}`),
};

export const executiveInsightsApi = {
  getTopRisks: (
    datasetId: string,
    options?: { provider_name?: string; model_name?: string; temperature?: number; force_regenerate?: boolean }
  ) =>
    apiClient<any[]>(`/datasets/${datasetId}/executive-insights/risks`, {
      method: 'POST',
      body: JSON.stringify(options || {}),
    }),

  getTopOpportunities: (
    datasetId: string,
    options?: { provider_name?: string; model_name?: string; temperature?: number; force_regenerate?: boolean }
  ) =>
    apiClient<any[]>(`/datasets/${datasetId}/executive-insights/opportunities`, {
      method: 'POST',
      body: JSON.stringify(options || {}),
    }),

  getPriorityActions: (
    datasetId: string,
    options?: { provider_name?: string; model_name?: string; temperature?: number; force_regenerate?: boolean }
  ) =>
    apiClient<any[]>(`/datasets/${datasetId}/executive-insights/actions`, {
      method: 'POST',
      body: JSON.stringify(options || {}),
    }),

  getStrategicThemes: (
    datasetId: string,
    options?: { provider_name?: string; model_name?: string; temperature?: number; force_regenerate?: boolean }
  ) =>
    apiClient<any[]>(`/datasets/${datasetId}/executive-insights/themes`, {
      method: 'POST',
      body: JSON.stringify(options || {}),
    }),

  getExecutiveAlerts: (
    datasetId: string,
    options?: { provider_name?: string; model_name?: string; temperature?: number; force_regenerate?: boolean }
  ) =>
    apiClient<any[]>(`/datasets/${datasetId}/executive-insights/alerts`, {
      method: 'POST',
      body: JSON.stringify(options || {}),
    }),

  getBoardCommentary: (
    datasetId: string,
    options?: { provider_name?: string; model_name?: string; temperature?: number; force_regenerate?: boolean }
  ) =>
    apiClient<any>(`/datasets/${datasetId}/executive-insights/board-commentary`, {
      method: 'POST',
      body: JSON.stringify(options || {}),
    }),

  generateExecutiveInsights: (
    datasetId: string,
    options?: { provider_name?: string; model_name?: string; temperature?: number; force_regenerate?: boolean }
  ) =>
    apiClient<any>(`/datasets/${datasetId}/executive-insights/full-package`, {
      method: 'POST',
      body: JSON.stringify(options || {}),
    }),

  getExecutiveInsights: (datasetId: string) =>
    apiClient<any>(`/datasets/${datasetId}/executive-insights/latest`),

  getLatestExecutiveInsights: (datasetId: string) =>
    apiClient<any>(`/datasets/${datasetId}/executive-insights/latest`),

  getExecutiveInsightHistory: (datasetId: string, limit = 10, offset = 0) =>
    apiClient<any[]>(`/datasets/${datasetId}/executive-insights/history?limit=${limit}&offset=${offset}`),
};

export const chatAnalystApi = {
  createSession: (
    datasetId: string,
    title?: string,
    options?: { provider?: string; model?: string }
  ) =>
    apiClient<any>(`/chat/sessions`, {
      method: 'POST',
      body: JSON.stringify({ dataset_id: datasetId, title, ...(options || {}) }),
    }),

  listSessions: (datasetId: string, limit = 20, offset = 0) =>
    apiClient<any[]>(`/chat/sessions?dataset_id=${datasetId}&limit=${limit}&offset=${offset}`),

  getSession: (sessionId: string) =>
    apiClient<any>(`/chat/sessions/${sessionId}`),

  deleteSession: (sessionId: string) =>
    apiClient<any>(`/chat/sessions/${sessionId}`, {
      method: 'DELETE',
    }),

  sendMessage: (
    sessionId: string,
    message: string,
    options?: { provider_override?: string; model_override?: string; temperature?: number }
  ) =>
    apiClient<any>(`/chat/sessions/${sessionId}/messages`, {
      method: 'POST',
      body: JSON.stringify({ message, ...(options || {}) }),
    }),

  getMessages: (sessionId: string, limit = 50, offset = 0) =>
    apiClient<any[]>(`/chat/sessions/${sessionId}/messages?limit=${limit}&offset=${offset}`),
};

export const reportingApi = {
  generateReport: (payload: {
    dataset_id: string;
    report_type?: string;
    export_format?: string;
    title?: string;
    company_name?: string;
    include_raw_evidence?: boolean;
  }) =>
    apiClient<any>(`/reports/generate`, {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  getReport: (reportId: string) =>
    apiClient<any>(`/reports/${reportId}`),

  listReports: (
    datasetId: string,
    options?: { report_type?: string; export_format?: string; limit?: number; offset?: number }
  ) => {
    const params = new URLSearchParams();
    if (options?.report_type) params.append('report_type', options.report_type);
    if (options?.export_format) params.append('export_format', options.export_format);
    if (options?.limit) params.append('limit', options.limit.toString());
    if (options?.offset) params.append('offset', options.offset.toString());
    const qs = params.toString();
    return apiClient<any[]>(`/reports/dataset/${datasetId}${qs ? `?${qs}` : ''}`);
  },

  deleteReport: (reportId: string) =>
    apiClient<any>(`/reports/${reportId}`, {
      method: 'DELETE',
    }),

  downloadReportUrl: (reportId: string) =>
    `/api/v1/reports/download/${reportId}`,
};

export const competitiveIntelligenceApi = {
  /**
   * GET /api/v1/os/benchmarks/market-position
   * Org-scoped. Returns market rank, percentile, tracked competitors, and live SWOT quadrants.
   */
  getMarketPosition: () =>
    apiClient<CompetitiveSnapshotResponse>('/os/benchmarks/market-position'),

  /**
   * GET /api/v1/os/benchmarks/comparisons
   * Org-scoped. Returns metric-by-metric gaps vs industry median, top quartile, best-in-class.
   */
  getComparisons: () =>
    apiClient<CompetitiveBenchmarkResponse[]>('/os/benchmarks/comparisons'),

  /**
   * GET /api/v1/os/benchmarks/opportunities
   * Org-scoped. Returns ARR opportunity candidates derived from benchmark gaps.
   * Includes auto_scenario_id when a Digital Twin scenario has been auto-generated.
   */
  getOpportunities: () =>
    apiClient<BenchmarkOpportunityResponse[]>('/os/benchmarks/opportunities'),
};

export const portfolioApi = {
  /**
   * GET /api/v1/portfolio/summary
   * Org-scoped. Returns executive portfolio summary across all workspaces.
   * Used by: CapitalAllocationStudioView, PortfolioRollupView, RiskConcentrationRadarView
   */
  getSummary: () =>
    apiClient<PortfolioSummaryResponse>('/portfolio/summary'),

  /**
   * GET /api/v1/portfolio/executive/risk
   * Org-scoped. Returns risk concentration metrics across the organization portfolio.
   * Used by: RiskConcentrationRadarView
   */
  getExecutiveRisk: () =>
    apiClient<PortfolioRiskSummary>('/portfolio/executive/risk'),
};

export const governanceApi = {
  /**
   * GET /api/v1/os/governance/scorecard
   * Auth-protected. Returns enterprise governance health scorecard.
   */
  getScorecard: () =>
    apiClient<GovernanceScorecardResponse>('/os/governance/scorecard'),

  /**
   * GET /api/v1/ai-governance/report
   * Returns AI usage governance report including interactions, cost, and trust score.
   */
  getAIGovernanceReport: () =>
    apiClient<AIGovernanceReportResponse>('/ai-governance/report'),

  /**
   * GET /api/v1/security-center/posture
   * Returns security posture scorecard with controls and compliance status.
   */
  getSecurityPosture: () =>
    apiClient<SecurityPostureResponse>('/security-center/posture'),
};

export const dashboardApi = {
  getWorkspace: (datasetId: string, sections?: string) =>
    apiClient<any>(`/dashboard/${datasetId}/workspace${sections ? `?sections=${sections}` : ''}`),

  refreshSnapshot: (datasetId: string, trigger = 'MANUAL') =>
    apiClient<any>(`/dashboard/${datasetId}/refresh?trigger=${trigger}`, {
      method: 'POST',
    }),

  getStatus: (datasetId: string) =>
    apiClient<any>(`/dashboard/${datasetId}/status`),

  recordTelemetry: (datasetId: string, events: Array<{ section: string; viewed_at?: string; event_metadata?: Record<string, any> }>) =>
    apiClient<any>(`/dashboard/${datasetId}/telemetry`, {
      method: 'POST',
      body: JSON.stringify({ events }),
    }),

  getMetricsSummary: () =>
    apiClient<any>(`/dashboard/metrics/summary`),
};







