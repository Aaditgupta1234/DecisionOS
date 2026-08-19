import React from 'react';
import { History, ShieldCheck, UserCheck, Calendar, Lock, AlertTriangle } from 'lucide-react';

export type AuditEventType =
  | 'STATUS_CHANGED'
  | 'OWNER_CHANGED'
  | 'PRIORITY_CHANGED'
  | 'TARGET_DATE_CHANGED'
  | 'RISK_ADDED'
  | 'RISK_RESOLVED'
  | 'BASELINE_CAPTURED';

export interface AuditActor {
  name: string;
  role: string;
  email?: string;
}

export interface EnterpriseAuditEvent {
  id: string;
  timestamp: string;
  eventType: AuditEventType;
  actionTitle: string;
  performedBy: AuditActor;
  details: string;
  hashSignature?: string;
}

interface Props {
  events?: EnterpriseAuditEvent[];
}

export const InitiativeAuditTimeline: React.FC<Props> = ({
  events = [
    {
      id: 'aud_5',
      timestamp: '2026-08-27 16:45:12 UTC',
      eventType: 'RISK_RESOLVED',
      actionTitle: 'Execution Risk Mitigated',
      performedBy: { name: 'Marcus Vance', role: 'VP Customer Success' },
      details: 'Mitigated "Audience Credit Incentive Email Bounce Rates" risk after deploying zero-bounce email verification gateway.',
      hashSignature: 'sig_89f1...e02c',
    },
    {
      id: 'aud_4',
      timestamp: '2026-08-25 11:20:00 UTC',
      eventType: 'TARGET_DATE_CHANGED',
      actionTitle: 'Commitment Target Date Extended',
      performedBy: { name: 'Elena Rostova', role: 'Head of Logistics' },
      details: 'Adjusted target completion date from Sep 15 → Sep 22 to align with southeastern courier carrier contract review.',
      hashSignature: 'sig_44b2...91aa',
    },
    {
      id: 'aud_3',
      timestamp: '2026-08-24 10:15:30 UTC',
      eventType: 'STATUS_CHANGED',
      actionTitle: 'State Transition to IN_PROGRESS',
      performedBy: { name: 'Sarah Johnson', role: 'VP Customer Success' },
      details: 'Transitioned initiative status from NOT_STARTED → IN_PROGRESS after prerequisite dependency resolution.',
      hashSignature: 'sig_31c8...a811',
    },
    {
      id: 'aud_2',
      timestamp: '2026-08-18 09:15:00 UTC',
      eventType: 'BASELINE_CAPTURED',
      actionTitle: 'Immutable Baseline Snapshot Frozen',
      performedBy: { name: 'DecisionOS Engine', role: 'System Orchestrator' },
      details: 'Captured cryptographic telemetry baseline for dataset ds_olist_2026 (v14) with SHA-256 seal.',
      hashSignature: 'sig_11aa...77cc',
    },
    {
      id: 'aud_1',
      timestamp: '2026-08-18 09:00:00 UTC',
      eventType: 'OWNER_CHANGED',
      actionTitle: 'Initiative Ownership Assigned',
      performedBy: { name: 'Elena Rostova', role: 'Chief Executive Officer' },
      details: 'Assigned primary executive accountability to Marcus Vance (VP Customer Success).',
      hashSignature: 'sig_02da...55eb',
    },
  ],
}) => {
  const getEventBadgeColor = (type: AuditEventType) => {
    switch (type) {
      case 'STATUS_CHANGED':
        return '#38BDF8';
      case 'BASELINE_CAPTURED':
        return '#10B981';
      case 'RISK_RESOLVED':
        return '#10B981';
      case 'RISK_ADDED':
        return '#EF4444';
      case 'PRIORITY_CHANGED':
        return '#F59E0B';
      default:
        return '#94A3B8';
    }
  };

  return (
    <div style={{
      background: '#090C12',
      border: '1px solid #1A2230',
      borderRadius: '12px',
      padding: '20px',
      marginBottom: '24px',
    }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <History size={16} color="#38BDF8" />
          <h4 style={{ fontSize: '13.5px', fontWeight: 800, color: '#FFFFFF', margin: 0, textTransform: 'uppercase' }}>
            Enterprise State & Governance Audit Trail
          </h4>
        </div>

        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '5px',
          background: 'rgba(56, 189, 248, 0.1)',
          border: '1px solid rgba(56, 189, 248, 0.3)',
          color: '#38BDF8',
          padding: '3px 10px',
          borderRadius: '6px',
          fontSize: '11px',
          fontWeight: 700,
        }}>
          <Lock size={12} />
          <span>Append-Only • Tamper-Proof Audit Log</span>
        </div>
      </div>

      {/* Events List */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
        {events.map((ev) => {
          const badgeColor = getEventBadgeColor(ev.eventType);

          return (
            <div
              key={ev.id}
              style={{
                background: '#05070B',
                border: '1px solid #141C28',
                borderRadius: '8px',
                padding: '12px 14px',
                display: 'flex',
                alignItems: 'flex-start',
                justifyContent: 'space-between',
              }}
            >
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                  <span style={{
                    fontSize: '9.5px',
                    fontWeight: 800,
                    color: badgeColor,
                    background: 'rgba(255, 255, 255, 0.04)',
                    padding: '1px 6px',
                    borderRadius: '4px',
                    fontFamily: 'monospace',
                  }}>
                    {ev.eventType}
                  </span>
                  <span style={{ fontSize: '13px', fontWeight: 700, color: '#FFFFFF' }}>
                    {ev.actionTitle}
                  </span>
                </div>

                <p style={{ fontSize: '11.5px', color: '#CBD5E1', margin: '0 0 6px', lineHeight: 1.45 }}>
                  {ev.details}
                </p>

                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '11px', color: '#64748B' }}>
                  <span>Performed By:</span>
                  <strong style={{ color: '#94A3B8' }}>{ev.performedBy.name}</strong>
                  <span>({ev.performedBy.role})</span>
                </div>
              </div>

              <div style={{ textAlign: 'right', flexShrink: 0, marginLeft: '16px' }}>
                <span style={{ fontSize: '10.5px', color: '#64748B', display: 'block', marginBottom: '2px' }}>
                  {ev.timestamp}
                </span>
                {ev.hashSignature && (
                  <span style={{ fontSize: '9.5px', color: '#475569', fontFamily: 'monospace' }}>
                    {ev.hashSignature}
                  </span>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
