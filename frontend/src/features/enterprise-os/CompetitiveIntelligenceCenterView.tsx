import React, { useState } from 'react';
import {
  TrendingUp,
  Award,
  Sparkles,
  ShieldCheck,
  CheckCircle2,
  ArrowRight,
  BarChart3,
  Layers,
  ArrowUpRight,
} from 'lucide-react';
import { Link } from 'react-router-dom';

export const CompetitiveIntelligenceCenterView: React.FC = () => {
  const [scenarioGenerated, setScenarioGenerated] = useState(false);

  const benchmarks = [
    {
      metric: 'Customer Retention Rate',
      ourValue: '84.2%',
      median: '91.0%',
      topQuartile: '94.5%',
      bestInClass: '97.0%',
      gap: '-6.8% vs Median',
      tier: 'MEDIAN_LAGGING',
      opportunity: '+$340,000 ARR',
    },
    {
      metric: 'Gross Profit Margin',
      ourValue: '76.5%',
      median: '72.0%',
      topQuartile: '78.0%',
      bestInClass: '82.5%',
      gap: '+4.5% vs Median',
      tier: 'MEDIAN_LEADER',
      opportunity: '+$180,000 ARR',
    },
    {
      metric: 'Delivery Latency Days',
      ourValue: '3.4 days',
      median: '4.1 days',
      topQuartile: '3.0 days',
      bestInClass: '2.2 days',
      gap: '-0.7d vs Median',
      tier: 'MEDIAN_LEADER',
      opportunity: 'Optimal',
    },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', paddingBottom: '40px' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ fontSize: '0.72rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: '#F59E0B', fontWeight: 800 }}>
              Competitive Intelligence & Benchmarking
            </span>
            <span style={{ fontSize: '0.68rem', fontWeight: 800, color: '#10B981', background: 'rgba(16, 185, 129, 0.15)', padding: '2px 6px', borderRadius: '4px' }}>
              Freshness: 98% (3d ago)
            </span>
          </div>
          <h1 style={{ fontSize: '1.8rem', fontWeight: 900, color: '#FFFFFF', margin: '4px 0 0 0' }}>
            Industry Benchmarks & Competitive Positioning
          </h1>
        </div>

        <div style={{ fontSize: '0.8rem', color: '#94A3B8' }}>
          Source: <code>SaaS Capital & Gartner Peer Insights (96% Confidence)</code>
        </div>
      </div>

      {/* Hero Metrics */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px' }}>
        <div style={{ background: '#090D14', border: '1px solid #1E293B', borderRadius: '14px', padding: '20px', display: 'flex', flexDirection: 'column', gap: '6px' }}>
          <div style={{ fontSize: '0.72rem', color: '#64748B', fontWeight: 800, textTransform: 'uppercase' }}>INDUSTRY RANK</div>
          <div style={{ fontSize: '2.2rem', fontWeight: 900, color: '#F59E0B' }}>#4 of 28</div>
          <div style={{ fontSize: '0.75rem', color: '#10B981', fontWeight: 700 }}>85.7th Industry Percentile</div>
        </div>

        <div style={{ background: '#090D14', border: '1px solid #1E293B', borderRadius: '14px', padding: '20px', display: 'flex', flexDirection: 'column', gap: '6px' }}>
          <div style={{ fontSize: '0.72rem', color: '#64748B', fontWeight: 800, textTransform: 'uppercase' }}>DISCOVERED REVENUE OPPORTUNITY</div>
          <div style={{ fontSize: '2.2rem', fontWeight: 900, color: '#38BDF8' }}>+$520,000</div>
          <div style={{ fontSize: '0.75rem', color: '#94A3B8', fontWeight: 700 }}>Across Retention & Margin Gaps</div>
        </div>

        <div style={{ background: '#090D14', border: '1px solid #1E293B', borderRadius: '14px', padding: '20px', display: 'flex', flexDirection: 'column', gap: '6px' }}>
          <div style={{ fontSize: '0.72rem', color: '#64748B', fontWeight: 800, textTransform: 'uppercase' }}>COMPETITIVE TIERS</div>
          <div style={{ fontSize: '2.2rem', fontWeight: 900, color: '#10B981' }}>2 Leader</div>
          <div style={{ fontSize: '0.75rem', color: '#EF4444', fontWeight: 700 }}>1 Median Lagging (Retention)</div>
        </div>

        <div style={{ background: '#090D14', border: '1px solid #1E293B', borderRadius: '14px', padding: '20px', display: 'flex', flexDirection: 'column', gap: '6px' }}>
          <div style={{ fontSize: '0.72rem', color: '#64748B', fontWeight: 800, textTransform: 'uppercase' }}>SWOT SYNTHESIS</div>
          <div style={{ fontSize: '2.2rem', fontWeight: 900, color: '#A855F7' }}>Autonomous</div>
          <div style={{ fontSize: '0.75rem', color: '#A855F7', fontWeight: 700 }}>Continuously Re-Indexed</div>
        </div>
      </div>

      {/* Benchmark Comparisons & Scenario Generator */}
      <div style={{ background: '#090D14', border: '1px solid #1E293B', borderRadius: '14px', padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <span style={{ fontSize: '1rem', fontWeight: 800, color: '#FFFFFF' }}>Competitive Scorecards & Digital Twin Feeder</span>
          <span style={{ fontSize: '0.75rem', color: '#64748B' }}>Benchmark Gap → Scenario Pipeline</span>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {benchmarks.map((item, idx) => (
            <div
              key={idx}
              style={{
                background: 'rgba(15, 23, 42, 0.6)',
                border: '1px solid #1E293B',
                borderRadius: '10px',
                padding: '18px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                flexWrap: 'wrap',
                gap: '14px',
              }}
            >
              <div>
                <div style={{ fontSize: '1rem', fontWeight: 800, color: '#FFFFFF' }}>{item.metric}</div>
                <div style={{ fontSize: '0.78rem', color: '#94A3B8', marginTop: '2px' }}>
                  Our Value: <strong style={{ color: '#FFFFFF' }}>{item.ourValue}</strong> • Median: {item.median} • Top Quartile: {item.topQuartile} • Best in Class: {item.bestInClass}
                </div>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <span
                  style={{
                    fontSize: '0.75rem',
                    fontWeight: 800,
                    padding: '4px 10px',
                    borderRadius: '6px',
                    background: item.tier === 'MEDIAN_LAGGING' ? 'rgba(239, 68, 68, 0.15)' : 'rgba(16, 185, 129, 0.15)',
                    color: item.tier === 'MEDIAN_LAGGING' ? '#EF4444' : '#10B981',
                  }}
                >
                  {item.gap}
                </span>

                {item.opportunity !== 'Optimal' && (
                  <button
                    onClick={() => setScenarioGenerated(true)}
                    style={{
                      padding: '8px 12px',
                      background: 'rgba(56, 189, 248, 0.1)',
                      border: '1px solid rgba(56, 189, 248, 0.3)',
                      borderRadius: '8px',
                      color: '#38BDF8',
                      fontSize: '0.75rem',
                      fontWeight: 700,
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '6px',
                    }}
                  >
                    <Sparkles size={14} />
                    <span>Generate Scenario ({item.opportunity})</span>
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>

        {scenarioGenerated && (
          <div style={{ background: 'rgba(16, 185, 129, 0.08)', border: '1px solid rgba(16, 185, 129, 0.2)', padding: '14px 18px', borderRadius: '8px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <CheckCircle2 size={16} color="#10B981" />
              <span style={{ fontSize: '0.82rem', color: '#F1F5F9' }}>
                Digital Twin Scenario Generated: <strong>"Close Retention Gap to Industry Median" (+$340,000 ARR)</strong>
              </span>
            </div>
            <Link
              to="/scenarios/comparison"
              style={{ color: '#10B981', fontSize: '0.78rem', fontWeight: 800, textDecoration: 'none' }}
            >
              View in Scenario Studio →
            </Link>
          </div>
        )}
      </div>
    </div>
  );
};
