import React from 'react';
import { ShieldCheck, TrendingUp, Zap, ArrowRight, Clock } from 'lucide-react';

export type RecommendationStatusType = 'NOT_STARTED' | 'IN_PROGRESS' | 'COMPLETED' | 'DISMISSED';

interface Props {
  id: string;
  title: string;
  actionSummary: string;
  priority?: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  difficulty?: 'LOW' | 'MEDIUM' | 'HIGH';
  confidence?: number;
  expectedRecovery?: string;
  status?: RecommendationStatusType | string;
  timeToValue?: string;
  onOpenDrawer?: (id: string) => void;
}

export const RecommendationCard: React.FC<Props> = ({
  id,
  title,
  actionSummary,
  priority = 'HIGH',
  difficulty = 'LOW',
  confidence = 92,
  expectedRecovery = '+$180K ARR',
  status = 'NOT_STARTED',
  timeToValue = '2–3 weeks',
  onOpenDrawer,
}) => {
  const isHigh = priority === 'HIGH' || priority === 'CRITICAL';

  return (
    <div style={{
      background: '#090C12',
      border: '1px solid #1A2230',
      borderRadius: '10px',
      padding: '18px 20px',
      marginBottom: '12px',
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'space-between',
      transition: 'border-color 0.15s ease',
    }}>
      <div>
        {/* Header Badges */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{
              fontSize: '10px',
              fontWeight: 800,
              color: isHigh ? '#F59E0B' : '#38BDF8',
              background: isHigh ? 'rgba(245, 158, 11, 0.12)' : 'rgba(56, 189, 248, 0.12)',
              border: `1px solid ${isHigh ? 'rgba(245, 158, 11, 0.28)' : 'rgba(56, 189, 248, 0.28)'}`,
              padding: '1px 6px',
              borderRadius: '4px',
            }}>
              {priority} PRIORITY
            </span>

            <span style={{
              fontSize: '10px',
              fontWeight: 700,
              color: '#94A3B8',
              background: '#070A0F',
              border: '1px solid #141C28',
              padding: '1px 6px',
              borderRadius: '4px',
            }}>
              {difficulty} DIFFICULTY
            </span>

            {/* Read-Only Status Badge */}
            <span style={{
              fontSize: '9.5px',
              fontWeight: 700,
              color: status === 'COMPLETED' ? '#10B981' : status === 'IN_PROGRESS' ? '#38BDF8' : '#64748B',
              background: 'rgba(255, 255, 255, 0.04)',
              padding: '1px 6px',
              borderRadius: '4px',
            }}>
              STATUS: {status}
            </span>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '10.5px', color: '#38BDF8', fontWeight: 700 }}>
            <ShieldCheck size={12} />
            <span>{confidence}% Confidence</span>
          </div>
        </div>

        {/* Title & Summary */}
        <h3 style={{ fontSize: '15px', fontWeight: 800, color: '#FFFFFF', letterSpacing: '-0.01em', marginBottom: '6px' }}>
          {title}
        </h3>

        <p style={{ fontSize: '12.5px', color: '#CBD5E1', lineHeight: 1.5, marginBottom: '14px' }}>
          {actionSummary}
        </p>
      </div>

      {/* Footer Strip */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        borderTop: '1px solid #141C28',
        paddingTop: '12px',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div>
            <span style={{ fontSize: '10px', color: '#64748B', textTransform: 'uppercase', display: 'block' }}>Expected ARR Recovery</span>
            <span style={{ fontSize: '15px', fontWeight: 800, color: '#10B981' }}>{expectedRecovery}</span>
          </div>

          <div style={{ width: '1px', height: '24px', background: '#141C28' }} />

          <div style={{ display: 'flex', alignItems: 'center', gap: '4px', color: '#94A3B8', fontSize: '11px' }}>
            <Clock size={12} />
            <span>Time to Value: {timeToValue}</span>
          </div>
        </div>

        <button
          type="button"
          onClick={() => onOpenDrawer && onOpenDrawer(id)}
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '6px',
            background: '#111622',
            border: '1px solid #1F2738',
            color: '#38BDF8',
            padding: '6px 12px',
            borderRadius: '6px',
            fontSize: '12px',
            fontWeight: 700,
            cursor: 'pointer',
          }}
        >
          <span>Inspect Execution Plan</span>
          <ArrowRight size={12} />
        </button>
      </div>
    </div>
  );
};
