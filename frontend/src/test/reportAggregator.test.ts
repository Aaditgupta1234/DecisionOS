import { describe, it, expect, vi, beforeEach } from 'vitest';
import { aggregateReportData } from '../services/reportAggregator';
import { DecisionApi } from '../api';
import { Dataset } from '../types';

describe('Report Aggregator Service (aggregateReportData)', () => {
  const mockDataset: Dataset = {
    id: 'd-12345678',
    name: 'Enterprise Q3 Financials',
    original_filename: 'q3_sales.csv',
    status: 'ACTIVE',
    file_size: 45000,
    created_at: '2026-08-14T00:00:00Z',
    updated_at: '2026-08-14T00:00:00Z',
  };

  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('aggregates all dataset artifacts with audit metadata', async () => {
    vi.spyOn(DecisionApi, 'getHealthScore').mockResolvedValue({
      dataset_id: 'd-12345678',
      score: 88,
      status: 'HEALTHY',
      description: 'Strong health',
    });

    vi.spyOn(DecisionApi, 'getExecutiveSummary').mockResolvedValue({
      dataset_id: 'd-12345678',
      generated_at: '2026-08-14T00:00:00Z',
      primary_issue: 'Operational bottleneck detected',
      severity: 'HIGH',
      key_risks: ['Margin compression'],
      overall_confidence: 0.94,
      confidence_breakdown: {},
      business_health_score: 88,
      business_health_status: 'HEALTHY',
      expected_business_impact: 'High upside upon remediation',
    });

    vi.spyOn(DecisionApi, 'getIntelligenceReport').mockResolvedValue({
      report_version: '1.0',
      dataset_id: 'd-12345678',
      dataset_name: 'Enterprise Q3 Financials',
      generated_at: '2026-08-14T00:00:00Z',
      artifact_counts: {},
      metrics: [],
      findings: [],
      root_causes: [],
      recommendations: [],
      executive_summary: {} as any,
    });

    vi.spyOn(DecisionApi, 'getRootCausesResponse').mockResolvedValue({
      dataset_id: 'd-12345678',
      total_root_causes: 1,
      analyses: [],
      summaries: [],
      graph: { nodes: [], edges: [] },
    });

    vi.spyOn(DecisionApi, 'getLatestInsight').mockResolvedValue(null as any);
    vi.spyOn(DecisionApi, 'getLatestStrategy').mockResolvedValue(null as any);
    vi.spyOn(DecisionApi, 'listScenarios').mockResolvedValue([]);
    vi.spyOn(DecisionApi, 'listForecasts').mockResolvedValue({ total_count: 0, forecasts: [] });

    const result = await aggregateReportData(mockDataset, 'cfo@company.com');

    expect(result.reportId).toContain('rep-d-123456');
    expect(result.datasetId).toBe('d-12345678');
    expect(result.generatedBy).toBe('cfo@company.com');
    expect(result.reportVersion).toBe('1.0.0');
    expect(result.health.score).toBe(88);
    expect(result.executiveSummary.primary_issue).toBe('Operational bottleneck detected');
    expect(result.aiInsight).toBeNull();
  });
});
