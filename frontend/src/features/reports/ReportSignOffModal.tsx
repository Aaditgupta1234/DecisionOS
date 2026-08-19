import React, { useState } from 'react';
import { X, CheckCircle2, ShieldCheck, AlertCircle, FileCheck } from 'lucide-react';

export interface ReportSignOffModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSignOffSuccess?: () => void;
  reportTitle?: string;
}

export const ReportSignOffModal: React.FC<ReportSignOffModalProps> = ({
  isOpen,
  onClose,
  onSignOffSuccess,
  reportTitle = 'DecisionOS Q4 Comprehensive Boardroom Governance Report',
}) => {
  const [role, setRole] = useState('CEO');
  const [action, setAction] = useState('APPROVED');
  const [rationale, setRationale] = useState('All findings and ARR projections verified against deterministic telemetry.');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setTimeout(() => {
      setIsSubmitting(false);
      if (onSignOffSuccess) onSignOffSuccess();
      onClose();
    }, 600);
  };

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
          width: '560px',
          maxWidth: '92vw',
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
        {/* Header */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '18px 24px', borderBottom: '1px solid #1E293B', background: '#070A0F' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <FileCheck size={18} color="#10B981" />
            <div>
              <span style={{ fontSize: '0.72rem', color: '#10B981', textTransform: 'uppercase', fontWeight: 800 }}>
                Executive Fiduciary Sign-Off
              </span>
              <div style={{ fontSize: '0.95rem', fontWeight: 800, color: '#FFFFFF' }}>{reportTitle}</div>
            </div>
          </div>

          <button
            onClick={onClose}
            style={{ background: 'rgba(30, 41, 59, 0.6)', border: '1px solid #334155', color: '#94A3B8', borderRadius: '6px', padding: '6px', cursor: 'pointer' }}
          >
            <X size={16} />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div>
            <label style={{ display: 'block', fontSize: '0.75rem', color: '#94A3B8', fontWeight: 700, textTransform: 'uppercase', marginBottom: '6px' }}>
              Sign-Off Role
            </label>
            <select
              value={role}
              onChange={(e) => setRole(e.target.value)}
              style={{ width: '100%', padding: '10px 14px', background: 'rgba(15, 23, 42, 0.8)', border: '1px solid #1E293B', borderRadius: '6px', color: '#FFFFFF', fontSize: '0.85rem' }}
            >
              <option value="CEO">Chief Executive Officer (CEO)</option>
              <option value="COO">Chief Operating Officer (COO)</option>
              <option value="CFO">Chief Financial Officer (CFO)</option>
              <option value="BOARD_CHAIR">Board Chair / Governance Lead</option>
            </select>
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.75rem', color: '#94A3B8', fontWeight: 700, textTransform: 'uppercase', marginBottom: '6px' }}>
              Decision Action
            </label>
            <div style={{ display: 'flex', gap: '8px' }}>
              {['APPROVED', 'REQUIRES_REVISION', 'REJECTED'].map((act) => (
                <button
                  type="button"
                  key={act}
                  onClick={() => setAction(act)}
                  style={{
                    flex: 1,
                    padding: '8px',
                    borderRadius: '6px',
                    border: `1px solid ${action === act ? '#10B981' : '#1E293B'}`,
                    background: action === act ? 'rgba(16, 185, 129, 0.15)' : 'rgba(15, 23, 42, 0.6)',
                    color: action === act ? '#10B981' : '#94A3B8',
                    fontSize: '0.78rem',
                    fontWeight: 700,
                    cursor: 'pointer',
                  }}
                >
                  {act}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.75rem', color: '#94A3B8', fontWeight: 700, textTransform: 'uppercase', marginBottom: '6px' }}>
              Executive Rationale & Endorsement Notes
            </label>
            <textarea
              rows={3}
              value={rationale}
              onChange={(e) => setRationale(e.target.value)}
              style={{ width: '100%', padding: '10px 14px', background: 'rgba(15, 23, 42, 0.8)', border: '1px solid #1E293B', borderRadius: '6px', color: '#FFFFFF', fontSize: '0.85rem', outline: 'none' }}
            />
          </div>

          <div style={{ display: 'flex', gap: '10px', marginTop: '10px' }}>
            <button
              type="button"
              onClick={onClose}
              style={{ flex: 1, padding: '10px', background: 'rgba(30, 41, 59, 0.8)', border: '1px solid #334155', borderRadius: '6px', color: '#CBD5E1', fontSize: '0.82rem', fontWeight: 700, cursor: 'pointer' }}
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              style={{ flex: 1, padding: '10px', background: '#0284C7', border: 'none', borderRadius: '6px', color: '#FFFFFF', fontSize: '0.82rem', fontWeight: 700, cursor: isSubmitting ? 'not-allowed' : 'pointer' }}
            >
              {isSubmitting ? 'Signing...' : 'Record Formal Sign-Off'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
