import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useDataset } from '../../context/DatasetContext';
import { DecisionApi } from '../../api';
import { queryKeys } from '../../shared/api/queryKeys';
import { useBackendHealth } from '../../shared/hooks/useBackendHealth';
import { BackendOfflineScreen } from '../../shared/components/feedback/BackendOfflineScreen';
import { NoDatasetEmptyState } from '../../shared/components/feedback/NoDatasetEmptyState';
import { IntelligencePipelineBreadcrumb } from '../../shared/components/pipeline/IntelligencePipelineBreadcrumb';
import { ExplainabilityDrawer } from '../../components/workspace/ExplainabilityDrawer';
import {
  CheckCircle2,
  AlertTriangle,
  RefreshCw,
  Bot,
  Sparkles,
  Layers,
  ShieldCheck,
  ArrowRight,
  Clock,
  Target,
  FileText,
  CheckSquare,
  ChevronRight,
  Database
} from 'lucide-react';

import { StrategyPlan, StrategicPriorityItem, StrategyActionItem } from '../../types';

export const DecisionCopilotView: React.FC = () => {
  const { activeDataset } = useDataset();
  const { status: healthStatus, checkHealth } = useBackendHealth();
  const [isExplainOpen, setIsExplainOpen] = useState(false);

  // Fetch Strategy Plan from backend API: GET /api/v1/datasets/{dataset_id}/strategy/latest
  const {
    data: strategyData,
    isLoading,
    isError,
    error,
    refetch,
  } = useQuery<StrategyPlan>({
    queryKey: queryKeys.strategy.latest(activeDataset?.id || ''),
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
          description="Select or upload a dataset to view AI Strategy Copilot recommendations and ratified directives."
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
          <div style={{ fontSize: '1rem', fontWeight: 700, color: '#F1F5F9' }}>Loading Strategic Decision Copilot Data...</div>
          <div style={{ fontSize: '0.8rem', color: '#64748B', marginTop: '4px' }}>Executing deterministic strategy planner query for {activeDataset.name}</div>
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
          <div style={{ fontSize: '1.1rem', fontWeight: 800, color: '#F87171' }}>Unable to Load Strategy Plan</div>
          <div style={{ fontSize: '0.82rem', color: '#94A3B8', textAlign: 'center', maxWidth: '500px' }}>
            {(error as any)?.message || 'An error occurred while communicating with the DecisionOS Strategy Engine.'}
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

  if (!strategyData) {
    return (
      <div style={{ padding: '32px', color: '#FFFFFF', maxWidth: '1600px', margin: '0 auto' }}>
        <IntelligencePipelineBreadcrumb currentStep="recommendations" />
        <div style={{ padding: '60px 24px', textAlign: 'center', background: '#090D14', border: '1px solid #1E293B', borderRadius: '12px', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '12px' }}>
          <Bot size={36} color="#64748B" />
          <div style={{ fontSize: '1.1rem', fontWeight: 800, color: '#F1F5F9' }}>No strategy plan available for this dataset.</div>
          <div style={{ fontSize: '0.82rem', color: '#64748B', maxWidth: '480px' }}>
            Active Dataset: <strong style={{ color: '#38BDF8' }}>{activeDataset.name}</strong>. No strategic plan has been calculated for this telemetry context yet.
          </div>
        </div>
      </div>
    );
  }

  const priorities = strategyData.strategic_priorities || [];
  const actionItems = strategyData.action_items || [];
  const milestones = strategyData.milestones || [];
  const successCriteria = strategyData.success_criteria || [];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px', paddingBottom: '40px', maxWidth: '1600px', margin: '0 auto' }}>
      {/* 1. Breadcrumb Navigation */}
      <IntelligencePipelineBreadcrumb currentStep="recommendations" />

      {/* 2. Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
            <span style={{ fontSize: '10.5px', fontWeight: 700, color: '#F59E0B', background: 'rgba(245, 158, 11, 0.12)', border: '1px solid rgba(245, 158, 11, 0.28)', padding: '1px 7px', borderRadius: '4px', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
              Phase 6.2 AI Strategy Copilot
            </span>
            <span style={{ fontSize: '12px', color: '#64748B' }}>•</span>
            <span style={{ fontSize: '12px', color: '#94A3B8', fontWeight: 600 }}>{activeDataset.name}</span>
          </div>
          <h1 style={{ fontSize: '1.8rem', fontWeight: 900, color: '#FFFFFF', margin: '4px 0 0 0' }}>
            Strategic Decision Copilot
          </h1>
        </div>

        {/* Status Pill */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', background: 'rgba(16, 185, 129, 0.15)', border: '1px solid rgba(16, 185, 129, 0.3)', padding: '6px 14px', borderRadius: '20px' }}>
          <CheckCircle2 size={14} color="#10B981" />
          <span style={{ fontSize: '0.78rem', color: '#10B981', fontWeight: 800 }}>
            Plan Status: {strategyData.status || 'ACTIVE'} ({strategyData.plan_version || 'v1.0'})
          </span>
        </div>
      </div>

      {/* 3. Main Boardroom Decision Package Card */}
      <div style={{ background: '#090D14', border: '1px solid #1E293B', borderRadius: '12px', padding: '24px', display: 'flex', flexDirection: 'column', gap: '18px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '12px' }}>
          <div>
            <div style={{ fontSize: '0.72rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: '#38BDF8', fontWeight: 800 }}>
              Boardroom Decision Directive
            </div>
            <h2 style={{ fontSize: '1.3rem', fontWeight: 800, color: '#FFFFFF', margin: '4px 0 0 0' }}>
              {strategyData.title || 'Strategic Execution Directive'}
            </h2>
            <div style={{ fontSize: '0.82rem', color: '#94A3B8', marginTop: '4px' }}>
              {strategyData.objective || strategyData.executive_summary}
            </div>
          </div>
        </div>

        {/* Summary Telemetry Metrics Grid */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '14px' }}>
          <div style={{ background: 'rgba(15, 23, 42, 0.6)', border: '1px solid #1E293B', padding: '14px', borderRadius: '8px' }}>
            <div style={{ fontSize: '0.72rem', color: '#64748B', fontWeight: 700 }}>STRATEGIC PRIORITIES</div>
            <div style={{ fontSize: '1.4rem', fontWeight: 900, color: '#10B981', marginTop: '2px' }}>
              {priorities.length} Areas
            </div>
          </div>
          <div style={{ background: 'rgba(15, 23, 42, 0.6)', border: '1px solid #1E293B', padding: '14px', borderRadius: '8px' }}>
            <div style={{ fontSize: '0.72rem', color: '#64748B', fontWeight: 700 }}>ACTION ITEMS</div>
            <div style={{ fontSize: '1.4rem', fontWeight: 900, color: '#38BDF8', marginTop: '2px' }}>
              {actionItems.length} Executable
            </div>
          </div>
          <div style={{ background: 'rgba(15, 23, 42, 0.6)', border: '1px solid #1E293B', padding: '14px', borderRadius: '8px' }}>
            <div style={{ fontSize: '0.72rem', color: '#64748B', fontWeight: 700 }}>ROADMAP MILESTONES</div>
            <div style={{ fontSize: '1.4rem', fontWeight: 900, color: '#F59E0B', marginTop: '2px' }}>
              {milestones.length} Checkpoints
            </div>
          </div>
          <div style={{ background: 'rgba(15, 23, 42, 0.6)', border: '1px solid #1E293B', padding: '14px', borderRadius: '8px' }}>
            <div style={{ fontSize: '0.72rem', color: '#64748B', fontWeight: 700 }}>SUCCESS CRITERIA</div>
            <div style={{ fontSize: '1.4rem', fontWeight: 900, color: '#A855F7', marginTop: '2px' }}>
              {successCriteria.length} Grounded KPIs
            </div>
          </div>
        </div>

        {/* Strategic Priorities Breakdown */}
        {priorities.length > 0 && (
          <div>
            <div style={{ fontSize: '0.85rem', fontWeight: 800, color: '#FFFFFF', marginBottom: '10px' }}>
              Prioritized Strategic Priorities
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {priorities.map((item: StrategicPriorityItem, idx: number) => (
                <div
                  key={idx}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '12px 16px',
                    background: idx === 0 ? 'rgba(56, 189, 248, 0.1)' : 'rgba(15, 23, 42, 0.6)',
                    border: `1px solid ${idx === 0 ? '#38BDF8' : '#1E293B'}`,
                    borderRadius: '8px',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <span style={{ fontSize: '0.85rem', fontWeight: 800, color: idx === 0 ? '#38BDF8' : '#64748B' }}>
                      #{idx + 1}
                    </span>
                    <div>
                      <span style={{ fontSize: '0.85rem', fontWeight: 700, color: '#FFFFFF' }}>{item.title}</span>
                      <div style={{ fontSize: '0.74rem', color: '#94A3B8', marginTop: '2px' }}>{item.rationale}</div>
                    </div>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                    <span style={{ fontSize: '0.72rem', fontWeight: 800, padding: '2px 8px', borderRadius: '4px', background: item.priority === 'CRITICAL' ? 'rgba(239, 68, 68, 0.2)' : 'rgba(16, 185, 129, 0.2)', color: item.priority === 'CRITICAL' ? '#EF4444' : '#10B981' }}>
                      {item.priority}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Action Items List */}
        {actionItems.length > 0 && (
          <div>
            <div style={{ fontSize: '0.85rem', fontWeight: 800, color: '#FFFFFF', marginBottom: '10px', marginTop: '8px' }}>
              Execution Action Items
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {actionItems.map((act: StrategyActionItem, idx: number) => (
                <div
                  key={idx}
                  style={{
                    background: 'rgba(15, 23, 42, 0.5)',
                    border: '1px solid #1E293B',
                    borderRadius: '8px',
                    padding: '12px 16px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                  }}
                >
                  <div>
                    <div style={{ fontSize: '0.82rem', fontWeight: 700, color: '#F1F5F9' }}>{act.title}</div>
                    <div style={{ fontSize: '0.74rem', color: '#94A3B8', marginTop: '2px' }}>{act.description}</div>
                  </div>
                  <span style={{ fontSize: '0.7rem', color: '#38BDF8', background: 'rgba(56, 189, 248, 0.1)', padding: '3px 8px', borderRadius: '4px', fontWeight: 700 }}>
                    {act.time_horizon}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Provenance Button */}
        <div style={{ display: 'flex', gap: '12px', borderTop: '1px solid #1E293B', paddingTop: '16px' }}>
          <button
            type="button"
            onClick={() => setIsExplainOpen(true)}
            style={{
              padding: '10px 20px',
              background: 'rgba(30, 41, 59, 0.8)',
              border: '1px solid #334155',
              borderRadius: '6px',
              color: '#F1F5F9',
              fontSize: '0.85rem',
              fontWeight: 700,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}
          >
            <ShieldCheck size={16} color="#38BDF8" /> Inspect Strategy Lineage
          </button>
        </div>
      </div>

      {/* Explainability Drawer */}
      <ExplainabilityDrawer
        isOpen={isExplainOpen}
        onClose={() => setIsExplainOpen(false)}
        title="Strategy Execution Plan Lineage"
        metricValue={`${strategyData.title} (${strategyData.plan_version})`}
      />
    </div>
  );
};

export default DecisionCopilotView;

