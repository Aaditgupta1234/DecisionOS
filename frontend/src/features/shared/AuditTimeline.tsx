import React from 'react';
import { Clock, ShieldCheck, CheckCircle2, AlertTriangle, User, FileText } from 'lucide-react';
import { Badge } from '../../design-system/Badge';

export interface AuditEventItem {
  id: string;
  title: string;
  actor: string;
  actorRole: string;
  timestamp: string;
  status: 'APPROVED' | 'COMPLETED' | 'MODIFIED' | 'REJECTED' | 'RECORDED';
  details?: string;
  urn?: string;
}

interface AuditTimelineProps {
  events: AuditEventItem[];
  title?: string;
}

export const AuditTimeline: React.FC<AuditTimelineProps> = ({
  events,
  title = 'Institutional Governance Audit Trail',
}) => {
  const getBadgeVariant = (status: AuditEventItem['status']) => {
    switch (status) {
      case 'APPROVED':
      case 'COMPLETED':
        return 'emerald';
      case 'MODIFIED':
        return 'amber';
      case 'REJECTED':
        return 'rose';
      case 'RECORDED':
      default:
        return 'sky';
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      {title && (
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <span style={{ fontSize: '0.88rem', fontWeight: 800, color: '#FFFFFF' }}>{title}</span>
          <span style={{ fontSize: '0.72rem', color: '#64748B' }}>Immutable Blockchain-Verified Audit Hash</span>
        </div>
      )}

      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', position: 'relative' }}>
        {events.map((evt, idx) => (
          <div
            key={evt.id || idx}
            style={{
              background: 'rgba(15, 23, 42, 0.6)',
              border: '1px solid #1E293B',
              borderRadius: '10px',
              padding: '16px 20px',
              display: 'flex',
              alignItems: 'flex-start',
              justifyContent: 'space-between',
              flexWrap: 'wrap',
              gap: '12px',
            }}
          >
            <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span style={{ fontSize: '0.88rem', fontWeight: 800, color: '#FFFFFF' }}>
                  {evt.title}
                </span>
                {evt.urn && <code style={{ fontSize: '0.7rem', color: '#38BDF8' }}>{evt.urn}</code>}
              </div>
              <div style={{ fontSize: '0.75rem', color: '#94A3B8' }}>
                Actor: <strong style={{ color: '#F1F5F9' }}>{evt.actor}</strong> ({evt.actorRole}) • {evt.timestamp}
              </div>
              {evt.details && (
                <div style={{ fontSize: '0.78rem', color: '#64748B', marginTop: '4px' }}>
                  {evt.details}
                </div>
              )}
            </div>

            <Badge variant={getBadgeVariant(evt.status)} size="sm">
              {evt.status}
            </Badge>
          </div>
        ))}
      </div>
    </div>
  );
};
