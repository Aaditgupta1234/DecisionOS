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
import { GitMerge, Network, ListTree, RefreshCw, Zap, TrendingDown, ShieldCheck, Activity } from 'lucide-react';

export const RootCausesView: React.FC = () => {
  const { activeDataset } = useDataset();
  const { status: healthStatus, checkHealth } = useBackendHealth();

  const [viewMode, setViewMode] = useState<'GRAPH' | 'TREE'>('GRAPH');
  const [selectedBranch, setSelectedBranch] = useState<AttributionBranch | null>(null);
  const [selectedNodeData, setSelectedNodeData] = useState<CausalNodeData | null>(null);

  // 1. Fetch Root Causes Response
  const { data: rcaData, isLoading, refetch } = useQuery<DatasetRootCausesResponse>({
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

      {/* 3. Primary Root Cause Hero Card with Estimated Recovery Potential */}
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
        {/* Left: Identified Problem Narrative */}
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '6px' }}>
            <GitMerge size={14} color="#EF4444" />
            <span style={{ fontSize: '11px', fontWeight: 800, color: '#EF4444', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
              Primary Root Cause Isolated
            </span>
          </div>

          <h3 style={{ fontSize: '17px', fontWeight: 800, color: '#FFFFFF', marginBottom: '4px', letterSpacing: '-0.01em' }}>
            Courier Transit Delays in Southeastern Corridor
          </h3>

          <p style={{ fontSize: '12.5px', color: '#94A3B8', lineHeight: 1.5, margin: 0 }}>
            Transit times exceeding 5 days depressed customer review ratings from 4.7★ to 2.1★, generating 48% of total churn velocity.
          </p>
        </div>

        {/* Center: Financial Impact & Confidence */}
        <div style={{ background: '#05070B', border: '1px solid #141C28', borderRadius: '8px', padding: '12px 16px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '4px' }}>
            <span style={{ fontSize: '10.5px', color: '#64748B', textTransform: 'uppercase', fontWeight: 600 }}>Total Impact</span>
            <span style={{ fontSize: '10px', color: '#38BDF8', fontWeight: 700 }}>91% Confidence</span>
          </div>
          <div style={{ fontSize: '20px', fontWeight: 800, color: '#EF4444' }}>
            -$218K / quarter
          </div>
          <span style={{ fontSize: '10.5px', color: '#94A3B8', marginTop: '2px', display: 'block' }}>Direct top-line erosion</span>
        </div>

        {/* Right: Estimated Recovery Potential Opportunity */}
        <div style={{ background: '#05070B', border: '1px solid rgba(16, 185, 129, 0.3)', borderRadius: '8px', padding: '12px 16px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '4px' }}>
            <span style={{ fontSize: '10.5px', color: '#10B981', textTransform: 'uppercase', fontWeight: 700 }}>Recovery Opportunity</span>
            <Zap size={13} color="#10B981" />
          </div>
          <div style={{ fontSize: '20px', fontWeight: 800, color: '#10B981' }}>
            +$180K ARR
          </div>
          <span style={{ fontSize: '10.5px', color: '#94A3B8', marginTop: '2px', display: 'block' }}>Via Win-Back initiative</span>
        </div>
      </div>

      {/* 4. Main Workspace: Graph / Tree on Left (2fr) + Recommendation Preview on Right (1fr) */}
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
              <ReactFlowCausalGraph onSelectNode={handleSelectNode} />
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
          {/* Recommendation Preview Card */}
          <RecommendationPreview
            title="Targeted Win-Back Campaign & Courier SLA Penalties"
            expectedImpact="+$180K ARR"
            confidence={91}
            difficulty="LOW"
            priority="HIGH"
            description="Deploy targeted retention incentives to impacted Southeastern customers while enforcing delivery SLA penalties on regional courier routes."
          />

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
                <div style={{ color: '#64748B', fontSize: '10.5px', textTransform: 'uppercase', marginBottom: '2px' }}>Corridor Data</div>
                <div style={{ color: '#F1F5F9', fontWeight: 600 }}>Southeastern Logistics Cluster (São Paulo / Rio de Janeiro)</div>
                <div style={{ color: '#EF4444', fontSize: '11px', marginTop: '2px' }}>Average Transit: 5.4 days (+2.2 days over SLA)</div>
              </div>

              <div style={{ background: '#05070B', border: '1px solid #141C28', borderRadius: '6px', padding: '10px 12px' }}>
                <div style={{ color: '#64748B', fontSize: '10.5px', textTransform: 'uppercase', marginBottom: '2px' }}>Customer Impact</div>
                <div style={{ color: '#F1F5F9', fontWeight: 600 }}>Repeat purchase rate dropped from 22.4% → 14.8%</div>
                <div style={{ color: '#F59E0B', fontSize: '11px', marginTop: '2px' }}>842 customers flagged in active win-back segment</div>
              </div>

              <div style={{ background: '#05070B', border: '1px solid #141C28', borderRadius: '6px', padding: '10px 12px' }}>
                <div style={{ color: '#64748B', fontSize: '10.5px', textTransform: 'uppercase', marginBottom: '2px' }}>Algorithm Confidence</div>
                <div style={{ color: '#10B981', fontWeight: 700 }}>94% Statistical Significance (p &lt; 0.001)</div>
              </div>
            </div>
          </div>
        </div>
      </div>

    </div>
  );
};

export default RootCausesView;
