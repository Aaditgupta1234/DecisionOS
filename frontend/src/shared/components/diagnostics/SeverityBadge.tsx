import React from 'react';
import { AlertOctagon, AlertTriangle, Info, ShieldAlert } from 'lucide-react';

export type SeverityType = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | 'INFO';

interface Props {
  severity: SeverityType | string;
}

export const SeverityBadge: React.FC<Props> = ({ severity }) => {
  const norm = severity.toUpperCase();

  switch (norm) {
    case 'CRITICAL':
      return (
        <span style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '4px',
          background: 'rgba(239, 68, 68, 0.15)',
          border: '1px solid rgba(239, 68, 68, 0.35)',
          color: '#F87171',
          padding: '2px 7px',
          borderRadius: '4px',
          fontSize: '10.5px',
          fontWeight: 800,
          textTransform: 'uppercase',
          letterSpacing: '0.04em',
        }}>
          <AlertOctagon size={11} />
          <span>CRITICAL</span>
        </span>
      );
    case 'HIGH':
      return (
        <span style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '4px',
          background: 'rgba(245, 158, 11, 0.15)',
          border: '1px solid rgba(245, 158, 11, 0.35)',
          color: '#FBBF24',
          padding: '2px 7px',
          borderRadius: '4px',
          fontSize: '10.5px',
          fontWeight: 800,
          textTransform: 'uppercase',
          letterSpacing: '0.04em',
        }}>
          <AlertTriangle size={11} />
          <span>HIGH</span>
        </span>
      );
    case 'MEDIUM':
      return (
        <span style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '4px',
          background: 'rgba(56, 189, 248, 0.12)',
          border: '1px solid rgba(56, 189, 248, 0.28)',
          color: '#38BDF8',
          padding: '2px 7px',
          borderRadius: '4px',
          fontSize: '10.5px',
          fontWeight: 700,
          textTransform: 'uppercase',
          letterSpacing: '0.04em',
        }}>
          <ShieldAlert size={11} />
          <span>MEDIUM</span>
        </span>
      );
    default:
      return (
        <span style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '4px',
          background: 'rgba(148, 163, 184, 0.1)',
          border: '1px solid rgba(148, 163, 184, 0.2)',
          color: '#94A3B8',
          padding: '2px 7px',
          borderRadius: '4px',
          fontSize: '10.5px',
          fontWeight: 600,
          textTransform: 'uppercase',
          letterSpacing: '0.04em',
        }}>
          <Info size={11} />
          <span>{norm || 'LOW'}</span>
        </span>
      );
  }
};
