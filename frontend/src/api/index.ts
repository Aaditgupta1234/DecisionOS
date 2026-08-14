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
  // Datasets
  // ------------------------------------------------------------------------
  listDatasets: () => apiClient<Dataset[]>('/datasets'),
  
  getDataset: (datasetId: string) => apiClient<Dataset>(`/datasets/${datasetId}`),

  uploadDataset: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return apiClient<Dataset>('/datasets/upload', {
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
};
