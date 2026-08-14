import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { ExecutiveReportDocument } from '../components/report/ExecutiveReportDocument';
import { ExecutiveReportData } from '../types';

describe('ExecutiveReportDocument Component', () => {
  const mockReportData: ExecutiveReportData = {
    reportId: 'rep-test-12345',
    datasetId: 'd-12345678',
    generatedAt: '2026-08-14T00:00:00Z',
    generatedBy: 'executive@decisionos.ai',
    reportVersion: '1.0.0',
    dataset: {
      id: 'd-12345678',
      name: 'Retail Performance Q3',
      original_filename: 'retail.csv',
      status: 'ACTIVE',
      file_size: 32000,
      created_at: '2026-08-14T00:00:00Z',
      updated_at: '2026-08-14T00:00:00Z',
    },
    health: {
      dataset_id: 'd-12345678',
      score: 91,
      status: 'EXCELLENT',
      description: 'Strong performance',
    },
    executiveSummary: {
      dataset_id: 'd-12345678',
      generated_at: '2026-08-14T00:00:00Z',
      primary_issue: 'Revenue Churn Contained',
      severity: 'LOW',
      top_root_cause: 'Support Resolution Lag',
      top_recommendation: 'Automate Tier 1 Triage',
      key_risks: [],
      overall_confidence: 0.95,
      confidence_breakdown: {},
      business_health_score: 91,
      business_health_status: 'EXCELLENT',
      expected_business_impact: 'Retains $150k monthly ARR',
    },
    intelligenceReport: {
      report_version: '1.0',
      dataset_id: 'd-12345678',
      dataset_name: 'Retail Performance Q3',
      generated_at: '2026-08-14T00:00:00Z',
      artifact_counts: {},
      metrics: [
        {
          id: 'm1',
          metric_key: 'total_revenue',
          metric_name: 'Total Revenue',
          metric_category: 'REVENUE',
          metric_value: 2450000,
          calculated_at: '2026-08-14T00:00:00Z',
        },
      ],
      findings: [
        {
          id: 'f1',
          finding_type: 'MARGIN_EROSION',
          severity: 'HIGH',
          title: 'Ad CAC Inflation',
          description: 'CAC increased 22% in July',
          business_impact: 'Margins contracted by 3.2%',
          confidence_score: 0.92,
          created_at: '2026-08-14T00:00:00Z',
        },
      ],
      root_causes: [],
      recommendations: [
        {
          id: 'r1',
          recommendation_key: 'rec_ad_opt',
          title: 'Reallocate Paid Ad Channels',
          action_summary: 'Shift budget from low ROAS campaigns to search ads',
          priority: 'HIGH',
          expected_impact: '+$40k profit/mo',
          estimated_effort: 'LOW',
          time_to_value: '2 WEEKS',
          status: 'PROPOSED',
          created_at: '2026-08-14T00:00:00Z',
        },
      ],
      executive_summary: {} as any,
    },
    aiInsight: {
      id: 'ai-1',
      dataset_id: 'd-12345678',
      executive_narrative: 'Executive financial assessment indicates steady expansion.',
      key_takeaways: ['Sustain CAC optimization'],
      business_assessment: 'Strong healthy trajectory',
      risk_analysis: ['Paid ad saturation'],
      strategic_priorities: ['Scale organic growth'],
      action_plan_90_day: [],
      model_name: 'gpt-4o-deterministic-hybrid',
      insight_version: '1.0',
      created_at: '2026-08-14T00:00:00Z',
    },
  };

  it('renders all executive sections with accurate labels and audit trail', () => {
    render(<ExecutiveReportDocument data={mockReportData} />);

    // Header & Metadata
    expect(screen.getByText('Executive Decision Intelligence Report')).toBeInTheDocument();
    expect(screen.getByText('Dataset: Retail Performance Q3')).toBeInTheDocument();
    expect(screen.getByText(/rep-test-12345/)).toBeInTheDocument();

    // Section 1 Summary
    expect(screen.getByText('1. Executive Summary & Business Health')).toBeInTheDocument();
    expect(screen.getByText('Revenue Churn Contained')).toBeInTheDocument();

    // Section 2 Metrics
    expect(screen.getByText('2. Core KPI Performance Indicators')).toBeInTheDocument();
    expect(screen.getByText('$2,450,000')).toBeInTheDocument();

    // Section 3 Diagnostics
    expect(screen.getByText('3. Business Diagnostic Findings')).toBeInTheDocument();
    expect(screen.getByText('Ad CAC Inflation')).toBeInTheDocument();

    // Section 5 Recommendations
    expect(screen.getByText('5. Prescribed Actionable Recommendations')).toBeInTheDocument();
    expect(screen.getByText('Reallocate Paid Ad Channels')).toBeInTheDocument();

    // Section 6 AI Synthesis
    expect(screen.getByText('6. AI-Generated Executive Narrative & Assessment')).toBeInTheDocument();
    expect(screen.getByText('Executive financial assessment indicates steady expansion.')).toBeInTheDocument();
    expect(screen.getByText(/Model: gpt-4o-deterministic-hybrid/)).toBeInTheDocument();
  });
});
