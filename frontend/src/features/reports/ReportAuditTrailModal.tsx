import React from 'react';
import { X, ShieldCheck, History, CheckCircle2, Lock } from 'lucide-react';

export interface ReportAuditTrailModalProps {
  isOpen: boolean;
  onClose: () => void;
  reportTitle?: string;
}

export const ReportAuditTrailModal: React.FC<ReportAuditTrailModalProps> = ({
  isOpen,
  onClose,
  reportTitle = 'DecisionOS Q4 Comprehensive Boardroom Governance Report',
}) => {
  if (!isOpen) return null;

  const events = [
    {
      type: 'REPORT_GENERATED',
      actor: 'DecisionOS Reporting Engine',
      time: 'Today at 2:00 PM',
      hash: 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
      details: 'Compiled from Pinned Graph Snapshot V3 (Health 85.0, ARR $124K)',
    },
    {
      type: 'REPORT_REVIEWED',
      actor: 'Chief Operating Officer (COO)',
      time: 'Today at 2:15 PM',
      hash: '8f4b238a2c13d8e578f2479e09d2bc1945a89e4726b89e34589d12389a023bc4',
      details: 'Verified Southeastern hub delivery metrics and courier SLA penalties',
    },
    {
      type: 'REPORT_APPROVED',
      actor: 'Chief Executive Officer (CEO)',
      time: 'Today at 2:30 PM',
      hash: '1a72a9b34e56c7890123456789abcdef0123456789abcdef0123456789abcdef',
      details: 'Formally approved for executive board distribution and fiduciary sign-off',
    },
    {
      type: 'REPORT_PUBLISHED',
      actor: 'Board Governance Secretary',
      time: 'Today at 2:45 PM',
      hash: '456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123',
      details: 'Published to Board of Directors with 100% citation coverage seal',
    },
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
            <History size={18} color="#38BDF8" />
            <div>
              <span style={{ fontSize: '0.72rem', color: '#38BDF8', textTransform: 'uppercase', fontWeight: 800 }}>
                Immutable Governance Audit Trail
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

        {/* Audit Events List */}
        <div style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '12px', maxHeight: '500px', overflowY: 'auto' }}>
          {events.map((ev, idx) => (
            <div
              key={idx}
              style={{
                padding: '16px',
                borderRadius: '8px',
                background: 'rgba(15, 23, 42, 0.7)',
                border: '1px solid #1E293B',
                display: 'flex',
                flexDirection: 'column',
                gap: '6px',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <span style={{ fontSize: '0.72rem', fontWeight: 800, color: '#10B981', background: 'rgba(16, 185, 129, 0.12)', padding: '2px 8px', borderRadius: '4px' }}>
                  ✓ {ev.type}
                </span>
                <span style={{ fontSize: '0.72rem', color: '#64748B' }}>{ev.time}</span>
              </div>

              <div style={{ fontSize: '0.88rem', fontWeight: 700, color: '#FFFFFF' }}>Actor: {ev.actor}</div>
              <div style={{ fontSize: '0.78rem', color: '#94A3B8' }}>{ev.details}</div>

              <div style={{ fontSize: '0.68rem', color: '#64748B', fontFamily: 'monospace', marginTop: '4px', display: 'flex', alignItems: 'center', gap: '4px' }}>
                <Lock size={11} color="#64748B" />
                <span>SHA-256 Seal: {ev.hash}</span>
              </div>
            </div>
          ))}
        </div>

        {/* Footer */}
        <div style={{ padding: '14px 24px', background: '#070A0F', borderTop: '1px solid #1E293B', display: 'flex', justifyContent: 'flex-end' }}>
          <button
            onClick={onClose}
            style={{ padding: '8px 18px', background: '#0284C7', border: 'none', borderRadius: '6px', color: '#FFFFFF', fontSize: '0.8rem', fontWeight: 700, cursor: 'pointer' }}
          >
            Close Audit Trail
          </button>
        </div>
      </div>
    </div>
  );
};
