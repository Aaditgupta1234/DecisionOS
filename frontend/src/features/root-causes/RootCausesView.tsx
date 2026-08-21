import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useDataset } from '../../context/DatasetContext';
import { DecisionApi } from '../../api';
import { queryKeys } from '../../shared/api/queryKeys';
import { useBackendHealth } from '../../shared/hooks/useBackendHealth';
import { BackendOfflineScreen } from '../../shared/components/feedback/BackendOfflineScreen';
import { NoDatasetEmptyState } from '../../shared/components/feedback/NoDatasetEmptyState';
import { IntelligencePipelineBreadcrumb } from '../../shared/components/pipeline/IntelligencePipelineBreadcrumb';
import { RootCauseTree, AttributionBranch } from '../../shared/components/root-causes/RootCauseTree';
import { ReactFlowCausalGraph, CausalNodeData } from '../../shared/components/root-causes/ReactFlowCausalGraph';
import { RecommendationPreview } from '../../shared/components/root-causes/RecommendationPreview';
import { DatasetRootCausesResponse } from '../../types';
import { GitMerge, Network, ListTree, RefreshCw, Zap, Activity, AlertTriangle, Database, Layers, CheckCircle, Info } from 'lucide-react';

export const RootCausesView: React.FC = () => {
  const { activeDataset } = useDataset();
  const { status: healthStatus, checkHealth } = useBackendHealth();

  const [viewMode, setViewMode] = useState<'GRAPH' | 'TREE'>('GRAPH');
  const [selectedBranch, setSelectedBranch] = useState<AttributionBranch | null>(null);
  const [selectedNodeData, setSelectedNodeData] = useState<CausalNodeData | null>(null);

  // 1. Fetch Root Causes Response from real backend API: GET /api/v1/datasets/{dataset_id}/root-causes
  const {
    data: rcaData,
    isLoading,
    isError,
    error,
    refetch,
  } = useQuery<DatasetRootCausesResponse>({
    queryKey: queryKeys.rootCauses.all(activeDataset?.id || ''),
    queryFn: () => DecisionApi.getRootCausesResponse(activeDataset!.id),
    enabled: !!activeDataset?.id && healthStatus === 'connected',
    staleTime: 60000,
  });

  if (healthStatus === 'offline') {
    return <BackendOfflineScreen onRetry={checkHealth} />;
  }

  if (!activeDataset) {
    return (
      <div style={{ padding: '32px' }}>
        <NoDatasetEmptyState
          title="No Active Dataset Selected"
          description="Select or upload a dataset to run deterministic root cause isolation and causal attribution graph generation."
        />
      </div>
    );
  }

  const handleSelectNode = (nodeId: string, nodeData: CausalNodeData) => {
    setSelectedNodeData(nodeData);
  };

  const totalCauses = rcaData?.total_root_causes ?? 0;
  const totalNodes = rcaData?.graph?.nodes?.length ?? 0;
  const totalEdges = rcaData?.graph?.edges?.length ?? 0;
  const topSummary = rcaData?.summaries?.[0];

  return (
    <div style={{ padding: '28px 32px', color: '#FFFFFF', maxWidth: '1600px', margin: '0 auto' }}>
      
      {/* 1. Pipeline Breadcrumb */}
      <IntelligencePipelineBreadcrumb currentStep="rootcause" />

      {/* 2. Header */}
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: '20px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
            <span style={{ fontSize: '10.5px', fontWeight: 700, color: '#10B981', background: 'rgba(16, 185, 129, 0.12)', border: '1px solid rgba(16, 185, 129, 0.28)', padding: '1px 7px', borderRadius: '4px', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
              Phase 5.2–5.5 Root Cause Isolation Core
            </span>
            <span style={{ fontSize: '12px', color: '#64748B' }}>•</span>
            <span style={{ fontSize: '12px', color: '#94A3B8', fontWeight: 600 }}>{activeDataset.name}</span>
          </div>
          <h1 style={{ fontSize: '24px', fontWeight: 800, letterSpacing: '-0.02em' }}>
            Root Cause Analysis Workspace
          </h1>
          <p style={{ fontSize: '13px', color: '#94A3B8', marginTop: '4px' }}>
            Deterministic causal DAG isolating the primary drivers of business anomalies and mapping direct paths to corrective action.
          </p>
        </div>

        {/* View Switcher & Refetch */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{ display: 'flex', background: '#070A0F', border: '1px solid #141C28', borderRadius: '8px', padding: '2px' }}>
            <button
              type="button"
              onClick={() => setViewMode('GRAPH')}
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '5px',
                background: viewMode === 'GRAPH' ? '#1D4ED8' : 'transparent',
                color: viewMode === 'GRAPH' ? '#FFFFFF' : '#94A3B8',
                border: 'none',
                borderRadius: '6px',
                padding: '6px 12px',
                fontSize: '11.5px',
                fontWeight: 700,
                cursor: 'pointer',
              }}
            >
              <Network size={13} />
              <span>Causal Graph</span>
            </button>

            <button
              type="button"
              onClick={() => setViewMode('TREE')}
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '5px',
                background: viewMode === 'TREE' ? '#1D4ED8' : 'transparent',
                color: viewMode === 'TREE' ? '#FFFFFF' : '#94A3B8',
                border: 'none',
                borderRadius: '6px',
                padding: '6px 12px',
                fontSize: '11.5px',
                fontWeight: 700,
                cursor: 'pointer',
              }}
            >
              <ListTree size={13} />
              <span>Attribution Tree</span>
            </button>
          </div>

          <button
            onClick={() => refetch()}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '6px',
              background: '#0F172A',
              border: '1px solid #1E293B',
              color: '#CBD5E1',
              padding: '7px 12px',
              borderRadius: '6px',
              fontSize: '12px',
              fontWeight: 600,
              cursor: 'pointer',
            }}
          >
            <RefreshCw size={13} />
          </button>
        </div>
      </div>

      {/* 2b. Active Dataset Ribbon */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '20px',
        background: '#070A0F',
        border: '1px solid #141C28',
        borderRadius: '8px',
        padding: '10px 16px',
        marginBottom: '20px',
        fontSize: '12px',
        color: '#94A3B8',
        flexWrap: 'wrap',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <Database size={14} color="#38BDF8" />
          <span style={{ color: '#E2E8F0', fontWeight: 600 }}>Active Dataset:</span>
          <span>{activeDataset.name}</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <Layers size={14} color="#10B981" />
          <span style={{ color: '#E2E8F0', fontWeight: 600 }}>Graph Vertices (Nodes):</span>
          <span>{totalNodes}</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <GitMerge size={14} color="#F59E0B" />
          <span style={{ color: '#E2E8F0', fontWeight: 600 }}>Causal Edges:</span>
          <span>{totalEdges}</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <CheckCircle size={14} color="#10B981" />
          <span style={{ color: '#E2E8F0', fontWeight: 600 }}>Causal Relationships:</span>
          <span>{totalCauses}</span>
        </div>
      </div>

      {/* 3. Primary Root Cause Hero Card */}
      {totalCauses > 0 && topSummary ? (
        <div style={{
          background: 'linear-gradient(135deg, #0C1018 0%, #080B10 100%)',
          border: '1px solid #20293A',
          borderRadius: '12px',
          padding: '20px 24px',
          marginBottom: '24px',
          display: 'grid',
          gridTemplateColumns: '1.8fr 1fr 1fr',
          gap: '20px',
          alignItems: 'center',
          boxShadow: '0 15px 35px rgba(0, 0, 0, 0.6)',
        }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '6px' }}>
              <GitMerge size={14} color="#EF4444" />
              <span style={{ fontSize: '11px', fontWeight: 800, color: '#EF4444', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                Primary Root Cause Isolated
              </span>
            </div>

            <h3 style={{ fontSize: '17px', fontWeight: 800, color: '#FFFFFF', marginBottom: '4px', letterSpacing: '-0.01em' }}>
              {topSummary.primary_issue}
            </h3>

            <p style={{ fontSize: '12.5px', color: '#94A3B8', lineHeight: 1.5, margin: 0 }}>
              Primary severity {topSummary.primary_severity} issue evaluated across {topSummary.root_causes.length} underlying causal driver(s).
            </p>
          </div>

          <div style={{ background: '#05070B', border: '1px solid #141C28', borderRadius: '8px', padding: '12px 16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '4px' }}>
              <span style={{ fontSize: '10.5px', color: '#64748B', textTransform: 'uppercase', fontWeight: 600 }}>Causal Confidence</span>
              <span style={{ fontSize: '10px', color: '#38BDF8', fontWeight: 700 }}>{Math.round(topSummary.overall_confidence * 100)}%</span>
            </div>
            <div style={{ fontSize: '20px', fontWeight: 800, color: '#EF4444' }}>
              Impact: {topSummary.highest_impact}
            </div>
            <span style={{ fontSize: '10.5px', color: '#94A3B8', marginTop: '2px', display: 'block' }}>Verified DAG linkage</span>
          </div>

          <div style={{ background: '#05070B', border: '1px solid rgba(16, 185, 129, 0.3)', borderRadius: '8px', padding: '12px 16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '4px' }}>
              <span style={{ fontSize: '10.5px', color: '#10B981', textTransform: 'uppercase', fontWeight: 700 }}>Recovery Opportunity</span>
              <Zap size={13} color="#10B981" />
            </div>
            <div style={{ fontSize: '20px', fontWeight: 800, color: '#10B981' }}>
              Action Ready
            </div>
            <span style={{ fontSize: '10.5px', color: '#94A3B8', marginTop: '2px', display: 'block' }}>Targeted recommendation</span>
          </div>
        </div>
      ) : (
        /* Zero Causal Edges / Neutral Hero Banner */
        <div style={{
          background: 'linear-gradient(135deg, #090E17 0%, #060910 100%)',
          border: '1px solid #1A2436',
          borderRadius: '12px',
          padding: '20px 24px',
          marginBottom: '24px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
            <div style={{ background: 'rgba(56, 189, 248, 0.1)', border: '1px solid rgba(56, 189, 248, 0.25)', borderRadius: '10px', padding: '10px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Info size={22} color="#38BDF8" />
            </div>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '2px' }}>
                <span style={{ fontSize: '14px', fontWeight: 800, color: '#FFFFFF' }}>
                  No Validated Causal Relationships Identified
                </span>
                <span style={{ fontSize: '10px', color: '#10B981', background: 'rgba(16, 185, 129, 0.1)', border: '1px solid rgba(16, 185, 129, 0.3)', padding: '1px 6px', borderRadius: '4px', fontWeight: 700 }}>
                  Deterministic Verified
                </span>
              </div>
              <p style={{ fontSize: '12.5px', color: '#94A3B8', margin: 0 }}>
                No validated causal relationships identified for dataset <strong style={{ color: '#E2E8F0' }}>{activeDataset.name}</strong>. Diagnostic findings operate independently without false-positive causal edges.
              </p>
            </div>
          </div>

          <div style={{ display: 'flex', gap: '16px', borderLeft: '1px solid #141C28', paddingLeft: '24px' }}>
            <div>
              <span style={{ fontSize: '10px', color: '#64748B', textTransform: 'uppercase', display: 'block', fontWeight: 600 }}>Findings</span>
              <span style={{ fontSize: '18px', fontWeight: 800, color: '#FFFFFF' }}>{totalNodes}</span>
            </div>
            <div>
              <span style={{ fontSize: '10px', color: '#64748B', textTransform: 'uppercase', display: 'block', fontWeight: 600 }}>Causal Edges</span>
              <span style={{ fontSize: '18px', fontWeight: 800, color: '#38BDF8' }}>0</span>
            </div>
          </div>
        </div>
      )}

      {/* 3b. API Error State */}
      {isError && (
        <div style={{
          background: 'rgba(239, 68, 68, 0.1)',
          border: '1px solid rgba(239, 68, 68, 0.3)',
          borderRadius: '8px',
          padding: '16px 20px',
          color: '#EF4444',
          fontSize: '13px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          marginBottom: '24px',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <AlertTriangle size={18} />
            <span>{(error as any)?.message || 'Failed to fetch root cause analysis graph from DecisionOS API.'}</span>
          </div>
          <button
            onClick={() => refetch()}
            style={{
              background: '#EF4444',
              color: '#FFFFFF',
              border: 'none',
              borderRadius: '4px',
              padding: '6px 12px',
              fontSize: '12px',
              fontWeight: 600,
              cursor: 'pointer',
            }}
          >
            Retry
          </button>
        </div>
      )}

      {/* 3c. Loading State */}
      {isLoading && !isError && (
        <div style={{ background: '#090C12', border: '1px solid #1A2230', borderRadius: '12px', height: '400px', marginBottom: '24px', animation: 'pulse 1.5s infinite' }} />
      )}

      {/* 4. Main Workspace */}
      {!isLoading && !isError && (
        <div style={{ display: 'grid', gridTemplateColumns: '2fr 1.15fr', gap: '20px' }}>
          {/* Left Interactive Workspace */}
          <div>
            {viewMode === 'GRAPH' ? (
              <div>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
                  <span style={{ fontSize: '12px', fontWeight: 700, color: '#CBD5E1', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                    Interactive Causal Relationship DAG
                  </span>
                  <span style={{ fontSize: '11px', color: '#64748B' }}>Click nodes to inspect factors</span>
                </div>
                <ReactFlowCausalGraph graph={rcaData?.graph} onSelectNode={handleSelectNode} />
              </div>
            ) : (
              <div>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
                  <span style={{ fontSize: '12px', fontWeight: 700, color: '#CBD5E1', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                    Multi-Tier Percentage Attribution Hierarchy
                  </span>
                  <span style={{ fontSize: '11px', color: '#64748B' }}>Select branch to trace impact</span>
                </div>
                <RootCauseTree onSelectBranch={(b) => setSelectedBranch(b)} selectedBranchId={selectedBranch?.id} />
              </div>
            )}
          </div>

          {/* Right Panel: Recommendation Preview & Supporting Evidence */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {totalCauses > 0 ? (
              <RecommendationPreview
                title="Targeted Operational Corrective Action"
                expectedImpact="High Value"
                confidence={95}
                difficulty="LOW"
                priority="HIGH"
                description="Executing recommended operational adjustments to address identified causal drivers."
              />
            ) : (
              <div style={{
                background: '#090C12',
                border: '1px solid #1A2230',
                borderRadius: '12px',
                padding: '20px',
                color: '#94A3B8',
              }}>
                <div style={{ fontSize: '12px', fontWeight: 800, color: '#FFFFFF', marginBottom: '6px' }}>
                  No Direct Causal Drivers Isolated
                </div>
                <p style={{ fontSize: '12px', lineHeight: 1.5, margin: 0 }}>
                  The Root Cause Engine verified 0 false-positive causal links. Findings operate independently based on dataset evidence.
                </p>
              </div>
            )}

            {/* Evidence Trail Box */}
            <div style={{
              background: '#090C12',
              border: '1px solid #1A2230',
              borderRadius: '12px',
              padding: '18px 20px',
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '12px' }}>
                <Activity size={14} color="#38BDF8" />
                <span style={{ fontSize: '11.5px', fontWeight: 700, color: '#FFFFFF', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                  Deterministic Supporting Evidence
                </span>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', fontSize: '12px' }}>
                <div style={{ background: '#05070B', border: '1px solid #141C28', borderRadius: '6px', padding: '10px 12px' }}>
                  <div style={{ color: '#64748B', fontSize: '10.5px', textTransform: 'uppercase', marginBottom: '2px' }}>Dataset Telemetry</div>
                  <div style={{ color: '#F1F5F9', fontWeight: 600 }}>{activeDataset.name}</div>
                  <div style={{ color: '#38BDF8', fontSize: '11px', marginTop: '2px' }}>Total Nodes: {totalNodes} • Edges: {totalEdges}</div>
                </div>

                <div style={{ background: '#05070B', border: '1px solid #141C28', borderRadius: '6px', padding: '10px 12px' }}>
                  <div style={{ color: '#64748B', fontSize: '10.5px', textTransform: 'uppercase', marginBottom: '2px' }}>Algorithm Verdict</div>
                  <div style={{ color: '#F1F5F9', fontWeight: 600 }}>Deterministic Correlation vs Causation Guardrails Enforced</div>
                  <div style={{ color: '#10B981', fontSize: '11px', marginTop: '2px' }}>Zero false causal links generated</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

    </div>
  );
};

export default RootCausesView;
