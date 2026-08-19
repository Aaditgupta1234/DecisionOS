import React, { useState } from 'react';
import { Network, Database, Target, AlertTriangle, CheckCircle2, GitBranch, ShieldCheck, Filter, Eye, Layers, ArrowRight } from 'lucide-react';
import { ExplainabilityDrawer } from '../../components/workspace/ExplainabilityDrawer';

export const KnowledgeGraphExplorerView: React.FC = () => {
  const [selectedNodeType, setSelectedNodeType] = useState('ALL');
  const [selectedNode, setSelectedNode] = useState<any | null>(null);
  const [isExplainOpen, setIsExplainOpen] = useState(false);

  const nodes = [
    { id: '1', type: 'DATASET', name: 'Master Orders Telemetry Stream', status: 'ACTIVE', system: 'DatasetIngestionEngine', confidence: 0.98, edgesCount: 3 },
    { id: '2', type: 'KPI', name: 'Customer Retention Rate', status: 'ACTIVE', system: 'KPIEngine', confidence: 0.95, edgesCount: 4 },
    { id: '3', type: 'KPI', name: 'Delivery Latency (Days)', status: 'ACTIVE', system: 'KPIEngine', confidence: 0.96, edgesCount: 3 },
    { id: '4', type: 'FINDING', name: 'Southeastern Transit Delays (+68.8%)', status: 'ACTIVE', system: 'DiagnosticsEngine', confidence: 0.94, edgesCount: 2 },
    { id: '5', type: 'ROOT_CAUSE', name: 'Secondary Hub Dispatch Bottleneck', status: 'ACTIVE', system: 'RootCauseEngine', confidence: 0.94, edgesCount: 3 },
    { id: '6', type: 'RECOMMENDATION', name: 'Carrier Rebalancing & Automated SLA Penalties', status: 'ACTIVE', system: 'RecommendationEngine', confidence: 0.92, edgesCount: 4 },
    { id: '7', type: 'INITIATIVE', name: 'INIT-2026-001: Win-Back & SLA Deployment', status: 'ACTIVE', system: 'ExecutionEngine', confidence: 0.95, edgesCount: 2 },
    { id: '8', type: 'ALERT', name: 'CRITICAL: Retention Drift (-7.3%)', status: 'ACTIVE', system: 'ExecutiveAlertEngine', confidence: 0.99, edgesCount: 2 },
    { id: '9', type: 'OUTCOME', name: 'Verified +$124K ARR Realized Recovery', status: 'ACTIVE', system: 'OutcomeEngine', confidence: 0.96, edgesCount: 2 },
  ];

  const filteredNodes = selectedNodeType === 'ALL' ? nodes : nodes.filter((n) => n.type === selectedNodeType);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px', paddingBottom: '40px' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <div style={{ fontSize: '0.72rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: '#10B981', fontWeight: 800 }}>
            Deterministic Causal DAG & Lineage Layer
          </div>
          <h1 style={{ fontSize: '1.8rem', fontWeight: 900, color: '#FFFFFF', margin: '4px 0 0 0' }}>
            Knowledge Graph Explorer
          </h1>
        </div>

        {/* Snapshot Telemetry Pill */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', background: 'rgba(16, 185, 129, 0.1)', border: '1px solid rgba(16, 185, 129, 0.25)', padding: '6px 14px', borderRadius: '20px' }}>
          <ShieldCheck size={14} color="#10B981" />
          <span style={{ fontSize: '0.78rem', color: '#10B981', fontWeight: 700 }}>Graph V3: 28 Nodes • 42 Edges • Cycles: 0 • Health: 96.4</span>
        </div>
      </div>

      {/* Filter Tabs */}
      <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap', background: 'rgba(15, 23, 42, 0.8)', border: '1px solid #1E293B', padding: '6px', borderRadius: '8px' }}>
        {['ALL', 'DATASET', 'KPI', 'FINDING', 'ROOT_CAUSE', 'RECOMMENDATION', 'INITIATIVE', 'ALERT', 'OUTCOME'].map((t) => (
          <button
            key={t}
            onClick={() => setSelectedNodeType(t)}
            style={{
              padding: '5px 12px',
              borderRadius: '4px',
              border: 'none',
              background: selectedNodeType === t ? '#0284C7' : 'transparent',
              color: selectedNodeType === t ? '#FFFFFF' : '#94A3B8',
              fontSize: '0.74rem',
              fontWeight: 700,
              cursor: 'pointer',
            }}
          >
            {t}
          </button>
        ))}
      </div>

      {/* 2-Column Graph Canvas + Node Inspector Layout */}
      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '20px' }}>
        {/* Left: Interactive DAG Grid */}
        <div style={{ background: '#090D14', border: '1px solid #1E293B', borderRadius: '12px', padding: '20px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <div style={{ fontSize: '0.9rem', fontWeight: 800, color: '#FFFFFF', display: 'flex', alignItems: 'center', gap: '6px' }}>
            <Layers size={14} color="#38BDF8" />
            <span>Topological DAG Entities ({filteredNodes.length})</span>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '12px', maxHeight: '500px', overflowY: 'auto' }}>
            {filteredNodes.map((n) => {
              const isSelected = selectedNode?.id === n.id;
              return (
                <div
                  key={n.id}
                  onClick={() => setSelectedNode(n)}
                  style={{
                    padding: '14px',
                    borderRadius: '8px',
                    background: isSelected ? 'rgba(56, 189, 248, 0.15)' : 'rgba(15, 23, 42, 0.7)',
                    border: `1px solid ${isSelected ? '#38BDF8' : '#1E293B'}`,
                    cursor: 'pointer',
                    transition: 'all 0.15s ease',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '4px' }}>
                    <span style={{ fontSize: '0.68rem', fontWeight: 800, textTransform: 'uppercase', color: '#38BDF8' }}>
                      {n.type}
                    </span>
                    <span style={{ fontSize: '0.68rem', color: '#10B981', fontWeight: 700 }}>
                      {Math.round(n.confidence * 100)}% Conf
                    </span>
                  </div>
                  <div style={{ fontSize: '0.85rem', fontWeight: 700, color: '#FFFFFF' }}>{n.name}</div>
                  <div style={{ fontSize: '0.72rem', color: '#64748B', marginTop: '4px' }}>
                    System: {n.system} • {n.edgesCount} Edges
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Right: Node & Edge Inspector */}
        <div style={{ background: '#090D14', border: '1px solid #1E293B', borderRadius: '12px', padding: '20px', display: 'flex', flexDirection: 'column', gap: '14px' }}>
          <div style={{ fontSize: '0.9rem', fontWeight: 800, color: '#FFFFFF' }}>Node & Edge Inspector</div>

          {selectedNode ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              <div style={{ background: 'rgba(15, 23, 42, 0.6)', border: '1px solid #1E293B', borderRadius: '8px', padding: '14px' }}>
                <div style={{ fontSize: '0.7rem', color: '#64748B', textTransform: 'uppercase', fontWeight: 700 }}>ENTITY NAME</div>
                <div style={{ fontSize: '0.95rem', fontWeight: 800, color: '#38BDF8', marginTop: '2px' }}>{selectedNode.name}</div>
                <div style={{ fontSize: '0.75rem', color: '#94A3B8', marginTop: '6px' }}>Type: {selectedNode.type} • Status: {selectedNode.status}</div>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                <div style={{ fontSize: '0.75rem', color: '#64748B', fontWeight: 700 }}>DOWNSTREAM RELATIONSHIPS</div>
                <div style={{ padding: '8px 12px', background: 'rgba(15, 23, 42, 0.6)', border: '1px solid #1E293B', borderRadius: '6px', fontSize: '0.78rem', color: '#CBD5E1' }}>
                  → RECOMMENDED → Carrier Rebalancing (Conf: 94%)
                </div>
                <div style={{ padding: '8px 12px', background: 'rgba(15, 23, 42, 0.6)', border: '1px solid #1E293B', borderRadius: '6px', fontSize: '0.78rem', color: '#CBD5E1' }}>
                  → EXECUTED_BY → INIT-2026-001 (Conf: 91%)
                </div>
              </div>

              <button
                onClick={() => setIsExplainOpen(true)}
                style={{
                  marginTop: '10px',
                  padding: '10px',
                  background: '#0284C7',
                  border: 'none',
                  borderRadius: '6px',
                  color: '#FFFFFF',
                  fontSize: '0.82rem',
                  fontWeight: 700,
                  cursor: 'pointer',
                }}
              >
                Inspect Multi-Hop Provenance
              </button>
            </div>
          ) : (
            <div style={{ padding: '40px 20px', textAlign: 'center', color: '#64748B', fontSize: '0.82rem' }}>
              Select any graph node on the left to inspect evidence metadata and directed causal links.
            </div>
          )}
        </div>
      </div>

      {/* Explainability Drawer */}
      <ExplainabilityDrawer
        isOpen={isExplainOpen}
        onClose={() => setIsExplainOpen(false)}
        title={selectedNode?.name || 'Knowledge Graph Lineage'}
        metricValue="96.4 Graph Health • 0 Cycles"
      />
    </div>
  );
};
