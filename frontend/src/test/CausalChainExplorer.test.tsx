import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { CausalChainExplorer } from '../components/graph/CausalChainExplorer';
import { CausalGraphNode, RootCauseSummaryGroup } from '../types';

describe('CausalChainExplorer Component', () => {
  const mockNodes: CausalGraphNode[] = [
    { id: 'f-1', title: 'Server Latency', category: 'OPS', subtype: 'latency', severity: 'HIGH', confidence_score: 0.9 },
    { id: 'f-2', title: 'Cart Abandonment', category: 'CONVERSION', subtype: 'drop', severity: 'HIGH', confidence_score: 0.88 },
    { id: 'f-3', title: 'Revenue Loss', category: 'REVENUE', subtype: 'loss', severity: 'CRITICAL', confidence_score: 0.95 },
  ];

  const mockSummaries: RootCauseSummaryGroup[] = [
    {
      primary_issue: 'Revenue Loss',
      primary_finding_id: 'f-3',
      primary_severity: 'CRITICAL',
      root_causes: [],
      overall_confidence: 0.92,
      highest_impact: 0.95,
      causal_chains: [['f-1', 'f-2', 'f-3']],
    },
  ];

  it('renders multi-hop chain path and allows clicking to select', () => {
    const handleSelectChain = vi.fn();

    render(
      <CausalChainExplorer
        summaries={mockSummaries}
        nodes={mockNodes}
        activeChainNodeIds={[]}
        onSelectChain={handleSelectChain}
        onClearChain={vi.fn()}
      />
    );

    expect(screen.getByText('Server Latency')).toBeInTheDocument();
    expect(screen.getByText('Cart Abandonment')).toBeInTheDocument();
    expect(screen.getByText('Revenue Loss')).toBeInTheDocument();

    const pathButton = screen.getByText('Path #1').closest('button')!;
    fireEvent.click(pathButton);

    expect(handleSelectChain).toHaveBeenCalledWith(['f-1', 'f-2', 'f-3']);
  });
});
