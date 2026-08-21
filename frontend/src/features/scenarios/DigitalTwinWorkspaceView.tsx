import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useDataset } from '../../context/DatasetContext';
import { DecisionApi } from '../../api';
import { queryKeys } from '../../shared/api/queryKeys';
import { useBackendHealth } from '../../shared/hooks/useBackendHealth';
import { BackendOfflineScreen } from '../../shared/components/feedback/BackendOfflineScreen';
import { NoDatasetEmptyState } from '../../shared/components/feedback/NoDatasetEmptyState';
import { IntelligencePipelineBreadcrumb } from '../../shared/components/pipeline/IntelligencePipelineBreadcrumb';
import { Scenario, ScenarioAssumption } from '../../types';
import {
  Activity,
  Cpu,
  TrendingUp,
  ShieldAlert,
  Clock,
  Zap,
  Sliders,
  Sparkles,
  GitBranch,
  Layers,
  ArrowUpRight,
  Database,
  History,
  CheckCircle2,
  RefreshCw,
  AlertTriangle
} from 'lucide-react';
import { AIScenarioAnalystModal } from './AIScenarioAnalystModal';

export const DigitalTwinWorkspaceView: React.FC = () => {
  const { activeDataset } = useDataset();
  const { status: healthStatus, checkHealth } = useBackendHealth();
  const [isAIAnalystOpen, setIsAIAnalystOpen] = useState(false);

  // Fetch Scenarios from backend API: GET /api/v1/datasets/{dataset_id}/scenarios
  const {
    data: scenariosData,
    isLoading,
    isError,
    error,
    refetch,
  } = useQuery<Scenario[]>({
    queryKey: queryKeys.digitalTwin.scenarios(activeDataset?.id || ''),
    queryFn: () => DecisionApi.listScenarios(activeDataset!.id),
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
          description="Select or upload a dataset to run digital twin scenario simulations."
        />
      </div>
    );
  }

  if (isLoading) {
    return (
      <div style={{ padding: '32px', color: '#FFFFFF', maxWidth: '1600px', margin: '0 auto' }}>
        <IntelligencePipelineBreadcrumb currentStep="execution" />
        <div style={{ padding: '60px 20px', textAlign: 'center', background: '#090D14', border: '1px solid #1E293B', borderRadius: '12px' }}>
          <RefreshCw size={28} color="#38BDF8" style={{ animation: 'spin 1s linear infinite', marginBottom: '12px' }} />
          <div style={{ fontSize: '1rem', fontWeight: 700, color: '#F1F5F9' }}>Loading Digital Twin Workspace...</div>
          <div style={{ fontSize: '0.8rem', color: '#64748B', marginTop: '4px' }}>Executing scenario simulation engine query for {activeDataset.name}</div>
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <div style={{ padding: '32px', color: '#FFFFFF', maxWidth: '1600px', margin: '0 auto' }}>
        <IntelligencePipelineBreadcrumb currentStep="execution" />
        <div style={{ padding: '40px 24px', background: 'rgba(239, 68, 68, 0.08)', border: '1px solid rgba(239, 68, 68, 0.3)', borderRadius: '12px', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '12px' }}>
          <AlertTriangle size={32} color="#EF4444" />
          <div style={{ fontSize: '1.1rem', fontWeight: 800, color: '#F87171' }}>Unable to Load Digital Twin Scenarios</div>
          <div style={{ fontSize: '0.82rem', color: '#94A3B8', textAlign: 'center', maxWidth: '500px' }}>
            {(error as any)?.message || 'An error occurred while communicating with the Scenario Planning Engine.'}
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

  const rawScenarios: Scenario[] = Array.isArray(scenariosData)
    ? scenariosData
    : (scenariosData as any)?.scenarios ?? [];
  const totalScenarios = rawScenarios.length;
  const activeSimulations = rawScenarios.filter((s: Scenario) => (s.status || '').toUpperCase() === 'ACTIVE').length;
  const governedAssumptions = rawScenarios.reduce((count: number, s: Scenario) => count + (s.assumptions || []).length, 0);

  if (totalScenarios === 0) {
    return (
      <div style={{ padding: '32px', color: '#FFFFFF', maxWidth: '1600px', margin: '0 auto' }}>
        <IntelligencePipelineBreadcrumb currentStep="execution" />
        <div style={{ padding: '60px 24px', textAlign: 'center', background: '#090D14', border: '1px solid #1E293B', borderRadius: '12px', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '12px' }}>
          <Cpu size={36} color="#64748B" />
          <div style={{ fontSize: '1.1rem', fontWeight: 800, color: '#F1F5F9' }}>No scenario simulations available for this dataset.</div>
          <div style={{ fontSize: '0.82rem', color: '#64748B', maxWidth: '480px' }}>
            Active Dataset: <strong style={{ color: '#38BDF8' }}>{activeDataset.name}</strong>. No scenario models have been compiled for this dataset yet.
          </div>
        </div>
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', paddingBottom: '40px', maxWidth: '1600px', margin: '0 auto' }}>
      {/* 1. Pipeline Breadcrumb Navigation */}
      <IntelligencePipelineBreadcrumb currentStep="execution" />

      {/* 2. Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
            <span style={{ fontSize: '10.5px', fontWeight: 700, color: '#38BDF8', background: 'rgba(56, 189, 248, 0.12)', border: '1px solid rgba(56, 189, 248, 0.28)', padding: '1px 7px', borderRadius: '4px', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
              Phase 6.3 Mathematical Simulation Layer
            </span>
            <span style={{ fontSize: '12px', color: '#64748B' }}>•</span>
            <span style={{ fontSize: '12px', color: '#94A3B8', fontWeight: 600 }}>{activeDataset.name}</span>
          </div>
          <h1 style={{ fontSize: '1.8rem', fontWeight: 900, color: '#FFFFFF', margin: '4px 0 0 0' }}>
            Enterprise Digital Twin Workspace
          </h1>
        </div>

        {/* AI Analyst Trigger Button */}
        <button
          type="button"
          onClick={() => setIsAIAnalystOpen(true)}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            padding: '8px 16px',
            background: 'linear-gradient(135deg, #7C3AED 0%, #2563EB 100%)',
            border: 'none',
            borderRadius: '8px',
            color: '#FFFFFF',
            fontSize: '0.8rem',
            fontWeight: 800,
            cursor: 'pointer',
            boxShadow: '0 4px 14px rgba(124, 58, 237, 0.3)',
          }}
        >
          <Sparkles size={14} />
          <span>Ask AI Scenario Analyst</span>
        </button>
      </div>

      {/* 3. Hero Dynamic Metrics Grid */}
      <div
        style={{
          background: 'linear-gradient(135deg, rgba(15, 23, 42, 0.9) 0%, rgba(9, 13, 20, 0.95) 100%)',
          border: '1px solid #1E293B',
          borderRadius: '16px',
          padding: '24px',
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
          gap: '18px',
        }}
      >
        <div style={{ borderRight: '1px solid #1E293B', paddingRight: '16px' }}>
          <div style={{ fontSize: '0.72rem', color: '#64748B', fontWeight: 800, textTransform: 'uppercase' }}>TOTAL SCENARIOS</div>
          <div style={{ fontSize: '2rem', fontWeight: 900, color: '#38BDF8', marginTop: '4px' }}>
            {totalScenarios} <span style={{ fontSize: '0.85rem', color: '#64748B' }}>Models</span>
          </div>
          <div style={{ fontSize: '0.75rem', color: '#10B981', fontWeight: 700, marginTop: '2px' }}>
            Compiled Telemetry Simulations
          </div>
        </div>

        <div style={{ borderRight: '1px solid #1E293B', paddingRight: '16px' }}>
          <div style={{ fontSize: '0.72rem', color: '#64748B', fontWeight: 800, textTransform: 'uppercase' }}>ACTIVE SIMULATIONS</div>
          <div style={{ fontSize: '2rem', fontWeight: 900, color: '#10B981', marginTop: '4px' }}>
            {activeSimulations} <span style={{ fontSize: '0.85rem', color: '#64748B' }}>Active</span>
          </div>
          <div style={{ fontSize: '0.75rem', color: '#94A3B8' }}>Governed Operating Envelopes</div>
        </div>

        <div>
          <div style={{ fontSize: '0.72rem', color: '#64748B', fontWeight: 800, textTransform: 'uppercase' }}>GOVERNED ASSUMPTIONS</div>
          <div style={{ fontSize: '2rem', fontWeight: 900, color: '#F59E0B', marginTop: '4px' }}>
            {governedAssumptions} <span style={{ fontSize: '0.85rem', color: '#64748B' }}>Parameters</span>
          </div>
          <div style={{ fontSize: '0.75rem', color: '#94A3B8' }}>Sensitivity Adjustment Controls</div>
        </div>
      </div>

      {/* 4. Living Digital Twin Scenarios Roster */}
      <div>
        <h2 style={{ fontSize: '1.2rem', fontWeight: 800, color: '#FFFFFF', marginBottom: '14px' }}>
          Compiled Scenario Models ({rawScenarios.length})
        </h2>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '16px' }}>
          {rawScenarios.map((scenario: Scenario, idx: number) => (
            <div
              key={scenario.id || idx}
              style={{
                background: '#090D14',
                border: '1px solid #1E293B',
                borderRadius: '12px',
                padding: '20px',
                display: 'flex',
                flexDirection: 'column',
                gap: '12px',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <span style={{ fontSize: '0.72rem', color: '#38BDF8', fontWeight: 800, textTransform: 'uppercase' }}>
                  {scenario.scenario_version || `SCENARIO-${idx + 1}`}
                </span>
                <span style={{ fontSize: '0.68rem', fontWeight: 800, color: '#10B981', background: 'rgba(16, 185, 129, 0.15)', padding: '2px 8px', borderRadius: '4px' }}>
                  {scenario.status || 'ACTIVE'}
                </span>
              </div>

              <div>
                <div style={{ fontSize: '1.1rem', fontWeight: 800, color: '#FFFFFF' }}>{scenario.name}</div>
                {scenario.description && (
                  <div style={{ fontSize: '0.78rem', color: '#94A3B8', marginTop: '4px' }}>{scenario.description}</div>
                )}
              </div>

              {/* Assumptions List */}
              {scenario.assumptions && scenario.assumptions.length > 0 && (
                <div style={{ borderTop: '1px solid #1E293B', paddingTop: '10px', marginTop: '4px' }}>
                  <div style={{ fontSize: '0.72rem', color: '#64748B', fontWeight: 700, marginBottom: '6px' }}>SENSITIVITY ASSUMPTIONS</div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                    {scenario.assumptions.map((asm: ScenarioAdjustmentTypeAssumptions, aIdx: number) => (
                      <div key={aIdx} style={{ fontSize: '0.76rem', color: '#CBD5E1', display: 'flex', justifyContent: 'space-between' }}>
                        <span>• {asm.metric_key}</span>
                        <strong style={{ color: '#F59E0B' }}>
                          {asm.adjustment_value > 0 ? `+${asm.adjustment_value}` : asm.adjustment_value} ({asm.adjustment_type})
                        </strong>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* AI Scenario Analyst Modal */}
      <AIScenarioAnalystModal
        isOpen={isAIAnalystOpen}
        onClose={() => setIsAIAnalystOpen(false)}
      />
    </div>
  );
};

type ScenarioAdjustmentTypeAssumptions = ScenarioAssumption;

export default DigitalTwinWorkspaceView;

