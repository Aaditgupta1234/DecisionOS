import React from 'react';
import { History, User, CheckCircle2, Calendar, PlayCircle } from 'lucide-react';

interface AuditEvent {
  timestamp: string;
  action: string;
  actor: string;
  details: string;
}

interface Props {
  events?: AuditEvent[];
}

export const InitiativeAuditTimeline: React.FC<Props> = ({
  events = [
    { timestamp: 'Aug 27, 2026 • 16:45 UTC', action: 'Milestone Completed', actor: 'Marcus Vance (VP Customer Success)', details: 'Marked "Audience Segmentation & Courier SLAs" milestone as completed.' },
    { timestamp: 'Aug 24, 2026 • 11:20 UTC', action: 'Status Transition', actor: 'Elena Rostova (CEO)', details: 'Transitioned initiative status from NOT_STARTED → IN_PROGRESS.' },
    { timestamp: 'Aug 20, 2026 • 09:15 UTC', action: 'Initiative Created', actor: 'DecisionOS Engine', details: 'Initialized INIT-2026-001 from Recommendation #1 (Targeted Win-Back Campaign).' },
  ],
}) => {
  return (
    <div style={{
      background: '#090C12',
      border: '1px solid #1A2230',
      borderRadius: '12px',
      padding: '20px',
      marginBottom: '24px',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '14px' }}>
        <History size={16} color="#38BDF8" />
        <h4 style={{ fontSize: '13.5px', fontWeight: 800, color: '#FFFFFF', margin: 0, textTransform: 'uppercase' }}>
          Initiative Governance & State Audit History
        </h4>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
        {events.map((ev, idx) => (
          <div
            key={idx}
            style={{
              background: '#05070B',
              border: '1px solid #141C28',
              borderRadius: '6px',
              padding: '10px 14px',
              display: 'flex',
              alignItems: 'flex-start',
              justifyContent: 'space-between',
            }}
          >
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '2px' }}>
                <span style={{ fontSize: '12px', fontWeight: 700, color: '#38BDF8' }}>{ev.action}</span>
                <span style={{ fontSize: '11px', color: '#64748B' }}>by {ev.actor}</span>
              </div>
              <p style={{ fontSize: '11.5px', color: '#CBD5E1', margin: 0 }}>
                {ev.details}
              </p>
            </div>

            <span style={{ fontSize: '10.5px', color: '#64748B', flexShrink: 0, marginLeft: '12px' }}>
              {ev.timestamp}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};
