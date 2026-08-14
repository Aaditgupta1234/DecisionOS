import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { CausalGraphCanvas } from '../components/graph/CausalGraphCanvas';
import { CausalGraphNode, CausalGraphEdge } from '../types';

describe('CausalGraphCanvas Component', () => {
  const mockNodes: CausalGraphNode[] = [
    { id: 'f-1', title: 'Ad Spend Spike', category: 'MARKETING', subtype: 'ad_spike', severity: 'MEDIUM', confidence_score: 0.88 },
    { id: 'f-2', title: 'Margin Compression', category: 'REVENUE', subtype: 'margin_drop', severity: 'CRITICAL', confidence_score: 0.92 },
  ];

  const mockEdges: CausalGraphEdge[] = [
    { source_id: 'f-1', target_id: 'f-2', relationship_type: 'CAUSES', relationship_strength: 'STRONG', confidence_score: 0.9, impact_score: 0.85 },
  ];

  it('renders SVG nodes and invokes onSelectNode when a node is clicked', () => {
    const handleSelectNode = vi.fn();
    const handleSelectEdge = vi.fn();

    render(
      <CausalGraphCanvas
        nodes={mockNodes}
        edges={mockEdges}
        selectedNodeId={null}
        selectedEdgeId={null}
        onSelectNode={handleSelectNode}
        onSelectEdge={handleSelectEdge}
        zoom={1.0}
        panOffset={{ x: 0, y: 0 }}
        onPanChange={vi.fn()}
        onZoomChange={vi.fn()}
      />
    );

    expect(screen.getByText('Ad Spend Spike')).toBeInTheDocument();
    expect(screen.getByText('Margin Compression')).toBeInTheDocument();

    const nodeElement = screen.getByText('Ad Spend Spike');
    fireEvent.click(nodeElement);
    expect(handleSelectNode).toHaveBeenCalled();
  });
});
