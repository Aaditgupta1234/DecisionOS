import React from 'react';
import { Sliders, TrendingUp, BarChart3, ShieldCheck, Target, ArrowRight } from 'lucide-react';

export const SensitivityAnalysisView: React.FC = () => {
  const drivers = [
    {
      name: 'Customer Retention Rate (±5%)',
      elasticity: '0.91 (Most Sensitive)',
      downside: '-$34,000',
      upside: '+$48,000',
      color: '#10B981',
      rank: 1,
    },
    {
      name: 'Courier SLA Compliance (±10%)',
      elasticity: '0.78 (High Sensitivity)',
      downside: '-$26,000',
      upside: '+$32,000',
      color: '#38BDF8',
      rank: 2,
    },
    {
      name: 'Win-Back Incentive Spend (±20%)',
      elasticity: '0.45 (Moderate)',
      downside: '-$12,000',
      upside: '+$18,000',
      color: '#A855F7',
      rank: 3,
    },
    {
      name: 'Support Team Headcount (±15%)',
      elasticity: '0.28 (Low Sensitivity)',
      downside: '-$6,000',
      upside: '+$8,000',
      color: '#F59E0B',
      rank: 4,
    },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', paddingBottom: '40px' }}>
      {/* Header */}
      <div>
        <div style={{ fontSize: '0.72rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: '#10B981', fontWeight: 800 }}>
          Parametric Elasticity & Critical Lever Identification
        </div>
        <h1 style={{ fontSize: '1.8rem', fontWeight: 900, color: '#FFFFFF', margin: '4px 0 0 0' }}>
          Sensitivity Analysis & Tornado Chart
        </h1>
      </div>

      {/* Driver Elasticity Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px' }}>
        {drivers.map((d) => (
          <div
            key={d.rank}
            style={{
              background: '#090D14',
              border: '1px solid #1E293B',
              borderRadius: '12px',
              padding: '20px',
              display: 'flex',
              flexDirection: 'column',
              gap: '10px',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <span style={{ fontSize: '0.72rem', fontWeight: 800, color: '#38BDF8', background: 'rgba(56, 189, 248, 0.12)', padding: '2px 8px', borderRadius: '4px' }}>
                Rank #{d.rank}
              </span>
              <span style={{ fontSize: '0.75rem', fontWeight: 800, color: d.color }}>
                {d.elasticity}
              </span>
            </div>

            <div style={{ fontSize: '1rem', fontWeight: 800, color: '#FFFFFF' }}>{d.name}</div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '8px', background: 'rgba(15, 23, 42, 0.6)', border: '1px solid #1E293B', padding: '10px', borderRadius: '6px' }}>
              <div>
                <div style={{ fontSize: '0.65rem', color: '#64748B' }}>DOWNSIDE SWING</div>
                <div style={{ fontSize: '0.95rem', fontWeight: 800, color: '#EF4444', marginTop: '2px' }}>{d.downside}</div>
              </div>
              <div>
                <div style={{ fontSize: '0.65rem', color: '#64748B' }}>UPSIDE SWING</div>
                <div style={{ fontSize: '0.95rem', fontWeight: 800, color: '#10B981', marginTop: '2px' }}>{d.upside}</div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
