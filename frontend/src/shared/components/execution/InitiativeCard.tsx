import React from 'react';
import { User, Calendar, TrendingUp, AlertCircle, ArrowRight, ShieldCheck, CheckCircle2, Clock } from 'lucide-react';
import { Link } from 'react-router-dom';

export type InitiativeStatus = 'NOT_STARTED' | 'IN_PROGRESS' | 'BLOCKED' | 'COMPLETED' | 'DISMISSED';

export interface InitiativeItem {
  id: string;
  code: string;
  title: string;
  owner: string;
  department: string;
  priority: 'CRITICAL' | 'HIGH' | 'MEDIUM';
  status: InitiativeStatus;
  targetDate: string;
  predictedRecovery: string;
  actualRecovery: string;
  achievementRate: number;
  blockedBy?: string;
}

interface Props {
  initiative: InitiativeItem;
  onMoveStatus?: (id: string, newStatus: InitiativeStatus) => void;
}

export const InitiativeCard: React.FC<Props> = ({ initiative, onMoveStatus }) => {
  const getStatusColor = (st: InitiativeStatus) => {
    switch (st) {
      case 'COMPLETED':
        return '#10B981';
      case 'IN_PROGRESS':
        return '#38BDF8';
      case 'BLOCKED':
        return '#EF4444';
      case 'DISMISSED':
        return '#64748B';
      case 'NOT_STARTED':
      default:
        return '#F59E0B';
    }
  };

  const statusColor = getStatusColor(initiative.status);

  return (
    <div style={{
      background: '#070A0F',
      border: `1px solid ${initiative.status === 'BLOCKED' ? 'rgba(239, 68, 68, 0.4)' : '#141C28'}`,
      borderRadius: '8px',
      padding: '14px',
      marginBottom: '10px',
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'space-between',
      boxShadow: '0 4px 12px rgba(0, 0, 0, 0.5)',
      transition: 'all 0.15s ease',
    }}>
      <div>
        {/* Header: Code & Priority */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px' }}>
          <span style={{ fontSize: '10px', fontWeight: 800, color: '#38BDF8', fontFamily: 'monospace' }}>
            {initiative.code}
          </span>

          <span style={{
            fontSize: '9px',
            fontWeight: 800,
            color: initiative.priority === 'CRITICAL' ? '#EF4444' : '#F59E0B',
            background: 'rgba(255, 255, 255, 0.04)',
            padding: '1px 5px',
            borderRadius: '4px',
          }}>
            {initiative.priority}
          </span>
        </div>

        {/* Title */}
        <Link
          to={`/initiatives/${initiative.id}`}
          style={{
            fontSize: '12.5px',
            fontWeight: 700,
            color: '#FFFFFF',
            lineHeight: 1.35,
            textDecoration: 'none',
            display: 'block',
            marginBottom: '8px',
          }}
        >
          {initiative.title}
        </Link>

        {/* Dependency Blocker Tag if any */}
        {initiative.blockedBy && (
          <div style={{
            background: 'rgba(239, 68, 68, 0.1)',
            border: '1px solid rgba(239, 68, 68, 0.3)',
            borderRadius: '4px',
            padding: '3px 6px',
            fontSize: '10px',
            color: '#F87171',
            fontWeight: 600,
            marginBottom: '8px',
            display: 'flex',
            alignItems: 'center',
            gap: '4px',
          }}>
            <AlertCircle size={11} />
            <span>Blocked by: {initiative.blockedBy}</span>
          </div>
        )}

        {/* Owner & Department */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '5px', fontSize: '11px', color: '#94A3B8', marginBottom: '10px' }}>
          <User size={12} color="#64748B" />
          <span>{initiative.owner}</span>
          <span style={{ color: '#475569' }}>•</span>
          <span style={{ color: '#64748B' }}>{initiative.department}</span>
        </div>
      </div>

      {/* Progress & Realized vs Predicted Recovery */}
      <div style={{ borderTop: '1px solid #101620', paddingTop: '10px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '4px' }}>
          <span style={{ fontSize: '10px', color: '#64748B', textTransform: 'uppercase' }}>Target Recovery</span>
          <span style={{ fontSize: '11.5px', fontWeight: 800, color: '#10B981' }}>
            {initiative.actualRecovery !== '$0' ? `${initiative.actualRecovery} / ` : ''}{initiative.predictedRecovery}
          </span>
        </div>

        {/* Progress Bar */}
        <div style={{ width: '100%', height: '4px', background: '#111827', borderRadius: '2px', overflow: 'hidden', marginBottom: '8px' }}>
          <div style={{ width: `${Math.min(100, initiative.achievementRate)}%`, height: '100%', background: statusColor }} />
        </div>

        {/* Footer Target Date & Detail Link */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '10.5px' }}>
          <span style={{ color: '#64748B', display: 'flex', alignItems: 'center', gap: '3px' }}>
            <Calendar size={11} />
            <span>{initiative.targetDate}</span>
          </span>

          <Link
            to={`/initiatives/${initiative.id}`}
            style={{
              color: '#38BDF8',
              fontWeight: 700,
              textDecoration: 'none',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '2px',
            }}
          >
            <span>Open</span>
            <ArrowRight size={10} />
          </Link>
        </div>
      </div>
    </div>
  );
};
