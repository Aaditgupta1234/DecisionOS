import React from 'react';
import { TrendingUp, Target, ShieldCheck, Activity, Award } from 'lucide-react';

interface Props {
  projectedRecovery?: string;
  actualRecovery?: string;
  remainingOpportunity?: string;
  healthScoreLift?: string;
  averageRoi?: string;
  achievementRate?: number;
}

export const OutcomeScorecard: React.FC<Props> = ({
  projectedRecovery = '+$480K ARR',
  actualRecovery = '+$124K ARR',
  remainingOpportunity = '+$356K ARR',
  healthScoreLift = '+5 pts (82 → 87)',
  averageRoi = '3.4x ROI',
  achievementRate = 25.8,
}) => {
  return (
    <div style={{
      background: 'linear-gradient(135deg, #090E17 0%, #06090F 100%)',
      border: '1px solid #1E293B',
      borderRadius: '12px',
      padding: '22px 24px',
      marginBottom: '24px',
      boxShadow: '0 12px 30px rgba(0, 0, 0, 0.6)',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '18px' }}>
        <div>
          <div style={{ fontSize: '10.5px', color: '#10B981', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
            Portfolio Recovery Command Center
          </div>
          <h3 style={{ fontSize: '16px', fontWeight: 800, color: '#FFFFFF', margin: '2px 0 0' }}>
            Realized Business Outcomes & Return on Investment
          </h3>
        </div>

        <div style={{
          background: 'rgba(16, 185, 129, 0.12)',
          border: '1px solid rgba(16, 185, 129, 0.3)',
          color: '#10B981',
          padding: '4px 12px',
          borderRadius: '6px',
          fontSize: '12px',
          fontWeight: 800,
        }}>
          {achievementRate}% Portfolio Realization
        </div>
      </div>

      {/* 5-Card Metrics Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '12px' }}>
        <div style={{ background: '#05070B', border: '1px solid #141C28', borderRadius: '8px', padding: '12px 14px' }}>
          <span style={{ fontSize: '10px', color: '#64748B', textTransform: 'uppercase', fontWeight: 700 }}>Total Target</span>
          <div style={{ fontSize: '16px', fontWeight: 800, color: '#FFFFFF', marginTop: '2px' }}>{projectedRecovery}</div>
        </div>

        <div style={{ background: '#05070B', border: '1px solid rgba(16, 185, 129, 0.3)', borderRadius: '8px', padding: '12px 14px' }}>
          <span style={{ fontSize: '10px', color: '#10B981', textTransform: 'uppercase', fontWeight: 700 }}>Actual Realized</span>
          <div style={{ fontSize: '16px', fontWeight: 800, color: '#10B981', marginTop: '2px' }}>{actualRecovery}</div>
        </div>

        <div style={{ background: '#05070B', border: '1px solid #141C28', borderRadius: '8px', padding: '12px 14px' }}>
          <span style={{ fontSize: '10px', color: '#64748B', textTransform: 'uppercase', fontWeight: 700 }}>Remaining Upside</span>
          <div style={{ fontSize: '16px', fontWeight: 800, color: '#38BDF8', marginTop: '2px' }}>{remainingOpportunity}</div>
        </div>

        <div style={{ background: '#05070B', border: '1px solid #141C28', borderRadius: '8px', padding: '12px 14px' }}>
          <span style={{ fontSize: '10px', color: '#64748B', textTransform: 'uppercase', fontWeight: 700 }}>Health Score Lift</span>
          <div style={{ fontSize: '16px', fontWeight: 800, color: '#FFFFFF', marginTop: '2px' }}>{healthScoreLift}</div>
        </div>

        <div style={{ background: '#05070B', border: '1px solid #141C28', borderRadius: '8px', padding: '12px 14px' }}>
          <span style={{ fontSize: '10px', color: '#64748B', textTransform: 'uppercase', fontWeight: 700 }}>Campaign Multiplier</span>
          <div style={{ fontSize: '16px', fontWeight: 800, color: '#F59E0B', marginTop: '2px' }}>{averageRoi}</div>
        </div>
      </div>
    </div>
  );
};
