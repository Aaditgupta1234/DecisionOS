import React from 'react';
import { ArrowUpRight, ArrowDownRight, ShieldCheck, Minus } from 'lucide-react';

interface Props {
  name: string;
  value: string | number;
  changePct?: number;
  trend?: 'up' | 'down' | 'neutral';
  confidence?: number;
  category?: string;
  unit?: string;
  periodLabel?: string;
}

export const MetricCard: React.FC<Props> = ({
  name,
  value,
  changePct,
  trend = 'up',
  confidence = 95,
  category,
  unit,
  periodLabel = 'vs previous period',
}) => {
  const isPositive = trend === 'up';
  const isNegative = trend === 'down';

  return (
    <div style={{
      background: '#090C12',
      border: '1px solid #1A2230',
      borderRadius: '10px',
      padding: '16px',
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'space-between',
      transition: 'border-color 0.15s ease',
    }}>
      {/* Header with Category & Confidence */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
        <span style={{ fontSize: '11px', fontWeight: 600, color: '#727A86', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
          {name}
        </span>
        {confidence && (
          <span style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '3px',
            fontSize: '9.5px',
            fontWeight: 700,
            color: '#38BDF8',
            background: 'rgba(56, 189, 248, 0.08)',
            padding: '1px 5px',
            borderRadius: '4px',
          }}>
            <ShieldCheck size={10} />
            <span>{confidence}%</span>
          </span>
        )}
      </div>

      {/* Main Metric Value */}
      <div style={{ fontSize: '24px', fontWeight: 800, color: '#FFFFFF', letterSpacing: '-0.02em', margin: '4px 0 8px' }}>
        {value}
        {unit && <span style={{ fontSize: '12px', color: '#64748B', fontWeight: 600, marginLeft: '3px' }}>{unit}</span>}
      </div>

      {/* Delta Trend Indicator */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '5px', fontSize: '11px' }}>
        {changePct !== undefined ? (
          <>
            <span style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '2px',
              fontWeight: 700,
              color: isPositive ? '#10B981' : isNegative ? '#EF4444' : '#94A3B8',
            }}>
              {isPositive ? <ArrowUpRight size={13} /> : isNegative ? <ArrowDownRight size={13} /> : <Minus size={13} />}
              <span>{changePct > 0 ? `+${changePct.toFixed(1)}%` : `${changePct.toFixed(1)}%`}</span>
            </span>
            <span style={{ color: '#64748B', fontSize: '10.5px' }}>{periodLabel}</span>
          </>
        ) : (
          <span style={{ color: '#64748B', fontSize: '10.5px' }}>Calculated from dataset</span>
        )}
      </div>
    </div>
  );
};
