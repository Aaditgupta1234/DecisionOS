import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useDataset } from '../../context/DatasetContext';
import { DecisionApi } from '../../api';
import { queryKeys } from '../../shared/api/queryKeys';
import { useBackendHealth } from '../../shared/hooks/useBackendHealth';
import { BackendOfflineScreen } from '../../shared/components/feedback/BackendOfflineScreen';
import { NoDatasetEmptyState } from '../../shared/components/feedback/NoDatasetEmptyState';
import { IntelligencePipelineBreadcrumb } from '../../shared/components/pipeline/IntelligencePipelineBreadcrumb';
import { PriorityRankingBanner } from '../../shared/components/recommendations/PriorityRankingBanner';
import { RecoveryWaterfallCard } from '../../shared/components/recommendations/RecoveryWaterfallCard';
import { ImpactDifficultyMatrix } from '../../shared/components/recommendations/ImpactDifficultyMatrix';
import { RecommendationCard } from '../../shared/components/recommendations/RecommendationCard';
import { RecommendationDrawer } from '../../shared/components/recommendations/RecommendationDrawer';
import { Recommendation } from '../../types';
import { CheckCircle2, Search, Filter, RefreshCw, Zap } from 'lucide-react';

export const RecommendationsView: React.FC = () => {
  const { activeDataset } = useDataset();
  const { status: healthStatus, checkHealth } = useBackendHealth();

  const [selectedPriority, setSelectedPriority] = useState<string>('ALL');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [activeDrawerId, setActiveDrawerId] = useState<string | null>(null);

  // 1. Fetch Recommendations
  const { data: recsData, isLoading, refetch } = useQuery<Recommendation[]>({
    queryKey: queryKeys.recommendations.all(activeDataset?.id || ''),
    queryFn: () => DecisionApi.listRecommendations(activeDataset!.id),
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

  const defaultRecommendations = [
    {
      id: 'rec_1',
      title: 'Targeted Win-Back Campaign & Courier SLA Penalties',
      actionSummary: 'Automate personalized discount incentives for the 842 churn-risk customers in southeastern corridors while enforcing courier SLA delivery caps.',
      priority: 'HIGH' as const,
      difficulty: 'LOW' as const,
      confidence: 92,
      expectedRecovery: '+$180K ARR',
      status: 'NOT_STARTED',
      timeToValue: '2–3 weeks',
      rootCauseId: 'rc_1',
      rootCauseTitle: 'Courier Transit Delays in Southeastern Logistics Routes',
      findingId: 'f-1',
    },
    {
      id: 'rec_2',
      title: 'Dynamic Dispatch Load-Balancing Across Secondary Hubs',
      actionSummary: 'Implement automated route leveling to distribute orders from saturated secondary hubs, bringing fulfillment times under 2.8 days.',
      priority: 'HIGH' as const,
      difficulty: 'MEDIUM' as const,
      confidence: 90,
      expectedRecovery: '+$140K ARR',
      status: 'NOT_STARTED',
      timeToValue: '3–4 weeks',
      rootCauseId: 'rc_2',
      rootCauseTitle: 'Secondary Hub Dispatch Backlog & Capacity Saturation',
      findingId: 'f-2',
    },
    {
      id: 'rec_3',
      title: 'Automated Post-Purchase Cross-Sell Recommendation Engine',
      actionSummary: 'Deploy AI-curated product attachment widgets during checkout and post-purchase confirmation emails in Health & Beauty categories.',
      priority: 'MEDIUM' as const,
      difficulty: 'LOW' as const,
      confidence: 88,
      expectedRecovery: '+$85K ARR',
      status: 'NOT_STARTED',
      timeToValue: '1–2 weeks',
      rootCauseId: 'rc_3',
      rootCauseTitle: 'Post-Promo Cross-Sell Disengagement in Beauty Segment',
      findingId: 'f-3',
    },
    {
      id: 'rec_4',
      title: 'One-Click Payment Gateway Integration with Automated Fallbacks',
      actionSummary: 'Eliminate high-ticket checkout drop-offs by adding seamless secondary payment routing and fraud verification pre-checks.',
      priority: 'MEDIUM' as const,
      difficulty: 'LOW' as const,
      confidence: 86,
      expectedRecovery: '+$40K ARR',
      status: 'NOT_STARTED',
      timeToValue: '2 weeks',
      rootCauseId: 'rc_4',
      rootCauseTitle: 'Payment Gateway Verification Latency on High-Ticket Orders',
      findingId: 'f-4',
    },
    {
      id: 'rec_5',
      title: 'Secondary Courier Redundancy Partnership for Northern Corridors',
      actionSummary: 'Contract regional express micro-couriers to handle rural delivery spikes and eliminate seasonal SLA penalties.',
      priority: 'LOW' as const,
      difficulty: 'HIGH' as const,
      confidence: 84,
      expectedRecovery: '+$35K ARR',
      status: 'NOT_STARTED',
      timeToValue: '6–8 weeks',
      rootCauseId: 'rc_5',
      rootCauseTitle: 'Low-Density Route Courier Monopoly',
      findingId: 'f-5',
    },
  ];

  const activeRec = defaultRecommendations.find(r => r.id === activeDrawerId) || defaultRecommendations[0];

  const filtered = defaultRecommendations.filter((r) => {
    const matchesPriority = selectedPriority === 'ALL' || r.priority === selectedPriority;
    const matchesSearch =
      r.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      r.actionSummary.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesPriority && matchesSearch;
  });

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
            Deterministic corrective actions ranked by ROI potential, feasibility, and time-to-value to optimize business health.
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

      {/* 3. Executive Priority Ranking Top 3 Strip */}
      <PriorityRankingBanner onSelectAction={(item) => setActiveDrawerId(item.id)} />

      {/* 4. Financial Recovery Potential Waterfall Bridge */}
      <RecoveryWaterfallCard currentLoss="-$218K / Qtr" netRecovery="+$480K ARR" />

      {/* 5. 4-Quadrant Impact vs Difficulty Matrix */}
      <ImpactDifficultyMatrix onSelectItem={(id) => setActiveDrawerId(id)} />

      {/* 6. Filter Toolbar & Search */}
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

      {/* 7. Recommendation Cards List */}
      <div>
        {filtered.map((rec) => (
          <RecommendationCard
            key={rec.id}
            id={rec.id}
            title={rec.title}
            actionSummary={rec.actionSummary}
            priority={rec.priority}
            difficulty={rec.difficulty}
            confidence={rec.confidence}
            expectedRecovery={rec.expectedRecovery}
            status={rec.status}
            timeToValue={rec.timeToValue}
            onOpenDrawer={(id) => setActiveDrawerId(id)}
          />
        ))}
      </div>

      {/* 8. Slide-Over Recommendation Details Drawer */}
      <RecommendationDrawer
        isOpen={!!activeDrawerId}
        onClose={() => setActiveDrawerId(null)}
        recommendation={activeRec}
      />

    </div>
  );
};

export default RecommendationsView;
