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
  // KPI Metrics
  // ------------------------------------------------------------------------
  listMetrics: (datasetId: string) =>
    apiClient<DatasetMetric[]>(`/datasets/${datasetId}/metrics`),

  // ------------------------------------------------------------------------
  // Root Causes & Recommendations
  // ------------------------------------------------------------------------
  getRootCausesResponse: (datasetId: string) =>
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
    apiClient<StrategyPlan>(`/datasets/${datasetId}/strategy/latest`),

  generateStrategy: (datasetId: string) =>
    apiClient<StrategyPlan>(`/datasets/${datasetId}/strategy/generate`, {
      method: 'POST',
    }),

  updateActionStatus: (planId: string, actionId: string, isCompleted: boolean) =>
    apiClient<any>(`/strategy/${planId}/actions/${actionId}`, {
      method: 'PATCH',
      body: JSON.stringify({ is_completed: isCompleted }),
    }),

  // ------------------------------------------------------------------------
  // Scenario Simulation
  // ------------------------------------------------------------------------
  listScenarios: (datasetId: string) =>
    apiClient<Scenario[]>(`/datasets/${datasetId}/scenarios`),

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




