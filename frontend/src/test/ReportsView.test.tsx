import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { ReportsView } from '../views/reports/ReportsView';
import { useDataset } from '../context/DatasetContext';
import { useAuth } from '../context/AuthContext';
import * as reportAggregator from '../services/reportAggregator';

vi.mock('../context/DatasetContext', () => ({
  useDataset: vi.fn(),
}));

vi.mock('../context/AuthContext', () => ({
  useAuth: vi.fn(),
}));

describe('ReportsView Component', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('renders empty state when no dataset is active', () => {
    (useDataset as any).mockReturnValue({ activeDataset: null });
    (useAuth as any).mockReturnValue({ user: { email: 'exec@test.com' } });

    render(<ReportsView />);
    expect(screen.getByText('No Active Dataset Selected')).toBeInTheDocument();
  });

  it('renders report studio and export button when active dataset is loaded', async () => {
    const mockDataset = {
      id: 'd-1',
      name: 'SaaS Expansion',
      original_filename: 'saas.csv',
      status: 'ACTIVE',
      file_size: 20000,
      created_at: '2026-08-14T00:00:00Z',
      updated_at: '2026-08-14T00:00:00Z',
    };

    (useDataset as any).mockReturnValue({ activeDataset: mockDataset });
    (useAuth as any).mockReturnValue({ user: { email: 'exec@test.com' } });

    vi.spyOn(reportAggregator, 'aggregateReportData').mockResolvedValue({
      reportId: 'rep-saas-1',
      datasetId: 'd-1',
      generatedAt: '2026-08-14T00:00:00Z',
      generatedBy: 'exec@test.com',
      reportVersion: '1.0.0',
      dataset: mockDataset,
      health: { dataset_id: 'd-1', score: 80, status: 'HEALTHY', description: 'Good health' },
      executiveSummary: {
        dataset_id: 'd-1',
        generated_at: '2026-08-14T00:00:00Z',
        primary_issue: 'Healthy growth',
        severity: 'LOW',
        key_risks: [],
        overall_confidence: 0.9,
        confidence_breakdown: {},
        business_health_score: 80,
        business_health_status: 'HEALTHY',
        expected_business_impact: 'Stable',
      },
      intelligenceReport: {
        report_version: '1.0',
        dataset_id: 'd-1',
        dataset_name: 'SaaS Expansion',
        generated_at: '2026-08-14T00:00:00Z',
        artifact_counts: {},
        metrics: [],
        findings: [],
        root_causes: [],
        recommendations: [],
        executive_summary: {} as any,
      },
    });

    render(<ReportsView />);

    expect(screen.getByText('Executive Report Studio')).toBeInTheDocument();
    expect(screen.getByText('Export Executive PDF')).toBeInTheDocument();
    expect(screen.getByText('Include Report Sections:')).toBeInTheDocument();
  });
});
