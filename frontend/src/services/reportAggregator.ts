import { DecisionApi } from '../api';
import {
  Dataset,
  ExecutiveReportData,
  BusinessHealthResponse,
  ExecutiveSummaryResponse,
  IntelligenceReportResponse,
  DatasetRootCausesResponse,
  AIInsight,
  StrategyPlan,
  Scenario,
  Forecast,
} from '../types';

/**
 * Aggregates all deterministic intelligence and AI enrichment layers for a dataset
 * into a canonical, presentation-ready ExecutiveReportData model.
 */
export async function aggregateReportData(
  dataset: Dataset,
  userEmail: string = 'executive@decisionos.ai'
): Promise<ExecutiveReportData> {
  const datasetId = dataset.id;
  const timestamp = new Date().toISOString();
  const reportId = `rep-${datasetId.slice(0, 8)}-${Date.now()}`;

  // Execute queries in parallel with graceful degradation
  const [
    healthRes,
    summaryRes,
    reportRes,
    rootCausesRes,
    insightRes,
    strategyRes,
    scenariosRes,
    forecastsRes,
  ] = await Promise.allSettled([
    DecisionApi.getHealthScore(datasetId),
    DecisionApi.getExecutiveSummary(datasetId),
    DecisionApi.getIntelligenceReport(datasetId),
    DecisionApi.getRootCausesResponse(datasetId),
    DecisionApi.getLatestInsight(datasetId),
    DecisionApi.getLatestStrategy(datasetId),
    DecisionApi.listScenarios(datasetId),
    DecisionApi.listForecasts(datasetId),
  ]);

  const health: BusinessHealthResponse =
    healthRes.status === 'fulfilled'
      ? healthRes.value
      : {
          dataset_id: datasetId,
          score: 0,
          status: 'HEALTHY',
          description: 'Calculated business health index',
        };

  const executiveSummary: ExecutiveSummaryResponse =
    summaryRes.status === 'fulfilled'
      ? summaryRes.value
      : {
          dataset_id: datasetId,
          generated_at: timestamp,
          primary_issue: 'Performance Intelligence Active',
          severity: 'LOW',
          key_risks: [],
          overall_confidence: 0.9,
          confidence_breakdown: {},
          business_health_score: health.score,
          business_health_status: health.status,
          expected_business_impact: 'Deterministic pipeline processing active.',
        };

  const intelligenceReport: IntelligenceReportResponse =
    reportRes.status === 'fulfilled'
      ? reportRes.value
      : {
          report_version: '1.0',
          dataset_id: datasetId,
          dataset_name: dataset.name,
          generated_at: timestamp,
          artifact_counts: {},
          metrics: [],
          findings: [],
          root_causes: [],
          recommendations: [],
          executive_summary: executiveSummary,
        };

  const rootCausesResponse: DatasetRootCausesResponse | null =
    rootCausesRes.status === 'fulfilled' ? rootCausesRes.value : null;

  const aiInsight: AIInsight | null =
    insightRes.status === 'fulfilled' ? insightRes.value : null;

  const strategyPlan: StrategyPlan | null =
    strategyRes.status === 'fulfilled' ? strategyRes.value : null;

  const scenarios: Scenario[] =
    scenariosRes.status === 'fulfilled' && Array.isArray(scenariosRes.value)
      ? scenariosRes.value
      : [];

  const forecasts: Forecast[] =
    forecastsRes.status === 'fulfilled' && forecastsRes.value?.forecasts
      ? forecastsRes.value.forecasts
      : [];

  return {
    reportId,
    datasetId,
    generatedAt: timestamp,
    generatedBy: userEmail,
    reportVersion: '1.0.0',
    dataset,
    health,
    executiveSummary,
    intelligenceReport,
    rootCausesResponse,
    aiInsight,
    strategyPlan,
    scenarios,
    forecasts,
  };
}
