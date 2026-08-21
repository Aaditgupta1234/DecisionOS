import React from 'react';
import { ShieldCheck, Activity, TrendingUp, Users, Truck } from 'lucide-react';

interface Props {
  score?: number;
  status?: string;
  confidence?: number;
  financialScore?: number;
  customerScore?: number;
  operationalScore?: number;
}

export const HealthScoreHeroCard: React.FC<Props> = ({
  score = 0,
  status = 'HEALTHY',
  confidence = 90,
  financialScore = 0,
  customerScore = 0,
  operationalScore = 0,
}) => {
  return (
    <div style={{
      background: 'linear-gradient(135deg, #0A0E17 0%, #06080D 100%)',
      border: '1px solid #1E293B',
      borderRadius: '14px',
      padding: '24px 28px',
      boxShadow: '0 20px 40px rgba(0, 0, 0, 0.7), inset 0 1px 0 rgba(255, 255, 255, 0.08)',
      display: 'grid',
      gridTemplateColumns: '1.4fr 1.6fr',
      gap: '28px',
      alignItems: 'center',
      marginBottom: '24px',
      position: 'relative',
      overflow: 'hidden',
    }}>
      {/* Background Subtle Spotlight */}
      <div style={{
        position: 'absolute',
        top: '-40px',
        left: '-40px',
        width: '240px',
        height: '240px',
        background: 'radial-gradient(circle, rgba(16, 185, 129, 0.12) 0%, rgba(0,0,0,0) 70%)',
        pointerEvents: 'none',
      }} />

      {/* Left Column: Flagship Score & Radial Gauge */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '20px', borderRight: '1px solid #141C28', paddingRight: '20px' }}>
        {/* Radial Circle Gauge */}
        <div style={{ position: 'relative', width: '84px', height: '84px', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
          <svg width="84" height="84" viewBox="0 0 36 36">
            <path
              d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
              fill="none"
              stroke="rgba(255, 255, 255, 0.06)"
              strokeWidth="3.2"
            />
            <path
              d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
              fill="none"
              stroke="#10B981"
              strokeWidth="3.2"
              strokeDasharray={`${score}, 100`}
              strokeLinecap="round"
              style={{ filter: 'drop-shadow(0 0 8px rgba(16, 185, 129, 0.6))' }}
            />
          </svg>
          <div style={{ position: 'absolute', textAlign: 'center' }}>
            <span style={{ fontSize: '20px', fontWeight: 800, color: '#FFFFFF', letterSpacing: '-0.02em' }}>{score}</span>
            <span style={{ display: 'block', fontSize: '8.5px', color: '#64748B', fontWeight: 700 }}>/ 100</span>
          </div>
        </div>

        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '4px' }}>
            <ShieldCheck size={14} color="#10B981" />
            <span style={{ fontSize: '11px', fontWeight: 700, color: '#94A3B8', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
              Business Health Score
            </span>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
            <span style={{ fontSize: '18px', fontWeight: 800, color: '#10B981', letterSpacing: '-0.01em' }}>
              {status}
            </span>
            <span style={{ fontSize: '10.5px', fontWeight: 700, color: '#38BDF8', background: 'rgba(56, 189, 248, 0.12)', border: '1px solid rgba(56, 189, 248, 0.28)', padding: '1px 7px', borderRadius: '4px' }}>
              {confidence}% Confidence
            </span>
          </div>

          <p style={{ fontSize: '11.5px', color: '#64748B', lineHeight: 1.4, margin: 0 }}>
            Deterministic composite evaluation across growth, customer retention, and operations.
          </p>
        </div>
      </div>

      {/* Right Column: 3 Pillar Breakdown */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '14px' }}>
        {/* Pillar 1: Financial Health */}
        <div style={{ background: '#070A0F', border: '1px solid #141C28', borderRadius: '8px', padding: '12px 14px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '5px', color: '#94A3B8', fontSize: '11px', fontWeight: 600 }}>
              <TrendingUp size={12} color="#38BDF8" />
              <span>Financial</span>
            </div>
            <span style={{ fontSize: '13px', fontWeight: 800, color: '#FFFFFF' }}>{financialScore}</span>
          </div>
          <div style={{ width: '100%', height: '4px', background: '#1E293B', borderRadius: '2px', overflow: 'hidden' }}>
            <div style={{ width: `${financialScore}%`, height: '100%', background: '#38BDF8' }} />
          </div>
          <span style={{ fontSize: '9px', color: '#64748B', marginTop: '4px', display: 'block' }}>Strong revenue growth</span>
        </div>

        {/* Pillar 2: Customer Health */}
        <div style={{ background: '#070A0F', border: '1px solid #141C28', borderRadius: '8px', padding: '12px 14px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '5px', color: '#94A3B8', fontSize: '11px', fontWeight: 600 }}>
              <Users size={12} color="#F59E0B" />
              <span>Customer</span>
            </div>
            <span style={{ fontSize: '13px', fontWeight: 800, color: '#FFFFFF' }}>{customerScore}</span>
          </div>
          <div style={{ width: '100%', height: '4px', background: '#1E293B', borderRadius: '2px', overflow: 'hidden' }}>
            <div style={{ width: `${customerScore}%`, height: '100%', background: '#F59E0B' }} />
          </div>
          <span style={{ fontSize: '9px', color: '#64748B', marginTop: '4px', display: 'block' }}>Retention risk (-4.2%)</span>
        </div>

        {/* Pillar 3: Operational Health */}
        <div style={{ background: '#070A0F', border: '1px solid #141C28', borderRadius: '8px', padding: '12px 14px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '5px', color: '#94A3B8', fontSize: '11px', fontWeight: 600 }}>
              <Truck size={12} color="#10B981" />
              <span>Operational</span>
            </div>
            <span style={{ fontSize: '13px', fontWeight: 800, color: '#FFFFFF' }}>{operationalScore}</span>
          </div>
          <div style={{ width: '100%', height: '4px', background: '#1E293B', borderRadius: '2px', overflow: 'hidden' }}>
            <div style={{ width: `${operationalScore}%`, height: '100%', background: '#10B981' }} />
          </div>
          <span style={{ fontSize: '9px', color: '#64748B', marginTop: '4px', display: 'block' }}>3.4 day fulfillment</span>
        </div>
      </div>
    </div>
  );
};
