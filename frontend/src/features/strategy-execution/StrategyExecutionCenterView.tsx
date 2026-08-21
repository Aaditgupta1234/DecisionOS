import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useDataset } from '../../context/DatasetContext';
import { DecisionApi } from '../../api';
import { queryKeys } from '../../shared/api/queryKeys';
import { useBackendHealth } from '../../shared/hooks/useBackendHealth';
import { BackendOfflineScreen } from '../../shared/components/feedback/BackendOfflineScreen';
import { NoDatasetEmptyState } from '../../shared/components/feedback/NoDatasetEmptyState';
import { IntelligencePipelineBreadcrumb } from '../../shared/components/pipeline/IntelligencePipelineBreadcrumb';
import { StrategyPlan, StrategyActionItem, StrategicPriorityItem, StrategyMilestoneItem, SuccessCriterionItem } from '../../types';
import {
  Target,
  TrendingUp,
  ShieldCheck,
  CheckCircle2,
  AlertTriangle,
  Clock,
  ArrowUpRight,
  Layers,
  Sparkles,
  GitMerge,
  BarChart3,
  Award,
  Users,
  RefreshCw,
  Rocket,
  CheckSquare
} from 'lucide-react';
import { Link } from 'react-router-dom';

export const StrategyExecutionCenterView: React.FC = () => {
  const { activeDataset } = useDataset();
  const { status: healthStatus, checkHealth } = useBackendHealth();
  const [filterHorizon, setFilterHorizon] = useState<string>('ALL');

  // Fetch Strategy Plan from backend API: GET /api/v1/datasets/{dataset_id}/strategy/latest
  const {
    data: strategyData,
    isLoading,
    isError,
    error,
    refetch,
  } = useQuery<StrategyPlan>({
    queryKey: queryKeys.strategyExecution.initiatives(activeDataset?.id || ''),
    queryFn: () => DecisionApi.getLatestStrategy(activeDataset!.id),
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
          description="Select or upload a dataset to view dynamic strategy execution initiatives."
        />
      </div>
    );
  }

  if (isLoading) {
    return (
      <div style={{ padding: '32px', color: '#FFFFFF', maxWidth: '1600px', margin: '0 auto' }}>
        <IntelligencePipelineBreadcrumb currentStep="recommendations" />
        <div style={{ padding: '60px 20px', textAlign: 'center', background: '#090D14', border: '1px solid #1E293B', borderRadius: '12px' }}>
          <RefreshCw size={28} color="#38BDF8" style={{ animation: 'spin 1s linear infinite', marginBottom: '12px' }} />
          <div style={{ fontSize: '1rem', fontWeight: 700, color: '#F1F5F9' }}>Loading Strategy Execution Roster...</div>
          <div style={{ fontSize: '0.8rem', color: '#64748B', marginTop: '4px' }}>Compiling active execution plan initiatives for {activeDataset.name}</div>
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <div style={{ padding: '32px', color: '#FFFFFF', maxWidth: '1600px', margin: '0 auto' }}>
        <IntelligencePipelineBreadcrumb currentStep="recommendations" />
        <div style={{ padding: '40px 24px', background: 'rgba(239, 68, 68, 0.08)', border: '1px solid rgba(239, 68, 68, 0.3)', borderRadius: '12px', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '12px' }}>
          <AlertTriangle size={32} color="#EF4444" />
          <div style={{ fontSize: '1.1rem', fontWeight: 800, color: '#F87171' }}>Unable to Load Strategy Execution Plan</div>
          <div style={{ fontSize: '0.82rem', color: '#94A3B8', textAlign: 'center', maxWidth: '500px' }}>
            {(error as any)?.message || 'An error occurred while communicating with the Strategy Execution Engine.'}
          </div>
          <button
            type="button"
            onClick={() => refetch()}
            style={{
              padding: '8px 16px',
              background: '#DC2626',
              color: '#FFFFFF',
              border: 'none',
              borderRadius: '6px',
              fontWeight: 700,
              fontSize: '0.8rem',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              marginTop: '8px'
            }}
          >
            <RefreshCw size={14} /> Retry Query
          </button>
        </div>
      </div>
    );
  }

  const actionItems: StrategyActionItem[] = strategyData?.action_items || [];
  const milestones: StrategyMilestoneItem[] = strategyData?.milestones || [];
  const successCriteria: SuccessCriterionItem[] = strategyData?.success_criteria || [];
  const priorities: StrategicPriorityItem[] = strategyData?.strategic_priorities || [];

  if (!strategyData || actionItems.length === 0) {
    return (
      <div style={{ padding: '32px', color: '#FFFFFF', maxWidth: '1600px', margin: '0 auto' }}>
        <IntelligencePipelineBreadcrumb currentStep="recommendations" />
        <div style={{ padding: '60px 24px', textAlign: 'center', background: '#090D14', border: '1px solid #1E293B', borderRadius: '12px', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '12px' }}>
          <Rocket size={36} color="#64748B" />
          <div style={{ fontSize: '1.1rem', fontWeight: 800, color: '#F1F5F9' }}>No strategic initiatives available for this dataset.</div>
          <div style={{ fontSize: '0.82rem', color: '#64748B', maxWidth: '480px' }}>
            Active Dataset: <strong style={{ color: '#38BDF8' }}>{activeDataset.name}</strong>. No strategy execution plan has been calculated for this telemetry context yet.
          </div>
        </div>
      </div>
    );
  }

  const filteredActions = filterHorizon === 'ALL'
    ? actionItems
    : actionItems.filter((item: StrategyActionItem) => item.time_horizon === filterHorizon);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', paddingBottom: '40px', maxWidth: '1600px', margin: '0 auto' }}>
      {/* 1. Breadcrumb Navigation */}
      <IntelligencePipelineBreadcrumb currentStep="recommendations" />

      {/* 2. Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
            <span style={{ fontSize: '10.5px', fontWeight: 700, color: '#10B981', background: 'rgba(16, 185, 129, 0.12)', border: '1px solid rgba(16, 185, 129, 0.28)', padding: '1px 7px', borderRadius: '4px', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
              Phase 6.2 Strategy Realization Engine
            </span>
            <span style={{ fontSize: '12px', color: '#64748B' }}>•</span>
            <span style={{ fontSize: '12px', color: '#94A3B8', fontWeight: 600 }}>{activeDataset.name}</span>
          </div>
          <h1 style={{ fontSize: '1.8rem', fontWeight: 900, color: '#FFFFFF', margin: '4px 0 0 0' }}>
            Strategy Execution & Benefits Realization Command Center
          </h1>
        </div>

        {/* Status Pill */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', background: 'rgba(16, 185, 129, 0.15)', border: '1px solid rgba(16, 185, 129, 0.3)', padding: '6px 14px', borderRadius: '20px' }}>
          <CheckCircle2 size={14} color="#10B981" />
          <span style={{ fontSize: '0.78rem', color: '#10B981', fontWeight: 800 }}>
            Plan Version: {strategyData.plan_version || 'v1.0'} ({strategyData.status || 'ACTIVE'})
          </span>
        </div>
      </div>

      {/* 3. 4 Dynamic Hero Metric Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '16px' }}>
        {/* Widget 1: Action Items */}
        <div style={{ background: '#090D14', border: '1px solid #1E293B', borderRadius: '14px', padding: '20px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <span style={{ fontSize: '0.72rem', color: '#64748B', fontWeight: 800, textTransform: 'uppercase' }}>ACTION ITEMS</span>
            <Target size={18} color="#38BDF8" />
          </div>
          <div style={{ fontSize: '2.2rem', fontWeight: 900, color: '#FFFFFF' }}>{actionItems.length} Initiatives</div>
          <div style={{ fontSize: '0.78rem', color: '#38BDF8', fontWeight: 700 }}>
            Traceable Execution Actions
          </div>
        </div>

        {/* Widget 2: Strategic Priorities */}
        <div style={{ background: '#090D14', border: '1px solid #1E293B', borderRadius: '14px', padding: '20px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <span style={{ fontSize: '0.72rem', color: '#64748B', fontWeight: 800, textTransform: 'uppercase' }}>STRATEGIC PRIORITIES</span>
            <TrendingUp size={18} color="#10B981" />
          </div>
          <div style={{ fontSize: '2.2rem', fontWeight: 900, color: '#10B981' }}>{priorities.length} Focus Areas</div>
          <div style={{ fontSize: '0.78rem', color: '#10B981', fontWeight: 800 }}>
            Phased Operational Focus
          </div>
        </div>

        {/* Widget 3: Milestones */}
        <div style={{ background: '#090D14', border: '1px solid #1E293B', borderRadius: '14px', padding: '20px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <span style={{ fontSize: '0.72rem', color: '#64748B', fontWeight: 800, textTransform: 'uppercase' }}>ROADMAP MILESTONES</span>
            <Sparkles size={18} color="#F59E0B" />
          </div>
          <div style={{ fontSize: '2.2rem', fontWeight: 900, color: '#F59E0B' }}>{milestones.length} Checkpoints</div>
          <div style={{ fontSize: '0.78rem', color: '#94A3B8', fontWeight: 700 }}>
            30 / 60 / 90-Day Execution Windows
          </div>
        </div>

        {/* Widget 4: Success Criteria */}
        <div style={{ background: '#090D14', border: '1px solid #1E293B', borderRadius: '14px', padding: '20px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <span style={{ fontSize: '0.72rem', color: '#64748B', fontWeight: 800, textTransform: 'uppercase' }}>SUCCESS CRITERIA</span>
            <ShieldCheck size={18} color="#A855F7" />
          </div>
          <div style={{ fontSize: '2.2rem', fontWeight: 900, color: '#A855F7' }}>{successCriteria.length} Grounded KPIs</div>
          <div style={{ fontSize: '0.78rem', color: '#10B981', fontWeight: 700 }}>
            Deterministic Target Metrics
          </div>
        </div>
      </div>

      {/* 4. Filter Tabs */}
      <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
        {['ALL', 'IMMEDIATE', '30_DAYS', '60_DAYS', '90_DAYS'].map((horizon) => (
          <button
            key={horizon}
            type="button"
            onClick={() => setFilterHorizon(horizon)}
            style={{
              padding: '6px 14px',
              borderRadius: '8px',
              border: 'none',
              background: filterHorizon === horizon ? '#0284C7' : 'rgba(15, 23, 42, 0.8)',
              color: '#FFFFFF',
              fontSize: '0.78rem',
              fontWeight: 700,
              cursor: 'pointer',
            }}
          >
            {horizon}
          </button>
        ))}
      </div>

      {/* 5. Strategic Initiatives Table */}
      <div style={{ background: '#090D14', border: '1px solid #1E293B', borderRadius: '14px', overflow: 'hidden' }}>
        <div style={{ padding: '16px 20px', borderBottom: '1px solid #1E293B', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <span style={{ fontSize: '0.88rem', fontWeight: 800, color: '#FFFFFF' }}>Strategic Action Items Roster</span>
          <span style={{ fontSize: '0.75rem', color: '#64748B' }}>Showing {filteredActions.length} Initiatives</span>
        </div>

        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.82rem' }}>
            <thead>
              <tr style={{ background: 'rgba(15, 23, 42, 0.6)', color: '#64748B', borderBottom: '1px solid #1E293B' }}>
                <th style={{ padding: '12px 16px' }}>CODE</th>
                <th style={{ padding: '12px 16px' }}>INITIATIVE & OPERATIONAL DETAILS</th>
                <th style={{ padding: '12px 16px' }}>TIME HORIZON</th>
                <th style={{ padding: '12px 16px' }}>PREREQUISITES</th>
              </tr>
            </thead>
            <tbody>
              {filteredActions.map((item: StrategyActionItem, idx: number) => (
                <tr key={idx} style={{ borderBottom: '1px solid #1E293B' }}>
                  <td style={{ padding: '14px 16px', fontWeight: 800, color: '#38BDF8' }}>
                    INIT-{String(idx + 1).padStart(3, '0')}
                  </td>
                  <td style={{ padding: '14px 16px' }}>
                    <div style={{ fontWeight: 800, color: '#FFFFFF', marginBottom: '2px' }}>{item.title}</div>
                    <div style={{ fontSize: '0.74rem', color: '#94A3B8' }}>{item.description}</div>
                  </td>
                  <td style={{ padding: '14px 16px' }}>
                    <span
                      style={{
                        fontSize: '0.7rem',
                        fontWeight: 800,
                        padding: '3px 8px',
                        borderRadius: '4px',
                        background: 'rgba(56, 189, 248, 0.15)',
                        color: '#38BDF8',
                      }}
                    >
                      {item.time_horizon}
                    </span>
                  </td>
                  <td style={{ padding: '14px 16px', fontSize: '0.74rem', color: '#94A3B8' }}>
                    {item.dependencies && item.dependencies.length > 0 ? item.dependencies.join(', ') : 'None'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default StrategyExecutionCenterView;

