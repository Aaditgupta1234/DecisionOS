import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useDataset } from '../../context/DatasetContext';
import { DecisionApi } from '../../api';
import { queryKeys } from '../../shared/api/queryKeys';
import { useBackendHealth } from '../../shared/hooks/useBackendHealth';
import { BackendOfflineScreen } from '../../shared/components/feedback/BackendOfflineScreen';
import { NoDatasetEmptyState } from '../../shared/components/feedback/NoDatasetEmptyState';
import { IntelligencePipelineBreadcrumb } from '../../shared/components/pipeline/IntelligencePipelineBreadcrumb';
import { RunComparisonModal } from '../../shared/components/history/RunComparisonModal';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from 'recharts';
import {
  History,
  GitCompare,
  FileSpreadsheet,
  CheckCircle2,
  ArrowRight,
  ShieldCheck,
  TrendingUp,
  RefreshCw,
  Eye,
} from 'lucide-react';
import { Link } from 'react-router-dom';

export interface AnalysisRunEntity {
  id: string;
  datasetName: string;
  generatedAt: string;
  healthScore: number;
  findingCount: number;
  criticalCount: number;
  recommendationCount: number;
  recoveryPotential: string;
  status: 'Completed' | 'Processing' | 'Failed';
}

export const AnalysisHistoryView: React.FC = () => {
  const { activeDataset } = useDataset();
  const { status: healthStatus, checkHealth } = useBackendHealth();

  const [selectedRunId, setSelectedRunId] = useState<string>('RUN-2026-0818-01');
  const [isCompareOpen, setIsCompareOpen] = useState(false);

  if (healthStatus === 'offline') {
    return <BackendOfflineScreen onRetry={checkHealth} />;
  }

  if (!activeDataset) {
    return (
      <div style={{ padding: '32px' }}>
        <NoDatasetEmptyState
          title="No Active Dataset Selected"
          description="Select or upload a dataset to inspect historical intelligence runs and track score progression."
        />
      </div>
    );
  }

  const historicalRuns: AnalysisRunEntity[] = [
    {
      id: 'RUN-2026-0818-01',
      datasetName: activeDataset.name || 'Olist Ecommerce Dataset',
      generatedAt: 'Aug 18, 2026 • 14:32 UTC',
      healthScore: 82,
      findingCount: 17,
      criticalCount: 2,
      recommendationCount: 6,
      recoveryPotential: '+$480K ARR',
      status: 'Completed',
    },
    {
      id: 'RUN-2026-0815-04',
      datasetName: activeDataset.name || 'Olist Ecommerce Dataset',
      generatedAt: 'Aug 15, 2026 • 09:15 UTC',
      healthScore: 78,
      findingCount: 21,
      criticalCount: 4,
      recommendationCount: 7,
      recoveryPotential: '+$390K ARR',
      status: 'Completed',
    },
    {
      id: 'RUN-2026-0810-02',
      datasetName: activeDataset.name || 'Olist Ecommerce Dataset',
      generatedAt: 'Aug 10, 2026 • 18:40 UTC',
      healthScore: 75,
      findingCount: 24,
      criticalCount: 5,
      recommendationCount: 8,
      recoveryPotential: '+$320K ARR',
      status: 'Completed',
    },
    {
      id: 'RUN-2026-0801-01',
      datasetName: activeDataset.name || 'Olist Ecommerce Dataset',
      generatedAt: 'Aug 01, 2026 • 11:20 UTC',
      healthScore: 71,
      findingCount: 28,
      criticalCount: 7,
      recommendationCount: 9,
      recoveryPotential: '+$280K ARR',
      status: 'Completed',
    },
  ];

  const timelineData = [
    { run: 'Aug 01', score: 71, findings: 28, recovery: 280 },
    { run: 'Aug 10', score: 75, findings: 24, recovery: 320 },
    { run: 'Aug 15', score: 78, findings: 21, recovery: 390 },
    { run: 'Aug 18', score: 82, findings: 17, recovery: 480 },
  ];

  const currentRun = historicalRuns.find(r => r.id === selectedRunId) || historicalRuns[0];

  return (
    <div style={{ padding: '28px 32px', color: '#FFFFFF', maxWidth: '1600px', margin: '0 auto' }}>
      
      {/* 1. Pipeline Breadcrumb */}
      <IntelligencePipelineBreadcrumb currentStep="reports" />

      {/* 2. Header & Action Bar */}
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: '20px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
            <span style={{ fontSize: '10.5px', fontWeight: 700, color: '#38BDF8', background: 'rgba(56, 189, 248, 0.12)', border: '1px solid rgba(56, 189, 248, 0.28)', padding: '1px 7px', borderRadius: '4px', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
              Historical Intelligence Audit
            </span>
            <span style={{ fontSize: '12px', color: '#64748B' }}>•</span>
            <span style={{ fontSize: '12px', color: '#94A3B8', fontWeight: 600 }}>{activeDataset.name}</span>
          </div>
          <h1 style={{ fontSize: '24px', fontWeight: 800, letterSpacing: '-0.02em' }}>
            Analysis Run History & Progression
          </h1>
          <p style={{ fontSize: '13px', color: '#94A3B8', marginTop: '4px' }}>
            Audit registry of all historical deterministic analysis executions with run-over-run diffing.
          </p>
        </div>

        {/* Compare Runs Button */}
        <button
          type="button"
          onClick={() => setIsCompareOpen(true)}
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '8px',
            background: '#1D4ED8',
            border: '1px solid #3B82F6',
            color: '#FFFFFF',
            padding: '8px 18px',
            borderRadius: '7px',
            fontSize: '12.5px',
            fontWeight: 700,
            cursor: 'pointer',
            boxShadow: '0 0 14px rgba(59, 130, 246, 0.35)',
          }}
        >
          <GitCompare size={14} />
          <span>Compare Runs (Run #24 vs Run #18)</span>
        </button>
      </div>

      {/* 3. Historical Timeline Trajectory Chart */}
      <div style={{
        background: '#090C12',
        border: '1px solid #1A2230',
        borderRadius: '12px',
        padding: '20px',
        marginBottom: '24px',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px' }}>
          <div>
            <h3 style={{ fontSize: '15px', fontWeight: 800, color: '#FFFFFF', margin: 0 }}>
              Business Health Score Progression Trajectory
            </h3>
            <span style={{ fontSize: '11px', color: '#64748B' }}>Historical run-over-run evolution from 71 → 82 (+11 pts)</span>
          </div>
          <span style={{ fontSize: '11px', fontWeight: 700, color: '#10B981', background: 'rgba(16, 185, 129, 0.1)', padding: '2px 8px', borderRadius: '4px' }}>
            +11 pts Overall Health Gain
          </span>
        </div>

        <div style={{ width: '100%', height: '200px' }}>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={timelineData} margin={{ top: 10, right: 20, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#141C28" vertical={false} />
              <XAxis dataKey="run" stroke="#475569" fontSize={11} tickLine={false} />
              <YAxis domain={[60, 100]} stroke="#475569" fontSize={11} tickLine={false} />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#090D14',
                  borderColor: '#1E293B',
                  borderRadius: '8px',
                  fontSize: '12px',
                  color: '#FFFFFF',
                }}
              />
              <Line type="monotone" dataKey="score" stroke="#10B981" strokeWidth={3} dot={{ fill: '#10B981', r: 5 }} name="Health Score" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* 4. Analysis Run Table */}
      <div style={{ background: '#090C12', border: '1px solid #1A2230', borderRadius: '12px', overflow: 'hidden', marginBottom: '24px' }}>
        <div style={{ padding: '16px 20px', borderBottom: '1px solid #141A24', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <History size={16} color="#38BDF8" />
            <span style={{ fontSize: '13px', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
              Execution Registry ({historicalRuns.length} Runs)
            </span>
          </div>
        </div>

        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid #141A24', color: '#64748B', textAlign: 'left', fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              <th style={{ padding: '12px 20px' }}>Run Identifier</th>
              <th style={{ padding: '12px 16px' }}>Execution Time</th>
              <th style={{ padding: '12px 16px' }}>Health Score</th>
              <th style={{ padding: '12px 16px' }}>Findings</th>
              <th style={{ padding: '12px 16px' }}>Recovery Upside</th>
              <th style={{ padding: '12px 16px' }}>Status</th>
              <th style={{ padding: '12px 20px', textAlign: 'right' }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {historicalRuns.map((run) => {
              const isSelected = selectedRunId === run.id;

              return (
                <tr
                  key={run.id}
                  style={{
                    borderBottom: '1px solid #111620',
                    background: isSelected ? 'rgba(56, 189, 248, 0.04)' : 'transparent',
                  }}
                >
                  <td style={{ padding: '14px 20px', fontWeight: 700, color: isSelected ? '#38BDF8' : '#FFFFFF', fontFamily: 'monospace' }}>
                    {run.id}
                  </td>

                  <td style={{ padding: '14px 16px', color: '#94A3B8', fontSize: '12px' }}>
                    {run.generatedAt}
                  </td>

                  <td style={{ padding: '14px 16px' }}>
                    <span style={{ fontSize: '12px', fontWeight: 800, color: '#10B981', background: 'rgba(16, 185, 129, 0.1)', padding: '2px 7px', borderRadius: '4px' }}>
                      {run.healthScore} / 100
                    </span>
                  </td>

                  <td style={{ padding: '14px 16px', color: '#CBD5E1', fontWeight: 600 }}>
                    {run.findingCount} ({run.criticalCount} Critical)
                  </td>

                  <td style={{ padding: '14px 16px', color: '#10B981', fontWeight: 700 }}>
                    {run.recoveryPotential}
                  </td>

                  <td style={{ padding: '14px 16px' }}>
                    <span style={{
                      fontSize: '11px',
                      fontWeight: 700,
                      color: '#10B981',
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: '4px',
                    }}>
                      <CheckCircle2 size={12} />
                      <span>{run.status}</span>
                    </span>
                  </td>

                  <td style={{ padding: '14px 20px', textAlign: 'right' }}>
                    <div style={{ display: 'flex', gap: '8px', justifyContent: 'flex-end' }}>
                      <button
                        type="button"
                        onClick={() => setSelectedRunId(run.id)}
                        style={{
                          background: isSelected ? '#1D4ED8' : '#111622',
                          border: `1px solid ${isSelected ? '#3B82F6' : '#1F2738'}`,
                          color: '#FFFFFF',
                          padding: '4px 10px',
                          borderRadius: '5px',
                          fontSize: '11.5px',
                          fontWeight: 600,
                          cursor: 'pointer',
                        }}
                      >
                        Inspect
                      </button>

                      <Link
                        to="/reports"
                        style={{
                          display: 'inline-flex',
                          alignItems: 'center',
                          gap: '4px',
                          background: '#070A0F',
                          border: '1px solid #141C28',
                          color: '#94A3B8',
                          padding: '4px 10px',
                          borderRadius: '5px',
                          fontSize: '11.5px',
                          fontWeight: 600,
                          textDecoration: 'none',
                        }}
                      >
                        <Eye size={12} />
                        <span>Brief</span>
                      </Link>
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* 5. Run Comparison Modal */}
      <RunComparisonModal
        isOpen={isCompareOpen}
        onClose={() => setIsCompareOpen(false)}
      />

    </div>
  );
};

export default AnalysisHistoryView;
