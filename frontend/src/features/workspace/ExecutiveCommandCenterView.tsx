import React, { useState } from 'react';
import { ShieldCheck, TrendingUp, TrendingDown, DollarSign, Activity, AlertTriangle, Cpu, Network, ArrowUpRight, CheckCircle2, ChevronRight, Eye, RefreshCw, Zap, Sparkles } from 'lucide-react';
import { ExecutiveQuickActions } from '../../components/workspace/ExecutiveQuickActions';
import { SavedViewsSelector } from '../../components/workspace/SavedViewsSelector';
import { ExplainabilityDrawer } from '../../components/workspace/ExplainabilityDrawer';
import { useNavigate } from 'react-router-dom';

export const ExecutiveCommandCenterView: React.FC = () => {
  const navigate = useNavigate();
  const [isExplainOpen, setIsExplainOpen] = useState(false);
  const [explainTitle, setExplainTitle] = useState('Portfolio Health Score');
  const [explainValue, setExplainValue] = useState('85.0 / 100 (+11.0 pts)');

  const handleOpenExplain = (title: string, value: string) => {
    setExplainTitle(title);
    setExplainValue(value);
    setIsExplainOpen(true);
  };

  const activityFeed = [
    { title: 'Critical Retention Drift Fired', desc: 'Customer retention dropped to 79.5% (-7.3% vs target) in Southeastern corridors.', time: '12m ago', severity: 'CRITICAL', link: '/monitoring' },
    { title: 'Simulation #12 Completed', desc: 'Monte Carlo confirmed Recovery Path A delivers +$124K ARR (92% confidence).', time: '45m ago', severity: 'SUCCESS', link: '/simulations' },
    { title: 'Executive Decision Ratified', desc: 'Board approved Recovery Path A: Secondary Hub Rebalancing & SLA Penalties.', time: '2h ago', severity: 'SUCCESS', link: '/decision-copilot' },
    { title: 'Forecast Accuracy Recalculated', desc: 'Rolling 3-cycle accuracy increased to 88.4% (+7.15% improvement).', time: '4h ago', severity: 'INFO', link: '/forecasting' },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', paddingBottom: '40px' }}>
      {/* Top Banner & Saved Views Bar */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
            <span style={{ fontSize: '0.72rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: '#38BDF8', fontWeight: 800 }}>
              DecisionOS Executive Intelligence Platform
            </span>
          </div>
          <h1 style={{ fontSize: '1.8rem', fontWeight: 900, color: '#FFFFFF', margin: 0, letterSpacing: '-0.02em' }}>
            Executive Command Center
          </h1>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <SavedViewsSelector />
        </div>
      </div>

      {/* Quick Actions Bar */}
      <ExecutiveQuickActions />

      {/* Hero Metric Cards Grid (4 Columns) */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '16px' }}>
        {/* Portfolio Health Card */}
        <div
          style={{
            background: 'linear-gradient(135deg, rgba(15, 23, 42, 0.8), rgba(9, 13, 20, 0.95))',
            border: '1px solid #1E293B',
            borderRadius: '12px',
            padding: '20px',
            position: 'relative',
            cursor: 'pointer',
          }}
          onClick={() => handleOpenExplain('Portfolio Health Score', '85.0 / 100 (+11.0 pts lift)')}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
            <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#94A3B8', textTransform: 'uppercase' }}>Portfolio Health</span>
            <ShieldCheck size={16} color="#10B981" />
          </div>
          <div style={{ fontSize: '2.2rem', fontWeight: 900, color: '#10B981', lineHeight: 1.1 }}>85.0</div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginTop: '6px', fontSize: '0.8rem', color: '#10B981' }}>
            <TrendingUp size={14} />
            <span>+11.0 pts vs baseline (74.0)</span>
          </div>
          <div style={{ marginTop: '12px', fontSize: '0.72rem', color: '#38BDF8', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '4px' }}>
            <span>Inspect Provenance Lineage</span>
            <ChevronRight size={12} />
          </div>
        </div>

        {/* ARR Recovery Progress Card */}
        <div
          style={{
            background: 'linear-gradient(135deg, rgba(15, 23, 42, 0.8), rgba(9, 13, 20, 0.95))',
            border: '1px solid #1E293B',
            borderRadius: '12px',
            padding: '20px',
            cursor: 'pointer',
          }}
          onClick={() => handleOpenExplain('Verified ARR Recovery', '+$124,000 Realized Recovery')}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
            <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#94A3B8', textTransform: 'uppercase' }}>Realized ARR Recovery</span>
            <DollarSign size={16} color="#38BDF8" />
          </div>
          <div style={{ fontSize: '2.2rem', fontWeight: 900, color: '#38BDF8', lineHeight: 1.1 }}>+$124,000</div>
          <div style={{ fontSize: '0.8rem', color: '#94A3B8', marginTop: '6px' }}>
            Target Completion: <span style={{ color: '#FFFFFF', fontWeight: 700 }}>78%</span> of $160K Goal
          </div>
          <div style={{ marginTop: '12px', fontSize: '0.72rem', color: '#38BDF8', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '4px' }}>
            <span>View Outcome Attribution</span>
            <ChevronRight size={12} />
          </div>
        </div>

        {/* Systemic Risk Summary Card */}
        <div
          style={{
            background: 'linear-gradient(135deg, rgba(15, 23, 42, 0.8), rgba(9, 13, 20, 0.95))',
            border: '1px solid #1E293B',
            borderRadius: '12px',
            padding: '20px',
            cursor: 'pointer',
          }}
          onClick={() => handleOpenExplain('Systemic Risk Index', '14.1 (Low Risk, -10.2 pts reduction)')}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
            <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#94A3B8', textTransform: 'uppercase' }}>Systemic Risk Score</span>
            <AlertTriangle size={16} color="#F59E0B" />
          </div>
          <div style={{ fontSize: '2.2rem', fontWeight: 900, color: '#F59E0B', lineHeight: 1.1 }}>14.1</div>
          <div style={{ fontSize: '0.8rem', color: '#10B981', marginTop: '6px' }}>
            Down from 24.3 (0 Critical, 2 High, 5 Med)
          </div>
          <div style={{ marginTop: '12px', fontSize: '0.72rem', color: '#38BDF8', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '4px' }}>
            <span>Inspect Risk Breakdown</span>
            <ChevronRight size={12} />
          </div>
        </div>

        {/* Forecast Reliability Card */}
        <div
          style={{
            background: 'linear-gradient(135deg, rgba(15, 23, 42, 0.8), rgba(9, 13, 20, 0.95))',
            border: '1px solid #1E293B',
            borderRadius: '12px',
            padding: '20px',
            cursor: 'pointer',
          }}
          onClick={() => handleOpenExplain('Rolling Forecast Reliability', '88.4% 3-Cycle Accuracy')}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
            <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#94A3B8', textTransform: 'uppercase' }}>Forecast Accuracy</span>
            <Activity size={16} color="#A855F7" />
          </div>
          <div style={{ fontSize: '2.2rem', fontWeight: 900, color: '#A855F7', lineHeight: 1.1 }}>88.4%</div>
          <div style={{ fontSize: '0.8rem', color: '#94A3B8', marginTop: '6px' }}>
            Variance Envelope: <span style={{ color: '#FFFFFF', fontWeight: 700 }}>±4.2%</span>
          </div>
          <div style={{ marginTop: '12px', fontSize: '0.72rem', color: '#38BDF8', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '4px' }}>
            <span>Inspect Forecast V3</span>
            <ChevronRight size={12} />
          </div>
        </div>
      </div>

      {/* Main Content: 2-Column Split (Live Command Telemetry + Real-Time Activity Feed) */}
      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '20px' }}>
        {/* Left: Active Strategic Decision Package */}
        <div style={{ background: '#090D14', border: '1px solid #1E293B', borderRadius: '12px', padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div>
              <div style={{ fontSize: '0.72rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: '#38BDF8', fontWeight: 800 }}>
                Active Strategic Direction
              </div>
              <h2 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#FFFFFF', margin: '4px 0 0 0' }}>
                Recovery Path A: Retention First & Courier SLA Fix
              </h2>
            </div>
            <span style={{ background: 'rgba(16, 185, 129, 0.15)', color: '#10B981', padding: '4px 10px', borderRadius: '20px', fontSize: '0.75rem', fontWeight: 800 }}>
              EXECUTING
            </span>
          </div>

          <p style={{ fontSize: '0.88rem', color: '#94A3B8', lineHeight: 1.6, margin: 0 }}>
            Deploying automated regional carrier rebalancing in Southeastern corridors. Resolves Secondary Hub Dispatch Bottlenecks (5.4d latency) and recovers +$124,000 realized ARR across 42 verified live cycles.
          </p>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '12px', background: 'rgba(15, 23, 42, 0.6)', border: '1px solid #1E293B', borderRadius: '8px', padding: '14px' }}>
            <div>
              <div style={{ fontSize: '0.72rem', color: '#64748B', fontWeight: 600 }}>Expected ARR Lift</div>
              <div style={{ fontSize: '1.1rem', fontWeight: 800, color: '#38BDF8', marginTop: '2px' }}>+$124,000</div>
            </div>
            <div>
              <div style={{ fontSize: '0.72rem', color: '#64748B', fontWeight: 600 }}>Health Lift</div>
              <div style={{ fontSize: '1.1rem', fontWeight: 800, color: '#10B981', marginTop: '2px' }}>+11.0 pts</div>
            </div>
            <div>
              <div style={{ fontSize: '0.72rem', color: '#64748B', fontWeight: 600 }}>Decision Confidence</div>
              <div style={{ fontSize: '1.1rem', fontWeight: 800, color: '#A855F7', marginTop: '2px' }}>92.0%</div>
            </div>
          </div>

          <div style={{ display: 'flex', gap: '12px', marginTop: 'auto' }}>
            <button
              onClick={() => navigate('/decision-copilot')}
              style={{
                flex: 1,
                padding: '10px 16px',
                background: '#0284C7',
                border: 'none',
                borderRadius: '6px',
                color: '#FFFFFF',
                fontSize: '0.85rem',
                fontWeight: 700,
                cursor: 'pointer',
              }}
            >
              Open Decision Copilot
            </button>
            <button
              onClick={() => navigate('/knowledge-graph')}
              style={{
                padding: '10px 16px',
                background: 'rgba(30, 41, 59, 0.8)',
                border: '1px solid #334155',
                borderRadius: '6px',
                color: '#F1F5F9',
                fontSize: '0.85rem',
                fontWeight: 700,
                cursor: 'pointer',
              }}
            >
              Explore Graph
            </button>
          </div>
        </div>

        {/* Right: Live Activity Stream */}
        <div style={{ background: '#090D14', border: '1px solid #1E293B', borderRadius: '12px', padding: '20px', display: 'flex', flexDirection: 'column', gap: '14px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ fontSize: '0.88rem', fontWeight: 800, color: '#FFFFFF', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <Zap size={15} color="#38BDF8" />
              <span>Real-Time Activity Feed</span>
            </div>
            <span style={{ fontSize: '0.7rem', color: '#10B981', fontWeight: 700 }}>● Live Stream</span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', maxHeight: '360px', overflowY: 'auto' }}>
            {activityFeed.map((ev, idx) => (
              <div
                key={idx}
                onClick={() => navigate(ev.link)}
                style={{
                  padding: '10px 12px',
                  borderRadius: '8px',
                  background: 'rgba(15, 23, 42, 0.6)',
                  border: '1px solid #1E293B',
                  cursor: 'pointer',
                  transition: 'all 0.15s ease',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '2px' }}>
                  <span style={{ fontSize: '0.68rem', fontWeight: 800, color: ev.severity === 'CRITICAL' ? '#EF4444' : ev.severity === 'SUCCESS' ? '#10B981' : '#38BDF8' }}>
                    {ev.severity}
                  </span>
                  <span style={{ fontSize: '0.68rem', color: '#64748B' }}>{ev.time}</span>
                </div>
                <div style={{ fontSize: '0.82rem', fontWeight: 700, color: '#FFFFFF' }}>{ev.title}</div>
                <div style={{ fontSize: '0.74rem', color: '#94A3B8', marginTop: '2px', lineHeight: 1.3 }}>{ev.desc}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Reusable In-Place Explainability Drawer */}
      <ExplainabilityDrawer
        isOpen={isExplainOpen}
        onClose={() => setIsExplainOpen(false)}
        title={explainTitle}
        metricValue={explainValue}
      />
    </div>
  );
};
