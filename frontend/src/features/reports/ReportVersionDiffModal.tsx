import React from 'react';
import { X, GitCompare, TrendingUp, CheckCircle, ArrowRight, ShieldAlert } from 'lucide-react';

export interface ReportVersionDiffModalProps {
  isOpen: boolean;
  onClose: () => void;
  reportTitle?: string;
}

export const ReportVersionDiffModal: React.FC<ReportVersionDiffModalProps> = ({
  isOpen,
  onClose,
  reportTitle = 'DecisionOS Boardroom Report Version Diff',
}) => {
  if (!isOpen) return null;

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        backgroundColor: 'rgba(0, 0, 0, 0.85)',
        backdropFilter: 'blur(8px)',
        zIndex: 300,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '24px',
        animation: 'fadeIn 0.15s ease',
      }}
      onClick={onClose}
    >
      <div
        style={{
          width: '880px',
          maxWidth: '94vw',
          backgroundColor: '#090D14',
          border: '1px solid #1E293B',
          borderRadius: '14px',
          boxShadow: '0 25px 60px rgba(0,0,0,0.95)',
          overflow: 'hidden',
          display: 'flex',
          flexDirection: 'column',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Modal Header */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '18px 24px', borderBottom: '1px solid #1E293B', background: '#070A0F' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <GitCompare size={18} color="#38BDF8" />
            <div>
              <span style={{ fontSize: '0.72rem', color: '#38BDF8', textTransform: 'uppercase', fontWeight: 800 }}>
                Historical Report Version Comparison
              </span>
              <div style={{ fontSize: '1rem', fontWeight: 800, color: '#FFFFFF' }}>Comparing Version V1 → Version V2</div>
            </div>
          </div>

          <button
            onClick={onClose}
            style={{ background: 'rgba(30, 41, 59, 0.6)', border: '1px solid #334155', color: '#94A3B8', borderRadius: '6px', padding: '6px', cursor: 'pointer' }}
          >
            <X size={16} />
          </button>
        </div>

        {/* Diff Content */}
        <div style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '18px', maxHeight: '520px', overflowY: 'auto' }}>
          {/* Summary Delta Banner */}
          <div style={{ background: 'rgba(56, 189, 248, 0.08)', border: '1px solid rgba(56, 189, 248, 0.25)', borderRadius: '10px', padding: '16px' }}>
            <div style={{ fontSize: '0.75rem', color: '#38BDF8', fontWeight: 800, textTransform: 'uppercase', marginBottom: '4px' }}>
              Summary Delta
            </div>
            <p style={{ fontSize: '0.88rem', color: '#F1F5F9', lineHeight: 1.5, margin: 0 }}>
              Report V2 incorporates confirmed <strong>+$124K ARR recovery</strong> from Recovery Path A with <strong>+11.0 pts health lift</strong>, transitioning directives from planning into active execution.
            </p>
          </div>

          {/* Metric Comparison Table */}
          <div>
            <div style={{ fontSize: '0.85rem', fontWeight: 800, color: '#FFFFFF', marginBottom: '10px' }}>
              KPI & Evidence Deltas
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '12px' }}>
              <div style={{ background: 'rgba(15, 23, 42, 0.6)', border: '1px solid #1E293B', padding: '14px', borderRadius: '8px' }}>
                <div style={{ fontSize: '0.72rem', color: '#64748B', fontWeight: 700 }}>PORTFOLIO HEALTH</div>
                <div style={{ fontSize: '1.2rem', fontWeight: 900, color: '#10B981', marginTop: '4px' }}>
                  74.0 → 85.0 <span style={{ fontSize: '0.85rem' }}>(+11.0)</span>
                </div>
              </div>
              <div style={{ background: 'rgba(15, 23, 42, 0.6)', border: '1px solid #1E293B', padding: '14px', borderRadius: '8px' }}>
                <div style={{ fontSize: '0.72rem', color: '#64748B', fontWeight: 700 }}>RETENTION RATE</div>
                <div style={{ fontSize: '1.2rem', fontWeight: 900, color: '#10B981', marginTop: '4px' }}>
                  79.5% → 84.2% <span style={{ fontSize: '0.85rem' }}>(+4.7%)</span>
                </div>
              </div>
              <div style={{ background: 'rgba(15, 23, 42, 0.6)', border: '1px solid #1E293B', padding: '14px', borderRadius: '8px' }}>
                <div style={{ fontSize: '0.72rem', color: '#64748B', fontWeight: 700 }}>REALIZED ARR</div>
                <div style={{ fontSize: '1.2rem', fontWeight: 900, color: '#38BDF8', marginTop: '4px' }}>
                  $45K → $124K <span style={{ fontSize: '0.85rem' }}>(+$79K)</span>
                </div>
              </div>
            </div>
          </div>

          {/* Recommendations Changed */}
          <div>
            <div style={{ fontSize: '0.85rem', fontWeight: 800, color: '#FFFFFF', marginBottom: '10px' }}>
              Strategic Recommendations Evolution
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <div style={{ padding: '10px 14px', background: 'rgba(16, 185, 129, 0.1)', border: '1px solid rgba(16, 185, 129, 0.25)', borderRadius: '6px', fontSize: '0.82rem', color: '#10B981', fontWeight: 600 }}>
                + ADDED: Recommendation #1: Carrier Rebalancing & Automated SLA Penalties (+$124K ARR)
              </div>
              <div style={{ padding: '10px 14px', background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.25)', borderRadius: '6px', fontSize: '0.82rem', color: '#EF4444', fontWeight: 600 }}>
                - REMOVED: Recommendation #14: Manual Courier Phone Outreach (SUPERSEDED)
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div style={{ padding: '14px 24px', background: '#070A0F', borderTop: '1px solid #1E293B', display: 'flex', justifyContent: 'flex-end' }}>
          <button
            onClick={onClose}
            style={{ padding: '8px 18px', background: '#0284C7', border: 'none', borderRadius: '6px', color: '#FFFFFF', fontSize: '0.8rem', fontWeight: 700, cursor: 'pointer' }}
          >
            Close Diff
          </button>
        </div>
      </div>
    </div>
  );
};
