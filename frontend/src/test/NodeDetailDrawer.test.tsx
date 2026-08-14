import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { describe, it, expect, vi } from 'vitest';
import { NodeDetailDrawer } from '../components/graph/NodeDetailDrawer';
import { LayoutNode } from '../components/graph/dagLayout';
import { RootCauseAnalysisRecord } from '../types';

describe('NodeDetailDrawer Component', () => {
  const mockNode: LayoutNode = {
    id: 'f-root',
    title: 'Customer Churn Surge',
    category: 'CUSTOMER',
    subtype: 'churn_anomaly',
    severity: 'CRITICAL',
    confidence_score: 0.94,
    x: 50,
    y: 50,
    width: 220,
    height: 92,
    rank: 0,
    isRootCause: true,
    isTerminalEffect: false,
  };

  const mockAnalyses: RootCauseAnalysisRecord[] = [
    {
      id: 'ana-1',
      dataset_id: 'd-1',
      primary_finding_id: 'f-effect',
      root_cause_finding_id: 'f-root',
      relationship_type: 'CAUSES',
      relationship_strength: 'VERY_STRONG',
      confidence_score: 0.95,
      impact_score: 0.9,
      explanation: 'Customer churn directly reduced recurring subscription volume.',
      created_at: '2026-08-14T00:00:00Z',
      primary_finding: {
        id: 'f-effect',
        title: 'Monthly Recurring Revenue Drop',
        description: 'Revenue dropped significantly in Q3',
        finding_type: 'MARGIN_EROSION',
        severity: 'CRITICAL',
        confidence_score: 0.96,
        business_impact: 'Revenue fell by 18%',
        created_at: '2026-08-14T00:00:00Z',
      },
    },
  ];

  it('renders node details and downstream triggered effect', () => {
    render(
      <BrowserRouter>
        <NodeDetailDrawer
          node={mockNode}
          analyses={mockAnalyses}
          onClose={vi.fn()}
        />
      </BrowserRouter>
    );

    expect(screen.getByText('Customer Churn Surge')).toBeInTheDocument();
    expect(screen.getByText('94%')).toBeInTheDocument();
    expect(screen.getByText('Root Origin')).toBeInTheDocument();
    expect(screen.getByText('Monthly Recurring Revenue Drop')).toBeInTheDocument();
  });
});
