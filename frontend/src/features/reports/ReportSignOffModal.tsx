import React, { useState } from 'react';
import { X, CheckCircle2, ShieldCheck, AlertCircle, FileCheck, History } from 'lucide-react';

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
  reportTitle = 'DecisionOS Comprehensive Boardroom Governance Report',
}) => {
  const [role, setRole] = useState('CEO');
  const [approverName, setApproverName] = useState('Chief Executive Officer');
  const [targetStatus, setTargetStatus] = useState<'DRAFT' | 'UNDER_REVIEW' | 'APPROVED' | 'REJECTED' | 'ARCHIVED'>('APPROVED');
  const [comments, setComments] = useState('All findings, causal lineages, and ARR impact projections verified against deterministic telemetry.');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const approvalHistory = [
    { role: 'COO / VP Logistics', name: 'Chief Operating Officer', action: 'REVIEWED', date: '2026-08-24 14:15 UTC', notes: 'Verified courier SLAs.' },
    { role: 'CFO', name: 'Chief Financial Officer', action: 'REVIEWED', date: '2026-08-24 14:00 UTC', notes: 'Verified ROI calculations.' },
  ];

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setTimeout(() => {
      setIsSubmitting(false);
      if (onSignOffSuccess) onSignOffSuccess();
      onClose();
    }, 500);
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
          width: '600px',
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
        {/* Header */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '18px 24px', borderBottom: '1px solid #1E293B', background: '#070A0F' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <FileCheck size={18} color="#10B981" />
            <div>
              <span style={{ fontSize: '0.72rem', color: '#10B981', textTransform: 'uppercase', fontWeight: 800 }}>
                Executive Fiduciary Sign-Off Workflow
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
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
            <div>
              <label style={{ display: 'block', fontSize: '0.75rem', color: '#94A3B8', fontWeight: 700, textTransform: 'uppercase', marginBottom: '6px' }}>
                Sign-Off Role
              </label>
              <select
                value={role}
                onChange={(e) => {
                  setRole(e.target.value);
                  if (e.target.value === 'CEO') setApproverName('Chief Executive Officer');
                  else if (e.target.value === 'COO') setApproverName('Chief Operating Officer');
                  else if (e.target.value === 'CFO') setApproverName('Chief Financial Officer');
                  else setApproverName('Board Chairperson');
                }}
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
                Target Governance State
              </label>
              <select
                value={targetStatus}
                onChange={(e) => setTargetStatus(e.target.value as any)}
                style={{ width: '100%', padding: '10px 14px', background: 'rgba(15, 23, 42, 0.8)', border: '1px solid #1E293B', borderRadius: '6px', color: '#FFFFFF', fontSize: '0.85rem' }}
              >
                <option value="APPROVED">APPROVED (Formal Ratification)</option>
                <option value="UNDER_REVIEW">UNDER_REVIEW (Requested Edits)</option>
                <option value="REJECTED">REJECTED (Requires Revision)</option>
                <option value="DRAFT">DRAFT (Working Revision)</option>
                <option value="ARCHIVED">ARCHIVED (Historical Record)</option>
              </select>
            </div>
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.75rem', color: '#94A3B8', fontWeight: 700, textTransform: 'uppercase', marginBottom: '6px' }}>
              Executive Rationale & Sign-Off Comments
            </label>
            <textarea
              value={comments}
              onChange={(e) => setComments(e.target.value)}
              rows={3}
              style={{ width: '100%', padding: '10px 14px', background: 'rgba(15, 23, 42, 0.8)', border: '1px solid #1E293B', borderRadius: '6px', color: '#FFFFFF', fontSize: '0.85rem', resize: 'vertical' }}
            />
          </div>

          {/* Previous Approval History */}
          <div style={{ background: 'rgba(15, 23, 42, 0.5)', border: '1px solid #1E293B', borderRadius: '6px', padding: '12px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.72rem', fontWeight: 800, color: '#94A3B8', textTransform: 'uppercase' }}>
              <History size={13} /> Approval History Trail
            </div>
            {approvalHistory.map((item, idx) => (
              <div key={idx} style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.76rem', color: '#64748B' }}>
                <span><strong>{item.role}:</strong> {item.notes}</span>
                <span style={{ color: '#10B981', fontWeight: 600 }}>{item.date}</span>
              </div>
            ))}
          </div>

          {/* Submit */}
          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', marginTop: '6px' }}>
            <button
              type="button"
              onClick={onClose}
              style={{ padding: '8px 16px', background: 'transparent', border: '1px solid #334155', borderRadius: '6px', color: '#94A3B8', fontSize: '0.82rem', fontWeight: 600, cursor: 'pointer' }}
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              style={{ padding: '8px 20px', background: '#10B981', border: 'none', borderRadius: '6px', color: '#090D14', fontSize: '0.82rem', fontWeight: 800, cursor: 'pointer' }}
            >
              {isSubmitting ? 'Recording Cryptographic Sign-Off...' : `Submit ${targetStatus} Sign-Off`}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
