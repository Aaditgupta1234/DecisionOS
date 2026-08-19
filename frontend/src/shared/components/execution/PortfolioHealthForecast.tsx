import React from 'react';
import { Activity, TrendingUp, Sparkles, Compass } from 'lucide-react';

interface Props {
  currentScore?: number;
  projectedBase?: number;
  projectedBestCase?: number;
  projectedConservative?: number;
}

export const PortfolioHealthForecast: React.FC<Props> = ({
  currentScore = 82,
  projectedBase = 88,
  projectedBestCase = 91,
  projectedConservative = 84,
}) => {
  return (
    <div style={{
      background: 'linear-gradient(135deg, #0B111A 0%, #06090F 100%)',
      border: '1px solid #1E293B',
      borderRadius: '12px',
      padding: '20px',
      marginBottom: '24px',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Compass size={16} color="#38BDF8" />
          <h3 style={{ fontSize: '14.5px', fontWeight: 800, color: '#FFFFFF', margin: 0, textTransform: 'uppercase' }}>
            Portfolio Health Forecast & Scenario Modeling
          </h3>
        </div>
        <span style={{ fontSize: '10.5px', color: '#38BDF8', fontWeight: 700 }}>
          Where is the business heading?
        </span>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '12px' }}>
        <div style={{ background: '#05070B', border: '1px solid #141C28', borderRadius: '8px', padding: '12px 14px' }}>
          <span style={{ fontSize: '10px', color: '#64748B', textTransform: 'uppercase', fontWeight: 700 }}>Current Baseline</span>
          <div style={{ fontSize: '20px', fontWeight: 800, color: '#FFFFFF', marginTop: '2px' }}>{currentScore} / 100</div>
          <span style={{ fontSize: '10.5px', color: '#94A3B8' }}>Verified Health Score</span>
        </div>

        <div style={{ background: '#05070B', border: '1px solid rgba(56, 189, 248, 0.3)', borderRadius: '8px', padding: '12px 14px' }}>
          <span style={{ fontSize: '10px', color: '#38BDF8', textTransform: 'uppercase', fontWeight: 700 }}>Base Projection</span>
          <div style={{ fontSize: '20px', fontWeight: 800, color: '#38BDF8', marginTop: '2px' }}>{projectedBase} / 100</div>
          <span style={{ fontSize: '10.5px', color: '#10B981' }}>+6 pts expected lift</span>
        </div>

        <div style={{ background: '#05070B', border: '1px solid rgba(16, 185, 129, 0.3)', borderRadius: '8px', padding: '12px 14px' }}>
          <span style={{ fontSize: '10px', color: '#10B981', textTransform: 'uppercase', fontWeight: 700 }}>Best-Case Ceiling</span>
          <div style={{ fontSize: '20px', fontWeight: 800, color: '#10B981', marginTop: '2px' }}>{projectedBestCase} / 100</div>
          <span style={{ fontSize: '10.5px', color: '#10B981' }}>All 6 initiatives succeed</span>
        </div>

        <div style={{ background: '#05070B', border: '1px solid #141C28', borderRadius: '8px', padding: '12px 14px' }}>
          <span style={{ fontSize: '10px', color: '#F59E0B', textTransform: 'uppercase', fontWeight: 700 }}>Conservative Floor</span>
          <div style={{ fontSize: '20px', fontWeight: 800, color: '#CBD5E1', marginTop: '2px' }}>{projectedConservative} / 100</div>
          <span style={{ fontSize: '10.5px', color: '#94A3B8' }}>High-confidence only</span>
        </div>
      </div>
    </div>
  );
};
