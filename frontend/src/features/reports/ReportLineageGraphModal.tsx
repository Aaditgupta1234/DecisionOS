import React from 'react';
import { X, Network, GitBranch, ArrowRight, ShieldCheck, Database, Target, AlertTriangle, CheckCircle2 } from 'lucide-react';

export interface ReportLineageGraphModalProps {
  isOpen: boolean;
  onClose: () => void;
  reportTitle?: string;
}

export const ReportLineageGraphModal: React.FC<ReportLineageGraphModalProps> = ({
  isOpen,
  onClose,
  reportTitle = 'DecisionOS Q4 Comprehensive Boardroom Governance Report',
}) => {
  if (!isOpen) return null;

  const nodes = [
    { id: '1', label: 'Q4 Boardroom Report', type: 'BOARD_REPORT', status: 'PUBLISHED', desc: 'Comprehensive Fiduciary Governance Package' },
    { id: '2', label: 'Root Cause #4: Dispatch Bottleneck', type: 'ROOT_CAUSE', status: 'ACTIVE', desc: '5.4d Latency Spike in Southeastern Corridors' },
    { id: '3', label: 'Recommendation #1: Carrier Rebalance', type: 'RECOMMENDATION', status: 'ACTIVE', desc: 'Automated 15% SLA Penalties on Bottom Couriers' },
    { id: '4', label: 'INIT-2026-001: Win-Back & SLA Deployment', type: 'INITIATIVE', status: 'EXECUTING', desc: '78% Complete Execution in Execution Center' },
    { id: '5', label: 'Forecast V3: $480K Annualized Run-Rate', type: 'FORECAST', status: 'ACTIVE', desc: '88.4% Rolling Forecast Reliability' },
    { id: '6', label: 'Outcome: +$124,000 Realized ARR', type: 'OUTCOME', status: 'VERIFIED', desc: 'Measured & Attributed by OutcomeEngine' },
  ];

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
          width: '840px',
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
            <Network size={18} color="#10B981" />
            <div>
              <span style={{ fontSize: '0.72rem', color: '#10B981', textTransform: 'uppercase', fontWeight: 800 }}>
                Visual Report Lineage DAG
              </span>
              <div style={{ fontSize: '1rem', fontWeight: 800, color: '#FFFFFF' }}>{reportTitle}</div>
            </div>
          </div>

          <button
            onClick={onClose}
            style={{ background: 'rgba(30, 41, 59, 0.6)', border: '1px solid #334155', color: '#94A3B8', borderRadius: '6px', padding: '6px', cursor: 'pointer' }}
          >
            <X size={16} />
          </button>
        </div>

        {/* Visual Lineage Nodes */}
        <div style={{ padding: '28px', display: 'flex', flexDirection: 'column', gap: '14px', maxHeight: '520px', overflowY: 'auto' }}>
          <div style={{ fontSize: '0.8rem', color: '#94A3B8', marginBottom: '4px' }}>
            Complete deterministic provenance graph linking the boardroom report to underlying causal findings:
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {nodes.map((n, idx) => (
              <React.Fragment key={n.id}>
                <div
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '14px 18px',
                    background: 'rgba(15, 23, 42, 0.8)',
                    border: '1px solid #1E293B',
                    borderRadius: '8px',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <div
                      style={{
                        width: '28px',
                        height: '28px',
                        borderRadius: '50%',
                        background: 'rgba(56, 189, 248, 0.15)',
                        color: '#38BDF8',
                        fontSize: '0.8rem',
                        fontWeight: 800,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                      }}
                    >
                      {idx + 1}
                    </div>
                    <div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <span style={{ fontSize: '0.68rem', fontWeight: 800, textTransform: 'uppercase', color: '#38BDF8' }}>
                          {n.type}
                        </span>
                        <span style={{ fontSize: '0.68rem', color: '#10B981', fontWeight: 700 }}>
                          • {n.status}
                        </span>
                      </div>
                      <div style={{ fontSize: '0.9rem', fontWeight: 700, color: '#FFFFFF', marginTop: '2px' }}>
                        {n.label}
                      </div>
                      <div style={{ fontSize: '0.76rem', color: '#94A3B8', marginTop: '2px' }}>
                        {n.desc}
                      </div>
                    </div>
                  </div>
                </div>

                {idx < nodes.length - 1 && (
                  <div style={{ display: 'flex', justifyContent: 'center', margin: '-4px 0' }}>
                    <span style={{ fontSize: '0.72rem', color: '#64748B', fontWeight: 700 }}>↓ DETERMINISTIC CAUSAL LINK ↓</span>
                  </div>
                )}
              </React.Fragment>
            ))}
          </div>
        </div>

        {/* Footer */}
        <div style={{ padding: '14px 24px', background: '#070A0F', borderTop: '1px solid #1E293B', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <span style={{ fontSize: '0.75rem', color: '#10B981', fontWeight: 700 }}>
            ✓ 100% Causal Coverage Verified
          </span>
          <button
            onClick={onClose}
            style={{ padding: '8px 18px', background: '#0284C7', border: 'none', borderRadius: '6px', color: '#FFFFFF', fontSize: '0.8rem', fontWeight: 700, cursor: 'pointer' }}
          >
            Close Lineage
          </button>
        </div>
      </div>
    </div>
  );
};
