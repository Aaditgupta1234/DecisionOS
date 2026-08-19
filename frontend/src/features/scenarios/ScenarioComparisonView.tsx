import React from 'react';
import {
  GitCompare,
  TrendingUp,
  CheckCircle2,
  DollarSign,
  ShieldAlert,
  ArrowUpRight,
  Download,
  Layers,
  Sparkles,
} from 'lucide-react';

export const ScenarioComparisonView: React.FC = () => {
  const scenarios = [
    {
      name: 'Scenario A: Retention First',
      badge: '★ Recommended Scenario (Score 92.4)',
      type: 'RETENTION_FIRST',
      arr: '+$124,000',
      health: '+11.0 pts',
      risk: '-10.2 pts',
      cost: '$25,800',
      roi: '4.8x ROI',
      winProb: '94%',
      confidence: '91.0%',
      isWinner: true,
      desc: 'Focuses on Secondary Hub dispatch carrier rebalancing and automated 15% courier SLA penalties in Southeast corridors.',
    },
    {
      name: 'Scenario B: Growth Accelerator',
      badge: 'Score 81.6',
      type: 'GROWTH_OPTIMIZATION',
      arr: '+$98,000',
      health: '+7.5 pts',
      risk: '-6.4 pts',
      cost: '$30,500',
      roi: '3.2x ROI',
      winProb: '82%',
      confidence: '86.4%',
      isWinner: false,
      desc: 'Expands paid customer acquisition and seasonal promotional discounts across regional shipping tiers.',
    },
    {
      name: 'Scenario C: Maximum Efficiency',
      badge: 'Score 77.2',
      type: 'EFFICIENCY_BOOST',
      arr: '+$72,000',
      health: '+5.2 pts',
      risk: '-8.1 pts',
      cost: '$18,900',
      roi: '3.8x ROI',
      winProb: '88%',
      confidence: '89.0%',
      isWinner: false,
      desc: 'Automates support workflows and consolidates freight loads across regional warehouse distribution hubs.',
    },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', paddingBottom: '40px' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <div style={{ fontSize: '0.72rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: '#10B981', fontWeight: 800 }}>
            Pareto Frontier Evaluation Layer
          </div>
          <h1 style={{ fontSize: '1.8rem', fontWeight: 900, color: '#FFFFFF', margin: '4px 0 0 0' }}>
            Multi-Scenario Comparison Matrix
          </h1>
        </div>

        <button
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            padding: '8px 16px',
            background: '#0284C7',
            border: 'none',
            borderRadius: '8px',
            color: '#FFFFFF',
            fontSize: '0.8rem',
            fontWeight: 800,
            cursor: 'pointer',
          }}
        >
          <Download size={14} />
          <span>Export Comparison Matrix (PDF/PPTX)</span>
        </button>
      </div>

      {/* Comparison Cards Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '20px' }}>
        {scenarios.map((scen, idx) => (
          <div
            key={idx}
            style={{
              background: '#090D14',
              border: `1px solid ${scen.isWinner ? '#10B981' : '#1E293B'}`,
              borderRadius: '14px',
              padding: '24px',
              display: 'flex',
              flexDirection: 'column',
              gap: '16px',
              position: 'relative',
              boxShadow: scen.isWinner ? '0 10px 30px rgba(16, 185, 129, 0.15)' : 'none',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <span
                style={{
                  fontSize: '0.72rem',
                  fontWeight: 800,
                  color: scen.isWinner ? '#10B981' : '#94A3B8',
                  background: scen.isWinner ? 'rgba(16, 185, 129, 0.15)' : 'rgba(15, 23, 42, 0.8)',
                  padding: '3px 8px',
                  borderRadius: '12px',
                }}
              >
                {scen.badge}
              </span>
              <span style={{ fontSize: '0.75rem', color: '#38BDF8', fontWeight: 700 }}>
                {scen.confidence} Certainty
              </span>
            </div>

            <div>
              <h3 style={{ fontSize: '1.2rem', fontWeight: 900, color: '#FFFFFF', margin: '0 0 6px 0' }}>
                {scen.name}
              </h3>
              <p style={{ fontSize: '0.82rem', color: '#94A3B8', lineHeight: 1.4, margin: 0 }}>
                {scen.desc}
              </p>
            </div>

            {/* Metric Comparison Table */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '10px', background: 'rgba(15, 23, 42, 0.6)', border: '1px solid #1E293B', padding: '12px', borderRadius: '8px' }}>
              <div>
                <div style={{ fontSize: '0.65rem', color: '#64748B' }}>EXPECTED ARR</div>
                <div style={{ fontSize: '1.2rem', fontWeight: 900, color: '#38BDF8', marginTop: '2px' }}>{scen.arr}</div>
              </div>
              <div>
                <div style={{ fontSize: '0.65rem', color: '#64748B' }}>ROI MULTIPLIER</div>
                <div style={{ fontSize: '1.2rem', fontWeight: 900, color: '#10B981', marginTop: '2px' }}>{scen.roi}</div>
              </div>
              <div>
                <div style={{ fontSize: '0.65rem', color: '#64748B' }}>HEALTH LIFT</div>
                <div style={{ fontSize: '1.1rem', fontWeight: 800, color: '#FFFFFF', marginTop: '2px' }}>{scen.health}</div>
              </div>
              <div>
                <div style={{ fontSize: '0.65rem', color: '#64748B' }}>WIN PROBABILITY</div>
                <div style={{ fontSize: '1.1rem', fontWeight: 800, color: '#A855F7', marginTop: '2px' }}>{scen.winProb}</div>
              </div>
            </div>

            <button
              style={{
                marginTop: 'auto',
                padding: '10px',
                background: scen.isWinner ? '#10B981' : 'rgba(30, 41, 59, 0.8)',
                border: 'none',
                borderRadius: '8px',
                color: scen.isWinner ? '#090D14' : '#FFFFFF',
                fontSize: '0.82rem',
                fontWeight: 800,
                cursor: 'pointer',
              }}
            >
              {scen.isWinner ? 'Ratify Recommended Scenario' : 'Select for Simulation'}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};
