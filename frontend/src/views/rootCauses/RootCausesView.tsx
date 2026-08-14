import React, { useEffect, useState } from 'react';
import { useDataset } from '../../context/DatasetContext';
import { DecisionApi } from '../../api';
import {
  DatasetRootCausesResponse,
  RootCauseAnalysisRecord,
  CausalGraphNode,
  CausalGraphEdge,
} from '../../types';
import { LayoutNode, LayoutEdge } from '../../components/graph/dagLayout';
import { CausalGraphCanvas } from '../../components/graph/CausalGraphCanvas';
import { GraphControls } from '../../components/graph/GraphControls';
import { NodeDetailDrawer } from '../../components/graph/NodeDetailDrawer';
import { EdgeDetailDrawer } from '../../components/graph/EdgeDetailDrawer';
import { CausalChainExplorer } from '../../components/graph/CausalChainExplorer';
import { LoadingSkeleton } from '../../components/feedback/LoadingSkeleton';
import { ErrorBanner } from '../../components/feedback/ErrorBanner';
import { EmptyState } from '../../components/feedback/EmptyState';
import { GitMerge, LayoutGrid, Network, Info } from 'lucide-react';

export const RootCausesView: React.FC = () => {
  const { activeDataset } = useDataset();
  const [rcaResponse, setRcaResponse] = useState<DatasetRootCausesResponse | null>(null);
  const [viewMode, setViewMode] = useState<'GRAPH' | 'LIST'>('GRAPH');

  // Graph Selection State
  const [selectedNode, setSelectedNode] = useState<LayoutNode | null>(null);
  const [selectedEdge, setSelectedEdge] = useState<LayoutEdge | null>(null);
  const [activeChainNodeIds, setActiveChainNodeIds] = useState<string[]>([]);

  // Graph Controls State
  const [zoom, setZoom] = useState<number>(1.0);
  const [panOffset, setPanOffset] = useState<{ x: number; y: number }>({ x: 20, y: 20 });
  const [selectedSeverity, setSelectedSeverity] = useState<string>('ALL');
  const [selectedCategory, setSelectedCategory] = useState<string>('ALL');
  const [highlightRootsOnly, setHighlightRootsOnly] = useState<boolean>(false);

  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchRootCauses = async (datasetId: string) => {
    try {
      setLoading(true);
      setError(null);
      const res = await DecisionApi.getRootCausesResponse(datasetId);
      setRcaResponse(res);
      setSelectedNode(null);
      setSelectedEdge(null);
      setActiveChainNodeIds([]);
    } catch (err: any) {
      console.error('Failed to load root causes:', err);
      setError(err?.message || 'Could not fetch root cause analyses for this dataset.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (activeDataset?.id) {
      fetchRootCauses(activeDataset.id);
    } else {
      setLoading(false);
    }
  }, [activeDataset?.id]);

  if (!activeDataset) {
    return (
      <div className="page-container">
        <EmptyState
          title="No Active Dataset Selected"
          description="Select a dataset to view its interactive root cause causal graph."
          icon={GitMerge}
        />
      </div>
    );
  }

  const graphNodes = rcaResponse?.graph?.nodes || [];
  const graphEdges = rcaResponse?.graph?.edges || [];
  const analyses = rcaResponse?.analyses || [];
  const summaries = rcaResponse?.summaries || [];

  // Available categories
  const categories = Array.from(new Set(graphNodes.map((n) => n.category).filter(Boolean)));

  const handleSelectNode = (node: LayoutNode | null) => {
    setSelectedNode(node);
    setSelectedEdge(null);
  };

  const handleSelectEdge = (edge: LayoutEdge | null) => {
    setSelectedEdge(edge);
    setSelectedNode(null);
  };

  const handleSelectRelatedNodeId = (nodeId: string) => {
    const target = graphNodes.find((n) => n.id === nodeId);
    if (target) {
      setSelectedNode({
        ...target,
        x: 0,
        y: 0,
        width: 220,
        height: 92,
        rank: 0,
        isRootCause: false,
        isTerminalEffect: false,
      });
      setSelectedEdge(null);
    }
  };

  return (
    <div className="page-container">
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: '20px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
            <span className="badge badge-primary">Phase 5.6 & 7.1 Causal DAG Engine</span>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              Deterministic Topological Graph & Evidence Traversal
            </span>
          </div>
          <h1>Root Cause Investigation Studio</h1>
          <p style={{ marginTop: '4px', fontSize: '0.9rem' }}>
            Explore causal linkages from underlying root drivers to downstream business symptoms without speculation.
          </p>
        </div>

        {/* View Mode Switcher */}
        <div style={{ display: 'flex', gap: '4px', backgroundColor: 'var(--bg-surface-elevated)', padding: '4px', borderRadius: 'var(--radius-md)' }}>
          <button
            onClick={() => setViewMode('GRAPH')}
            className={`btn btn-sm ${viewMode === 'GRAPH' ? 'btn-primary' : 'btn-ghost'}`}
            style={{ gap: '6px' }}
          >
            <Network size={15} />
            <span>Interactive DAG</span>
          </button>
          <button
            onClick={() => setViewMode('LIST')}
            className={`btn btn-sm ${viewMode === 'LIST' ? 'btn-primary' : 'btn-ghost'}`}
            style={{ gap: '6px' }}
          >
            <LayoutGrid size={15} />
            <span>Ranked List</span>
          </button>
        </div>
      </div>

      {error && <ErrorBanner message={error} onRetry={() => fetchRootCauses(activeDataset.id)} />}

      {loading ? (
        <LoadingSkeleton count={4} height="120px" />
      ) : graphNodes.length > 0 ? (
        viewMode === 'GRAPH' ? (
          <div>
            {/* Multi-Hop Causal Chain Breadcrumb Bar */}
            <CausalChainExplorer
              summaries={summaries}
              nodes={graphNodes}
              activeChainNodeIds={activeChainNodeIds}
              onSelectChain={(chain) => setActiveChainNodeIds(chain)}
              onClearChain={() => setActiveChainNodeIds([])}
            />

            {/* Graph Controls Toolbar */}
            <GraphControls
              zoom={zoom}
              onZoomIn={() => setZoom((z) => Math.min(2.5, z + 0.15))}
              onZoomOut={() => setZoom((z) => Math.max(0.4, z - 0.15))}
              onFitView={() => {
                setZoom(0.9);
                setPanOffset({ x: 20, y: 20 });
              }}
              onReset={() => {
                setZoom(1.0);
                setPanOffset({ x: 20, y: 20 });
                setSelectedSeverity('ALL');
                setSelectedCategory('ALL');
                setHighlightRootsOnly(false);
              }}
              selectedCategory={selectedCategory}
              onSelectCategory={setSelectedCategory}
              selectedSeverity={selectedSeverity}
              onSelectSeverity={setSelectedSeverity}
              categories={categories}
              highlightRootsOnly={highlightRootsOnly}
              onToggleRootsOnly={() => setHighlightRootsOnly(!highlightRootsOnly)}
            />

            {/* Canvas & Drawer Layout */}
            <div style={{ display: 'flex', gap: '16px', alignItems: 'flex-start', position: 'relative' }}>
              <div style={{ flex: 1, minWidth: 0 }}>
                <CausalGraphCanvas
                  nodes={graphNodes}
                  edges={graphEdges}
                  selectedNodeId={selectedNode?.id || null}
                  selectedEdgeId={selectedEdge?.id || null}
                  activeChainNodeIds={activeChainNodeIds}
                  onSelectNode={handleSelectNode}
                  onSelectEdge={handleSelectEdge}
                  selectedSeverity={selectedSeverity}
                  selectedCategory={selectedCategory}
                  highlightRootsOnly={highlightRootsOnly}
                  zoom={zoom}
                  panOffset={panOffset}
                  onPanChange={setPanOffset}
                  onZoomChange={setZoom}
                />
              </div>

              {/* Slide-Out Detail Drawers */}
              {selectedNode ? (
                <NodeDetailDrawer
                  node={selectedNode}
                  analyses={analyses}
                  onClose={() => setSelectedNode(null)}
                  onSelectRelatedNodeId={handleSelectRelatedNodeId}
                />
              ) : selectedEdge ? (
                <EdgeDetailDrawer
                  edge={selectedEdge}
                  nodes={graphNodes as any}
                  analyses={analyses}
                  onClose={() => setSelectedEdge(null)}
                />
              ) : (
                /* Default Right Telemetry Panel */
                <div
                  style={{
                    width: '320px',
                    backgroundColor: 'var(--bg-surface-elevated)',
                    border: '1px solid var(--border-default)',
                    borderRadius: 'var(--radius-lg)',
                    padding: '20px',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '14px',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <Info size={16} color="var(--color-primary-light)" />
                    <h4 style={{ fontSize: '0.95rem', color: '#ffffff' }}>Causal Graph Telemetry</h4>
                  </div>
                  <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                    Click on any finding node or causal edge in the graph canvas to inspect statistical evidence, confidence scores, and upstream/downstream ripples.
                  </p>

                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '0.8rem' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 0', borderBottom: '1px solid var(--border-subtle)' }}>
                      <span style={{ color: 'var(--text-muted)' }}>Total Vertices (Findings):</span>
                      <strong style={{ color: '#ffffff' }}>{graphNodes.length}</strong>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 0', borderBottom: '1px solid var(--border-subtle)' }}>
                      <span style={{ color: 'var(--text-muted)' }}>Causal Edges:</span>
                      <strong style={{ color: 'var(--color-primary-light)' }}>{graphEdges.length}</strong>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 0' }}>
                      <span style={{ color: 'var(--text-muted)' }}>Validated Relationships:</span>
                      <strong style={{ color: 'var(--color-success)' }}>{analyses.length}</strong>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        ) : (
          /* Ranked Drivers List View */
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {analyses.map((ana, idx) => (
              <div key={ana.id} className="card-elevated">
                <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: '10px' }}>
                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
                      <span className="badge badge-warning">Causal Driver #{idx + 1}</span>
                      <span className="badge badge-primary">{ana.relationship_type}</span>
                      <span className="badge badge-neutral">Strength: {ana.relationship_strength}</span>
                    </div>
                    <h3 style={{ fontSize: '1.15rem', color: '#ffffff', marginBottom: '4px' }}>
                      {ana.root_cause_finding?.title || 'Root Cause Finding'}
                    </h3>
                    <div style={{ fontSize: '0.85rem', color: 'var(--color-danger)' }}>
                      Triggers: {ana.primary_finding?.title || 'Primary Business Symptom'}
                    </div>
                  </div>

                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                      Confidence: <strong style={{ color: 'var(--color-success)' }}>{(ana.confidence_score * 100).toFixed(0)}%</strong>
                    </div>
                    <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                      Impact: <strong style={{ color: 'var(--color-primary-light)' }}>{(ana.impact_score * 100).toFixed(0)}%</strong>
                    </div>
                  </div>
                </div>

                <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', lineHeight: 1.5, marginTop: '8px' }}>
                  {ana.explanation}
                </p>
              </div>
            ))}
          </div>
        )
      ) : (
        <EmptyState
          title="No Causal Graph Available"
          description="Diagnostic findings for this dataset did not exhibit causal links meeting the deterministic confidence threshold."
          icon={GitMerge}
        />
      )}
    </div>
  );
};
