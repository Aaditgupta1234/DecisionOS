import React from 'react';
import { CheckCircle2, Clock, PlayCircle, XCircle } from 'lucide-react';

interface Props {
  notStartedCount?: number;
  inProgressCount?: number;
  completedCount?: number;
  dismissedCount?: number;
}

export const ActionStatusSummary: React.FC<Props> = ({
  notStartedCount = 4,
  inProgressCount = 1,
  completedCount = 1,
  dismissedCount = 0,
}) => {
  const total = notStartedCount + inProgressCount + completedCount + dismissedCount;

  return (
    <div style={{
      background: '#070A0F',
      border: '1px solid #141C28',
      borderRadius: '8px',
      padding: '12px 16px',
      marginBottom: '20px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      flexWrap: 'wrap',
      gap: '12px',
    }}>
      <div style={{ fontSize: '11px', color: '#64748B', textTransform: 'uppercase', fontWeight: 800, letterSpacing: '0.04em' }}>
        Executive Action Tracker ({total} Initiatives)
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '10px', fontSize: '11.5px' }}>
        <span style={{ color: '#94A3B8', display: 'flex', alignItems: 'center', gap: '4px' }}>
          <Clock size={13} color="#64748B" />
          <span>Not Started: <strong style={{ color: '#FFFFFF' }}>{notStartedCount}</strong></span>
        </span>

        <span style={{ color: '#38BDF8', display: 'flex', alignItems: 'center', gap: '4px' }}>
          <PlayCircle size={13} color="#38BDF8" />
          <span>In Progress: <strong style={{ color: '#FFFFFF' }}>{inProgressCount}</strong></span>
        </span>

        <span style={{ color: '#10B981', display: 'flex', alignItems: 'center', gap: '4px' }}>
          <CheckCircle2 size={13} color="#10B981" />
          <span>Completed: <strong style={{ color: '#FFFFFF' }}>{completedCount}</strong></span>
        </span>
      </div>
    </div>
  );
};
