import React from 'react';
import { X, GitMerge, ArrowRight, ShieldCheck, CheckCircle2, Layers } from 'lucide-react';

interface AlertLineageModalProps {
  isOpen: boolean;
  onClose: () => void;
  alertCode: string;
}

export const AlertLineageModal: React.FC<AlertLineageModalProps> = ({
  isOpen,
  onClose,
  alertCode,
}) => {
  if (!isOpen) return null;

  const lineageNodes = [
    { type: 'ALERT', label: `${alertCode}: Retention Drift (-6.0%)`, color: '#EF4444' },
    { type: 'ROOT_CAUSE', label: 'Root Cause #4: Southeastern Transit Latency', color: '#F59E0B' },
    { type: 'RECOMMENDATION', label: 'Recommendation #1: Enforce 15% Courier SLA Penalties', color: '#38BDF8' },
    { type: 'INITIATIVE', label: 'Initiative INIT-2026-001 (78% Complete)', color: '#10B981' },
    { type: 'TELEMETRY', label: 'Snapshot V4 Telemetry Baseline', color: '#A855F7' },
  ];

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        backgroundColor: 'rgba(0, 0, 0, 0.75)',
        backdropFilter: 'blur(6px)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 9999,
        padding: '20px',
      }}
      onClick={onClose}
    >
      <div
        style={{
          backgroundColor: '#090D14',
          border: '1px solid #1E293B',
          borderRadius: '16px',
          width: '100%',
          maxWidth: '680px',
          overflow: 'hidden',
          boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.7)',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div style={{ padding: '20px 24px', borderBottom: '1px solid #1E293B', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <GitMerge size={18} color="#10B981" />
            <h3 style={{ fontSize: '1.1rem', fontWeight: 800, color: '#FFFFFF', margin: 0 }}>
              Explainable Alert Lineage DAG • {alertCode}
            </h3>
          </div>
          <button onClick={onClose} style={{ background: 'transparent', border: 'none', color: '#64748B', cursor: 'pointer' }}>
            <X size={18} />
          </button>
        </div>

        {/* Content */}
        <div style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '14px' }}>
          <p style={{ fontSize: '0.82rem', color: '#94A3B8', margin: 0 }}>
            Every alert in DecisionOS is mathematically connected back to root causes, recommendations, and strategic initiatives.
          </p>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {lineageNodes.map((node, idx) => (
              <div
                key={idx}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '12px',
                  padding: '12px 16px',
                  background: 'rgba(15, 23, 42, 0.6)',
                  border: '1px solid #1E293B',
                  borderRadius: '8px',
                }}
              >
                <span style={{ fontSize: '0.68rem', fontWeight: 800, color: node.color, background: 'rgba(15, 23, 42, 0.8)', padding: '2px 8px', borderRadius: '4px', minWidth: '110px', textAlign: 'center' }}>
                  {node.type}
                </span>
                <span style={{ fontSize: '0.85rem', fontWeight: 700, color: '#FFFFFF' }}>{node.label}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
