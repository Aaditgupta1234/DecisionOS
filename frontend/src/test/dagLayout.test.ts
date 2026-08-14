import { describe, it, expect } from 'vitest';
import { computeDagLayout } from '../components/graph/dagLayout';
import { CausalGraphNode, CausalGraphEdge } from '../types';

describe('DAG Layout Algorithm (computeDagLayout)', () => {
  it('correctly ranks nodes from root cause to downstream terminal effect', () => {
    const nodes: CausalGraphNode[] = [
      { id: 'n1', title: 'Delivery Delays', category: 'OPERATIONS', subtype: 'operational_delay', severity: 'HIGH', confidence_score: 0.9 },
      { id: 'n2', title: 'Customer Churn', category: 'CUSTOMER', subtype: 'churn_spike', severity: 'HIGH', confidence_score: 0.85 },
      { id: 'n3', title: 'Revenue Decline', category: 'REVENUE', subtype: 'revenue_decline', severity: 'CRITICAL', confidence_score: 0.95 },
    ];

    const edges: CausalGraphEdge[] = [
      { source_id: 'n1', target_id: 'n2', relationship_type: 'CAUSES', relationship_strength: 'STRONG', confidence_score: 0.9, impact_score: 0.8 },
      { source_id: 'n2', target_id: 'n3', relationship_type: 'CAUSES', relationship_strength: 'VERY_STRONG', confidence_score: 0.95, impact_score: 0.9 },
    ];

    const result = computeDagLayout(nodes, edges);

    expect(result.nodes).toHaveLength(3);
    expect(result.edges).toHaveLength(2);

    const n1 = result.nodes.find((n) => n.id === 'n1')!;
    const n2 = result.nodes.find((n) => n.id === 'n2')!;
    const n3 = result.nodes.find((n) => n.id === 'n3')!;

    // n1 is root cause (rank 0), n2 is intermediate (rank 1), n3 is outcome (rank 2)
    expect(n1.rank).toBe(0);
    expect(n1.isRootCause).toBe(true);
    expect(n1.isTerminalEffect).toBe(false);

    expect(n2.rank).toBe(1);
    expect(n2.isRootCause).toBe(false);

    expect(n3.rank).toBe(2);
    expect(n3.isTerminalEffect).toBe(true);

    // Coordinate ordering (left to right)
    expect(n1.x).toBeLessThan(n2.x);
    expect(n2.x).toBeLessThan(n3.x);

    // Edge path calculations
    expect(result.edges[0].pathD).toContain('M');
    expect(result.edges[0].pathD).toContain('C');
  });

  it('handles empty graphs gracefully', () => {
    const result = computeDagLayout([], []);
    expect(result.nodes).toHaveLength(0);
    expect(result.edges).toHaveLength(0);
  });
});
