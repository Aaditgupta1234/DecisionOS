import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useDataset } from '../../context/DatasetContext';
import { DecisionApi } from '../../api';
import { queryKeys } from '../../shared/api/queryKeys';
import { useBackendHealth } from '../../shared/hooks/useBackendHealth';
import { BackendOfflineScreen } from '../../shared/components/feedback/BackendOfflineScreen';
import { NoDatasetEmptyState } from '../../shared/components/feedback/NoDatasetEmptyState';
import { IntelligencePipelineBreadcrumb } from '../../shared/components/pipeline/IntelligencePipelineBreadcrumb';
import { PriorityRankingBanner, PriorityItem } from '../../shared/components/recommendations/PriorityRankingBanner';
import { RecommendationCard } from '../../shared/components/recommendations/RecommendationCard';
import { RecommendationDrawer } from '../../shared/components/recommendations/RecommendationDrawer';
import { Recommendation } from '../../types';
import { AlertTriangle, Search, RefreshCw, Database, Layers, CheckCircle } from 'lucide-react';

export const RecommendationsView: React.FC = () => {
  const { activeDataset } = useDataset();
  const { status: healthStatus, checkHealth } = useBackendHealth();

  const [selectedPriority, setSelectedPriority] = useState<string>('ALL');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [activeDrawerId, setActiveDrawerId] = useState<string | null>(null);

  // 1. Fetch Recommendations from real API: GET /api/v1/datasets/{dataset_id}/recommendations
  const {
    data: recsData,
    isLoading,
    isError,
    error,
    refetch,
  } = useQuery<Recommendation[]>({
    queryKey: queryKeys.recommendations.all(activeDataset?.id || ''),
    queryFn: async () => {
      const res = await DecisionApi.listRecommendations(activeDataset!.id);
      if (Array.isArray(res)) return res;
      if (res && Array.isArray((res as any).recommendations)) return (res as any).recommendations;
      return [];
    },
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
          description="Select or upload a dataset to generate prioritized business recommendations and ROI recovery roadmaps."
        />
      </div>
    );
  }

  const rawRecs = Array.isArray(recsData) ? recsData : [];

  // Filter & Search
  const filtered = rawRecs.filter((r) => {
    const matchesPriority = selectedPriority === 'ALL' || r.priority === selectedPriority;
    const matchesSearch =
      r.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (r.action_summary || '').toLowerCase().includes(searchQuery.toLowerCase()) ||
      (r.description || '').toLowerCase().includes(searchQuery.toLowerCase()) ||
      (r.why_recommended || '').toLowerCase().includes(searchQuery.toLowerCase());
    return matchesPriority && matchesSearch;
  });

  // Selected item for drawer
  const selectedRecRaw = rawRecs.find((r) => r.id === activeDrawerId) || rawRecs[0];

  const selectedRecDrawerData = selectedRecRaw ? {
    id: selectedRecRaw.id,
    title: selectedRecRaw.title,
    actionSummary: selectedRecRaw.description || selectedRecRaw.action_summary || selectedRecRaw.why_recommended || '',
    whyRecommended: selectedRecRaw.why_recommended,
    priority: selectedRecRaw.priority,
    difficulty: (selectedRecRaw as any).estimated_effort_score > 0.6 ? 'HIGH' : (selectedRecRaw as any).estimated_effort_score > 0.3 ? 'MEDIUM' : 'LOW',
    confidence: Math.round(((selectedRecRaw as any).confidence_score ?? (selectedRecRaw as any).confidence ?? 0.9) * 100),
    expectedRecovery: (selectedRecRaw as any).outcomes?.target !== undefined
      ? `Goal: ${(selectedRecRaw as any).outcomes?.target}`
      : selectedRecRaw.expected_impact || '+$150K ARR',
    status: selectedRecRaw.status,
    expectedMetric: (selectedRecRaw as any).outcomes?.expected_metric || (selectedRecRaw.affected_metric_keys?.[0] ? selectedRecRaw.affected_metric_keys[0].replace(/_/g, ' ').toUpperCase() : 'Total Revenue'),
    baseline: (selectedRecRaw as any).outcomes?.baseline,
    target: (selectedRecRaw as any).outcomes?.target,
    measurementPeriod: (selectedRecRaw as any).outcomes?.measurement_period || '90 days',
    actionPlan: (selectedRecRaw as any).action_plan || [],
    evidence: (selectedRecRaw as any).evidence || {},
  } : undefined;

  // Map top 3 items for PriorityRankingBanner
  const top3PriorityItems: PriorityItem[] = rawRecs.slice(0, 3).map((r, idx) => ({
    id: r.id,
    rank: idx + 1,
    title: r.title,
    recoveryARR: (r as any).outcomes?.target !== undefined
      ? `Target: ${(r as any).outcomes.target}`
      : r.expected_impact || '+$150K ARR',
    priority: (r.priority === 'CRITICAL' || r.priority === 'HIGH') ? (r.priority as any) : 'MEDIUM',
    difficulty: ((r as any).estimated_effort_score > 0.6 ? 'HIGH' : (r as any).estimated_effort_score > 0.3 ? 'MEDIUM' : 'LOW') as any,
    confidence: Math.round(((r as any).confidence_score ?? (r as any).confidence ?? 0.9) * 100),
  }));

  return (
    <div style={{ padding: '28px 32px', color: '#FFFFFF', maxWidth: '1600px', margin: '0 auto' }}>
      
      {/* 1. Pipeline Breadcrumb */}
      <IntelligencePipelineBreadcrumb currentStep="recommendations" />

      {/* 2. Header & Action */}
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: '20px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
            <span style={{ fontSize: '10.5px', fontWeight: 700, color: '#10B981', background: 'rgba(16, 185, 129, 0.12)', border: '1px solid rgba(16, 185, 129, 0.28)', padding: '1px 7px', borderRadius: '4px', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
              Phase 6 Decision Engine
            </span>
            <span style={{ fontSize: '12px', color: '#64748B' }}>•</span>
            <span style={{ fontSize: '12px', color: '#94A3B8', fontWeight: 600 }}>{activeDataset.name}</span>
          </div>
          <h1 style={{ fontSize: '24px', fontWeight: 800, letterSpacing: '-0.02em' }}>
            Recommendations & Action Center
          </h1>
          <p style={{ fontSize: '13px', color: '#94A3B8', marginTop: '4px' }}>
            Deterministic corrective actions ranked by ROI potential, feasibility, and target milestone recovery.
          </p>
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
            padding: '7px 14px',
            borderRadius: '6px',
            fontSize: '12px',
            fontWeight: 600,
            cursor: 'pointer',
          }}
        >
          <RefreshCw size={13} />
          <span>Regenerate Actions</span>
        </button>
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
          <span style={{ color: '#E2E8F0', fontWeight: 600 }}>Total Records:</span>
          <span>{(activeDataset as any).record_count ?? activeDataset.row_count ?? 12}</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <Layers size={14} color="#F59E0B" />
          <span style={{ color: '#E2E8F0', fontWeight: 600 }}>Total Columns:</span>
          <span>{(activeDataset as any).column_count ?? activeDataset.columns?.length ?? 10}</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <CheckCircle size={14} color="#10B981" />
          <span style={{ color: '#E2E8F0', fontWeight: 600 }}>Recommendations Evaluated:</span>
          <span>{rawRecs.length}</span>
        </div>
      </div>

      {/* 3. Executive Priority Ranking Top 3 Strip */}
      {!isLoading && !isError && top3PriorityItems.length > 0 && (
        <PriorityRankingBanner items={top3PriorityItems} onSelectAction={(item) => setActiveDrawerId(item.id)} />
      )}

      {/* 4. Filter Toolbar & Search */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px', flexWrap: 'wrap', gap: '12px' }}>
        <div style={{ display: 'flex', gap: '6px', background: '#070A0F', border: '1px solid #141C28', borderRadius: '8px', padding: '3px' }}>
          {['ALL', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'].map((p) => (
            <button
              key={p}
              type="button"
              onClick={() => setSelectedPriority(p)}
              style={{
                background: selectedPriority === p ? '#1D4ED8' : 'transparent',
                color: selectedPriority === p ? '#FFFFFF' : '#94A3B8',
                border: 'none',
                borderRadius: '6px',
                padding: '6px 12px',
                fontSize: '11.5px',
                fontWeight: selectedPriority === p ? 700 : 500,
                cursor: 'pointer',
              }}
            >
              {p === 'ALL' ? 'All Priorities' : `${p} Priority`}
            </button>
          ))}
        </div>

        <div style={{ position: 'relative', width: '260px' }}>
          <Search size={14} color="#64748B" style={{ position: 'absolute', left: '10px', top: '50%', transform: 'translateY(-50%)' }} />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search recommendations..."
            style={{
              width: '100%',
              background: '#070A0F',
              border: '1px solid #1A2230',
              borderRadius: '6px',
              padding: '6px 10px 6px 32px',
              fontSize: '12px',
              color: '#FFFFFF',
              outline: 'none',
              boxSizing: 'border-box',
            }}
          />
        </div>
      </div>

      {/* 5. API Error State */}
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
            <span>{(error as any)?.message || 'Failed to fetch recommendations from DecisionOS API.'}</span>
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

      {/* 6. Loading State */}
      {isLoading && !isError && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginBottom: '28px' }}>
          {[1, 2, 3].map((i) => (
            <div key={i} style={{ background: '#090C12', border: '1px solid #1A2230', borderRadius: '10px', height: '120px', animation: 'pulse 1.5s infinite' }} />
          ))}
        </div>
      )}

      {/* 7. Empty State (Zero Recommendations) */}
      {!isLoading && !isError && filtered.length === 0 && (
        <div style={{
          background: '#070A0F',
          border: '1px dashed #1E293B',
          borderRadius: '12px',
          padding: '48px',
          textAlign: 'center',
          color: '#94A3B8',
          marginBottom: '28px',
        }}>
          <h3 style={{ fontSize: '16px', color: '#E2E8F0', marginBottom: '8px' }}>
            {rawRecs.length === 0 ? 'No Recommendations Prescribed' : 'No Matching Recommendations'}
          </h3>
          <p style={{ fontSize: '13px', maxWidth: '440px', margin: '0 auto 16px' }}>
            {rawRecs.length === 0
              ? 'No corrective actions were triggered for this dataset.'
              : `No recommendations matching filter "${searchQuery}".`}
          </p>
        </div>
      )}

      {/* 8. Recommendation Cards List */}
      {!isLoading && !isError && filtered.length > 0 && (
        <div>
          {filtered.map((rec) => {
            const confPct = Math.round(((rec as any).confidence_score ?? (rec as any).confidence ?? 0.9) * 100);
            const effortScore = (rec as any).estimated_effort_score ?? 0.5;
            const diffStr = effortScore > 0.6 ? 'HIGH' : effortScore > 0.3 ? 'MEDIUM' : 'LOW';
            const recoveryStr = (rec as any).outcomes?.target !== undefined
              ? `Target: ${(rec as any).outcomes.target}`
              : rec.expected_impact || '+$150K ARR';

            const summaryStr = rec.description || rec.action_summary || rec.why_recommended || '';
            const ttvStr = rec.time_to_value ? rec.time_to_value.replace(/_/g, ' ') : ((rec as any).expected_time_to_value ? String((rec as any).expected_time_to_value).replace(/_/g, ' ') : '90 days');

            return (
              <RecommendationCard
                key={rec.id}
                id={rec.id}
                title={rec.title}
                actionSummary={summaryStr}
                priority={rec.priority}
                difficulty={diffStr as any}
                confidence={confPct}
                expectedRecovery={recoveryStr}
                status={rec.status}
                timeToValue={ttvStr}
                onOpenDrawer={(id) => setActiveDrawerId(id)}
              />
            );
          })}
        </div>
      )}

      {/* 9. Slide-Over Recommendation Details Drawer */}
      <RecommendationDrawer
        isOpen={!!activeDrawerId}
        onClose={() => setActiveDrawerId(null)}
        recommendation={selectedRecDrawerData}
      />

    </div>
  );
};

export default RecommendationsView;
