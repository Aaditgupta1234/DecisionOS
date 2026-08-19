import React from 'react';
import { X, ArrowRight, ShieldCheck, TrendingUp, TrendingDown, GitCompare, CheckCircle2 } from 'lucide-react';

interface Props {
  isOpen: boolean;
  onClose: () => void;
  runA?: {
    runId: string;
    completedAt: string;
    healthScore: number;
    findingsCount: number;
    criticalCount: number;
    recoveryPotential: string;
    datasetName: string;
  };
  runB?: {
    runId: string;
    completedAt: string;
    healthScore: number;
    findingsCount: number;
    criticalCount: number;
    recoveryPotential: string;
    datasetName: string;
  };
}

export const RunComparisonModal: React.FC<Props> = ({
  isOpen,
  onClose,
  runA = {
    runId: 'RUN-2026-0818-01 (Current Run)',
    completedAt: 'Aug 18, 2026 • 14:32 UTC',
    healthScore: 82,
    findingsCount: 17,
    criticalCount: 2,
    recoveryPotential: '+$480K ARR',
    datasetName: 'Olist Ecommerce Dataset (2023–2024)',
  },
  runB = {
    runId: 'RUN-2026-0810-02 (Prior Run)',
    completedAt: 'Aug 10, 2026 • 18:40 UTC',
    healthScore: 75,
    findingsCount: 24,
    criticalCount: 5,
    recoveryPotential: '+$320K ARR',
    datasetName: 'Olist Ecommerce Dataset (2023–2024)',
  },
}) => {
  if (!isOpen) return null;

  const scoreDelta = runA.healthScore - runB.healthScore;
  const criticalDelta = runA.criticalCount - runB.criticalCount;

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      background: 'rgba(0, 0, 0, 0.8)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000,
      padding: '24px',
    }}>
      <div style={{
        maxWidth: '720px',
        width: '100%',
        background: '#090C12',
        border: '1px solid #1E293B',
        borderRadius: '14px',
        padding: '28px',
        boxShadow: '0 25px 60px rgba(0, 0, 0, 0.9)',
        color: '#FFFFFF',
        position: 'relative',
      }}>
        {/* Header */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <GitCompare size={18} color="#38BDF8" />
            <h2 style={{ fontSize: '18px', fontWeight: 800, margin: 0 }}>
              Analysis Run Comparison & Delta Engine
            </h2>
          </div>

          <button
            onClick={onClose}
            style={{ background: 'transparent', border: 'none', color: '#94A3B8', cursor: 'pointer', padding: '4px' }}
          >
            <X size={18} />
          </button>
        </div>

        {/* Comparison Header */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr auto 1fr', gap: '16px', alignItems: 'center', marginBottom: '24px' }}>
          <div style={{ background: '#05070B', border: '1px solid #141C28', borderRadius: '8px', padding: '14px' }}>
            <span style={{ fontSize: '10px', color: '#64748B', textTransform: 'uppercase', fontWeight: 700 }}>Run A (Active)</span>
            <div style={{ fontSize: '14px', fontWeight: 800, color: '#38BDF8', margin: '2px 0' }}>{runA.runId}</div>
            <span style={{ fontSize: '11px', color: '#94A3B8' }}>{runA.completedAt}</span>
          </div>

          <span style={{ fontSize: '13px', fontWeight: 800, color: '#64748B' }}>VS</span>

          <div style={{ background: '#05070B', border: '1px solid #141C28', borderRadius: '8px', padding: '14px' }}>
            <span style={{ fontSize: '10px', color: '#64748B', textTransform: 'uppercase', fontWeight: 700 }}>Run B (Historical)</span>
            <div style={{ fontSize: '14px', fontWeight: 800, color: '#CBD5E1', margin: '2px 0' }}>{runB.runId}</div>
            <span style={{ fontSize: '11px', color: '#94A3B8' }}>{runB.completedAt}</span>
          </div>
        </div>

        {/* Delta Metrics Comparison Grid */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginBottom: '24px' }}>
          {/* Delta 1: Health Score */}
          <div style={{ background: '#05070B', border: '1px solid #141C28', borderRadius: '8px', padding: '14px 18px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div>
              <span style={{ fontSize: '11px', color: '#94A3B8', textTransform: 'uppercase', fontWeight: 600 }}>Business Health Score</span>
              <div style={{ fontSize: '15px', fontWeight: 800, color: '#FFFFFF', marginTop: '2px' }}>
                {runA.healthScore}/100 vs {runB.healthScore}/100
              </div>
            </div>

            <div style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '4px',
              color: scoreDelta >= 0 ? '#10B981' : '#EF4444',
              background: scoreDelta >= 0 ? 'rgba(16, 185, 129, 0.12)' : 'rgba(239, 68, 68, 0.12)',
              padding: '4px 10px',
              borderRadius: '6px',
              fontSize: '13px',
              fontWeight: 800,
            }}>
              {scoreDelta >= 0 ? <TrendingUp size={14} /> : <TrendingDown size={14} />}
              <span>{scoreDelta >= 0 ? `+${scoreDelta} pts improvement` : `${scoreDelta} pts decrease`}</span>
            </div>
          </div>

          {/* Delta 2: Critical Findings */}
          <div style={{ background: '#05070B', border: '1px solid #141C28', borderRadius: '8px', padding: '14px 18px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div>
              <span style={{ fontSize: '11px', color: '#94A3B8', textTransform: 'uppercase', fontWeight: 600 }}>Critical Severity Risks</span>
              <div style={{ fontSize: '15px', fontWeight: 800, color: '#FFFFFF', marginTop: '2px' }}>
                {runA.criticalCount} Critical vs {runB.criticalCount} Critical
              </div>
            </div>

            <div style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '4px',
              color: '#10B981',
              background: 'rgba(16, 185, 129, 0.12)',
              padding: '4px 10px',
              borderRadius: '6px',
              fontSize: '13px',
              fontWeight: 800,
            }}>
              <CheckCircle2 size={14} />
              <span>{Math.abs(criticalDelta)} Critical Risks Mitigated</span>
            </div>
          </div>

          {/* Delta 3: Projected Recovery Potential */}
          <div style={{ background: '#05070B', border: '1px solid #141C28', borderRadius: '8px', padding: '14px 18px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div>
              <span style={{ fontSize: '11px', color: '#94A3B8', textTransform: 'uppercase', fontWeight: 600 }}>Projected Recovery Opportunity</span>
              <div style={{ fontSize: '15px', fontWeight: 800, color: '#FFFFFF', marginTop: '2px' }}>
                {runA.recoveryPotential} vs {runB.recoveryPotential}
              </div>
            </div>

            <div style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '4px',
              color: '#38BDF8',
              background: 'rgba(56, 189, 248, 0.12)',
              padding: '4px 10px',
              borderRadius: '6px',
              fontSize: '13px',
              fontWeight: 800,
            }}>
              <TrendingUp size={14} />
              <span>+$160K Additional Upside Identified</span>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
          <button
            onClick={onClose}
            style={{
              background: '#1D4ED8',
              border: '1px solid #3B82F6',
              color: '#FFFFFF',
              padding: '8px 20px',
              borderRadius: '6px',
              fontSize: '12.5px',
              fontWeight: 700,
              cursor: 'pointer',
            }}
          >
            Done Comparing
          </button>
        </div>
      </div>
    </div>
  );
};
