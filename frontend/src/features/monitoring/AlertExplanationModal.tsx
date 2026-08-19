import React from 'react';
import { X, Sparkles, AlertTriangle, ShieldCheck, FileCheck, CheckCircle2 } from 'lucide-react';

interface AlertExplanationModalProps {
  isOpen: boolean;
  onClose: () => void;
  alertCode: string;
}

export const AlertExplanationModal: React.FC<AlertExplanationModalProps> = ({
  isOpen,
  onClose,
  alertCode,
}) => {
  if (!isOpen) return null;

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
          maxWidth: '620px',
          overflow: 'hidden',
          boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.7)',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div style={{ padding: '20px 24px', borderBottom: '1px solid #1E293B', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Sparkles size={18} color="#38BDF8" />
            <h3 style={{ fontSize: '1.1rem', fontWeight: 800, color: '#FFFFFF', margin: 0 }}>
              Deterministic Explainability Diagnosis • {alertCode}
            </h3>
          </div>
          <button onClick={onClose} style={{ background: 'transparent', border: 'none', color: '#64748B', cursor: 'pointer' }}>
            <X size={18} />
          </button>
        </div>

        {/* Content */}
        <div style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div style={{ background: 'rgba(56, 189, 248, 0.08)', border: '1px solid rgba(56, 189, 248, 0.2)', padding: '16px', borderRadius: '10px' }}>
            <div style={{ fontSize: '0.72rem', fontWeight: 800, color: '#38BDF8', textTransform: 'uppercase' }}>
              RULE FIRED: RETENTION_DRIFT_5PCT
            </div>
            <div style={{ fontSize: '0.85rem', color: '#F1F5F9', marginTop: '6px', lineHeight: 1.4 }}>
              Alert triggered because <strong>Customer Retention Rate (79.1%)</strong> dropped below the -5.0% tolerance band relative to expected baseline (84.2%). Grounded in SnapshotV4 telemetry with 94.2% statistical confidence.
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '10px' }}>
            <div style={{ background: 'rgba(15, 23, 42, 0.6)', border: '1px solid #1E293B', padding: '12px', borderRadius: '8px' }}>
              <div style={{ fontSize: '0.65rem', color: '#64748B' }}>CURRENT VALUE</div>
              <div style={{ fontSize: '1.2rem', fontWeight: 900, color: '#EF4444', marginTop: '2px' }}>79.1%</div>
              <div style={{ fontSize: '0.7rem', color: '#94A3B8' }}>Expected: 84.2%</div>
            </div>
            <div style={{ background: 'rgba(15, 23, 42, 0.6)', border: '1px solid #1E293B', padding: '12px', borderRadius: '8px' }}>
              <div style={{ fontSize: '0.65rem', color: '#64748B' }}>MEASURED DRIFT</div>
              <div style={{ fontSize: '1.2rem', fontWeight: 900, color: '#F59E0B', marginTop: '2px' }}>-6.0%</div>
              <div style={{ fontSize: '0.7rem', color: '#94A3B8' }}>Threshold: -5.0%</div>
            </div>
          </div>

          <div style={{ background: 'rgba(15, 23, 42, 0.6)', border: '1px solid #1E293B', padding: '14px', borderRadius: '8px', display: 'flex', flexDirection: 'column', gap: '6px' }}>
            <div style={{ fontSize: '0.72rem', fontWeight: 800, color: '#10B981' }}>CITATIONS & EVIDENCE TELEMETRY</div>
            <div style={{ fontSize: '0.78rem', color: '#94A3B8' }}>• Primary Source: <code>SnapshotV4.RetentionEngine:Node#04</code></div>
            <div style={{ fontSize: '0.78rem', color: '#94A3B8' }}>• Associated Metric: <code>LogisticsEngine.HubSoutheastLatency (4.8d)</code></div>
            <div style={{ fontSize: '0.78rem', color: '#94A3B8' }}>• Statistical Confidence: <strong>94.2%</strong> (Grounded in 14,200 transactions)</div>
          </div>
        </div>
      </div>
    </div>
  );
};
